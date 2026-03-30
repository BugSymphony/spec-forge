"""
模板加载器
统一组合 ProjectConfig 和 ResourceTemplateConfig 获取模板文件
"""
from pathlib import Path
from typing import Optional, Dict, Any
from .project_config import ProjectConfig
from .resource_template_config import ResourceTemplateConfig


class TemplateLoader:
    """模板加载器 - 统一的模板获取接口"""

    def __init__(self, project_config: Optional[ProjectConfig] = None,
                 resource_config: Optional[ResourceTemplateConfig] = None):
        """
        初始化模板加载器
        
        Args:
            project_config: ProjectConfig 实例（可选，默认创建新的）
            resource_config: ResourceTemplateConfig 实例（可选，默认创建新的）
        """
        self.project_config = project_config or ProjectConfig()
        self.resource_config = resource_config or ResourceTemplateConfig()

    @classmethod
    def create(cls) -> 'TemplateLoader':
        """
        创建默认的 TemplateLoader 实例
        
        Returns:
            TemplateLoader 实例
        """
        return cls()

    def get_prompt(self, stage_name: str, content_type: str) -> Optional[str]:
        """
        获取 Prompt 模板内容（带优先级回退）
        
        优先级：
        1. .forge/config.yaml 配置的自定义 Prompt
        2. templates/agent-prompts/{stage}/{content_type}.md
        3. templates/agent-prompts/{stage}/{stage}.md
        
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
            content_type: 内容类型
            
        Returns:
            Prompt 模板内容字符串，如果都不存在则返回 None
        """
        # 第一优先级：从 .forge/config.yaml 加载
        prompt_path = self.project_config.get_prompt_path(stage_name)
        if prompt_path and prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')

        # 第二优先级：内容类型专用模板
        content_type_template = self.resource_config.get_prompt_template(stage_name, content_type)
        if content_type_template and content_type_template.exists():
            return content_type_template.read_text(encoding='utf-8')

        # 第三优先级：通用模板
        generic_template = self.resource_config.get_prompt_template(stage_name, content_type)
        if generic_template and generic_template.exists():
            return generic_template.read_text(encoding='utf-8')

        return None

    def get_output_template(self, stage_name: str, content_type: str) -> Optional[Path]:
        """
        获取 Output 模板路径（带优先级回退）
        
        优先级：
        1. .forge/config.yaml 配置的 Output 模板
        2. templates/output-docs/{stage}/template.md
        3. templates/output-docs/{stage}/{content_type}/template.md
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型
            
        Returns:
            Output 模板文件路径，如果都不存在则返回 None
        """
        # 第一优先级：从 .forge/config.yaml 加载
        output_path = self.project_config.get_output_path(stage_name)
        if output_path and output_path.exists():
            return output_path

        # 第二优先级：通用模板
        generic_output = self.resource_config.get_output_template(stage_name, content_type)
        if generic_output and generic_output.exists():
            return generic_output

        # 第三优先级：内容类型专用模板
        content_type_output = Path(f"templates/output-docs/{stage_name}/{content_type}/template.md")
        if content_type_output.exists():
            return content_type_output

        return None

    def get_schema(self, stage_name: str, content_type: str) -> Optional[str]:
        """
        获取 Schema YAML 内容（带优先级回退）
        
        优先级：
        1. .forge/config.yaml 配置的 Schema
        2. templates/output-docs/{stage}/{content_type}/schema.yaml
        3. templates/output-docs/{stage}/schema.yaml
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型
            
        Returns:
            Schema YAML 内容字符串，如果都不存在则返回 None
        """
        # 第一优先级：从 .forge/config.yaml 加载
        schema_path = self.project_config.get_schema_path(stage_name)
        if schema_path and schema_path.exists():
            return schema_path.read_text(encoding='utf-8')

        # 第二优先级：内容类型专用 Schema
        content_type_schema = Path(f"templates/output-docs/{stage_name}/{content_type}/schema.yaml")
        if content_type_schema.exists():
            return content_type_schema.read_text(encoding='utf-8')

        # 第三优先级：通用 Schema
        generic_schema = self.resource_config.get_schema_template(stage_name, content_type)
        if generic_schema and generic_schema.exists():
            return generic_schema.read_text(encoding='utf-8')

        return None

    def get_template_info(self, stage_name: str, content_type: str) -> Dict[str, Any]:
        """
        获取指定阶段的所有模板信息
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型
            
        Returns:
            包含所有模板路径和内容的字典
        """
        return {
            'prompt': {
                'path': self.project_config.get_prompt_path(stage_name) or
                        self.resource_config.get_prompt_template(stage_name, content_type),
                'content': self.get_prompt(stage_name, content_type)
            },
            'output': {
                'path': self.get_output_template(stage_name, content_type),
            },
            'schema': {
                'path': self.project_config.get_schema_path(stage_name) or
                        Path(f"templates/output-docs/{stage_name}/{content_type}/schema.yaml"),
                'content': self.get_schema(stage_name, content_type)
            }
        }
