"""
Agent 基类
统一 Agent 核心能力（Prompt / LLM / YAML / Render）
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import yaml
import re

from forge.config.constants import STAGE_DEPENDENCIES
from ..formats.yaml_format_provider import YamlFormatProvider
from ..config.project_config import ProjectConfig
from ..config.template_loader import TemplateLoader
from ..config.resource_template_config import ResourceTemplateConfig
from ..config.specs_manager import SpecsManager
from ..exceptions import LLMError, YAMLParseError

from .stage_executor import StageExecutor
from ..llm.base import BaseLLM
from ..llm.types import Message
from forge.utils.schema import SchemaParser
from ..utils.logging import logger
from ..utils.template_renderer import TemplateRenderer


class BaseAgent(ABC):
    """
    Agent 基类
    定义所有 Agent 的通用接口和实现
    """

    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm
        self.config = ProjectConfig()

        self.template_loader = TemplateLoader(
            project_config=self.config,
            resource_config=ResourceTemplateConfig()
        )

        self.specs_manager = SpecsManager()

    # =========================
    # 抽象方法
    # =========================

    @abstractmethod
    def generate(self, **kwargs) -> Optional[str]:
        pass

    def run_stage(
            self,
            stage: str,
            content_type: str,
            context: Dict[str, Any]
    ) -> str:
        """
        Stage 执行入口

        Args:
            stage: 阶段名称
            content_type: 内容类型
            context: 上下文

        """
        executor = StageExecutor(self)
        return executor.execute(stage, content_type, context)

    def getLLM(self):
        """
        获取 LLM
        """
        return self.llm

    # =========================
    # Prompt 构建方法
    # =========================

    def build_prompt(
            self,
            stage: str,
            content_type: str,
            context: Dict[str, Any]
    ) -> str:
        """
        Prompt 构建

        Args:
            stage: 阶段名称
            content_type: 内容类型
            context: 上下文
        """
        # 1. 加载业务 Prompt
        template = self.template_loader.get_prompt(stage, content_type)

        # 2. 渲染变量
        template = self.render_template_vars(template, context)

        # 3. 阶段上下文
        context_block = self.build_stage_context(stage)

        # 4. 输出格式
        format_block = self.build_output_format(stage, content_type)

        # 5. 构建系统提示
        system_rules = self.build_system_rules()

        return f"""
{template}

# Context
\"""md
{context_block}
\"""

{format_block}

# Global Constraints
{system_rules}
"""

    def get_system_prompt(self) -> str:
        """
        获取 Constitution，自动注入 Constitution 到 system
        """
        return self.specs_manager.get_constitution_content()

    # =========================
    # LLM 调用方法
    # =========================

    def call_llm(self, user_prompt: str) -> str:
        """
        调用 LLM
        """
        if not self.llm:
            raise LLMError("LLM 未初始化")

        messages = []

        system_prompt = self.get_system_prompt()
        if system_prompt:
            messages.append(Message("system", system_prompt))

        messages.append(Message("user", user_prompt))

        response = self.llm.chat(messages)

        return response.content

    # =========================
    # YAML 处理方法
    # =========================

    def parse_yaml(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 响应内容，返回 YAML 内容
        """
        match = re.search(r"```(?:yaml)?\s*(.*?)```", response, re.S)
        content = match.group(1) if match else response

        try:
            return yaml.safe_load(content)
        except Exception as e:
            raise YAMLParseError(f"[ERROR] YAML 解析失败：{e}\n{content}")

    def schema_validate(self, stage, content_type, data):
        """
        YAML 验证
        """
        # 检查是否启用了 Schema 校验
        if not self.config.is_schema_validation_enabled():
            logger.info(f"⚠️  Schema 校验已禁用，跳过 {stage} 阶段验证")
            return True, []
        
        logger.info(f"🔍 开始 {stage} 阶段 Schema 校验...")

        # 1. 获取 schema parser
        parser = SchemaParser()
        parser.load(self.config.get_schema_path(stage))

        # 2. 执行校验
        is_valid, errors = parser.validate_structure(data)

        # 3. 分离 warning
        real_errors = []
        warnings = []

        for err in errors:
            if err.startswith("警告"):
                warnings.append(err)
            else:
                real_errors.append(err)

        # 4. 输出日志
        if warnings:
            for w in warnings:
                print(f"  - {w}")

        if real_errors:
            for e in real_errors:
                print(f"  - {e}")

        # 5. 返回结果
        return len(real_errors) == 0, real_errors

    # =========================
    # 模板渲染方法
    # =========================

    def get_output_template(self, stage: str, content_type: str) -> Path:
        """
        获取输出模板路径
        """
        return self.template_loader.get_output_template(stage, content_type)

    def render(self, template_path: Path, data: Dict[str, Any]) -> str:
        """
        渲染
        """
        return TemplateRenderer.render_from_path(template_path, data)

    def render_template_vars(self, template: str, context: Dict[str, Any]) -> str:
        """
        渲染模板变量
        """
        return TemplateRenderer.render_string(template, context)

    # =========================
    # 上下文构建方法
    # =========================

    def build_stage_context(self, stage: str) -> str:
        """
        构建阶段依赖上下文（从 specs 文件系统读取）
        """
        deps = STAGE_DEPENDENCIES.get(stage, [])

        parts = []

        for dep in deps:
            content = self.specs_manager.get_document_content(dep)
            if not content:
                continue

            parts.append(f"## {dep.upper()}\n{content}")
            logger.info(f"[dim]加载 {dep} 文档[/dim]")

        return "\n\n".join(parts)

    def build_output_format(self, stage: str, content_type: str) -> str:
        """
        Format 注入
        """
        schema = self.template_loader.get_schema(stage, content_type)
        if not schema or not schema.strip():
            return ""

        provider = YamlFormatProvider(schema=schema)
        format_prompt = provider.get_format()

        return f"""# Output Format
{format_prompt}   
"""

    def build_system_rules(self):
        pass

    # =========================
    # 文件保存方法
    # =========================

    def save(self, stage, output, data):
        output_path = self.specs_manager.get_stage_document(stage, must_exist=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)

        logger.success(f"✅ {stage} 已生成")
        logger.info(f"📄 文件：{output_path.absolute()}")
