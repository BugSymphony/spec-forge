from pathlib import Path
from typing import Optional

from forge.config.constants import STAGE_NAMES


class ResourceTemplateConfig:
    """
    资源模板配置管理器
    """

    def __init__(self):
        """初始化资源模板配置"""
        # 获取 forge 包的实际路径
        import forge
        forge_path = Path(forge.__file__).parent
        self.templates_dir = forge_path.parent.parent / 'templates'

    def get_stage_template(self, stage_name: str, file_type: str, content_type: str) -> Optional[Path]:
        """
        获取指定阶段的特定类型模板路径（统一查询方法，包含 content_type）
        
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
            file_type: 文件类型（prompt/output/schema）
            content_type: 内容类型（novel/article/comic/video）
            
        Returns:
            模板文件路径（如果存在），否则 None
        """
        if not stage_name in STAGE_NAMES:
            raise ValueError(f"无效的阶段名称：{stage_name}")

        # Prompt 模板
        if file_type == 'prompt':
            specific_path = self.templates_dir / "agent-prompts" / stage_name / f"{content_type}.md"
            default_path = self.templates_dir / "agent-prompts" / stage_name / "prompt.md"
            return specific_path if specific_path.exists() else default_path

        # Output 模板
        elif file_type == 'output':
            specific_path = self.templates_dir / "output-docs" / stage_name / content_type / "template.md"
            default_path = self.templates_dir / "output-docs" / stage_name / "template.md"
            return specific_path if specific_path.exists() else default_path

        # Schema 模板
        elif file_type == 'schema':
            specific_path = self.templates_dir / "output-docs" / stage_name / content_type / "schema.yaml"
            default_path = self.templates_dir / "output-docs" / stage_name / "schema.yaml"
            return specific_path if specific_path.exists() else default_path

        return None

    def get_prompt_template(self, stage_name: str, content_type: str) -> Optional[Path]:
        """
        获取指定阶段的 Prompt 模板路径
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型
            
        Returns:
            Prompt 模板路径
        """
        return self.get_stage_template(stage_name, 'prompt', content_type)

    def get_output_template(self, stage_name: str, content_type: Optional[str] = None) -> Optional[Path]:
        """
        获取指定阶段的 Output 模板路径
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型，为 None 时使用通用模板
            
        Returns:
            Output 模板路径
        """
        if content_type:
            return self.templates_dir / "output-docs" / stage_name / content_type / "template.md"
        else:
            # 通用模板（不带 content_type）
            return self.templates_dir / "output-docs" / stage_name / "template.md"

    def get_schema_template(self, stage_name: str, content_type: Optional[str] = None) -> Optional[Path]:
        """
        获取指定阶段的 Schema 模板路径
        
        Args:
            stage_name: 阶段名称
            content_type: 内容类型，为 None 时使用通用 schema
            
        Returns:
            Schema 模板路径
        """
        if content_type:
            return self.templates_dir / "output-docs" / stage_name / content_type / "schema.yaml"
        else:
            # 通用 schema（不带 content_type）
            return self.templates_dir / "output-docs" / stage_name / "schema.yaml"
