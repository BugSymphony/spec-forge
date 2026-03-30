"""
项目配置管理器
统一管理 .forge 目录下的配置文件
"""
import yaml
from pathlib import Path
from typing import Dict, Optional, Any


class ProjectConfig:
    """项目配置管理器"""

    def __init__(self, forge_dir: Path = Path(".forge")):
        """
        初始化配置管理器
        
        Args:
            forge_dir: .forge 目录路径
        """
        self.forge_dir = forge_dir
        self.config_file = forge_dir / "config.yaml"
        self._config: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self._config is not None:
            return self._config

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = {}

        return self._config or {}

    def get_content_type(self) -> str:
        """获取内容类型"""
        config = self.load()
        return config.get('content_type', 'novel')
    
    def get_llm_provider(self) -> str:
        """获取 LLM 提供商"""
        config = self.load()
        return config.get('llm_provider', 'deepseek')
    
    def is_schema_validation_enabled(self) -> bool:
        """检查是否启用 Schema 校验"""
        config = self.load()
        return config.get('schema_validation', True)

    def get_stage_config(self, stage_name: str) -> Dict[str, Path]:
        """
        获取指定阶段的完整配置
            
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
                
        Returns:
            包含 prompt、output、schema 路径的字典
        """
        config = self.load()
        paths = {}

        if 'stages' in config and stage_name in config['stages']:
            stage_config = config['stages'][stage_name]

            if 'prompt' in stage_config:
                prompt_path = Path(stage_config['prompt'])
                # 判断是否为绝对路径
                if prompt_path.is_absolute():
                    paths['prompt'] = prompt_path
                else:
                    paths['prompt'] = self.forge_dir / stage_config['prompt']

            if 'output' in stage_config:
                output_path = Path(stage_config['output'])
                # 判断是否为绝对路径
                if output_path.is_absolute():
                    paths['output'] = output_path
                else:
                    paths['output'] = self.forge_dir / stage_config['output']

            if 'schema' in stage_config:
                schema_path = Path(stage_config['schema'])
                # 判断是否为绝对路径
                if schema_path.is_absolute():
                    paths['schema'] = schema_path
                else:
                    paths['schema'] = self.forge_dir / stage_config['schema']

        return paths

    def get_stage_file(self, stage_name: str, file_type: str) -> Optional[Path]:
        """
        获取指定阶段的特定文件路径（统一查询方法）
            
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
            file_type: 文件类型（prompt/output/schema）
                
        Returns:
            文件路径（如果存在），否则 None
        """
        stage_config = self.get_stage_config(stage_name)
        return stage_config.get(file_type)

    def get_prompt_path(self, stage_name: str) -> Optional[Path]:
        """
        获取指定阶段的 Prompt 文件路径
            
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
                
        Returns:
            Prompt 文件路径
        """
        return self.get_stage_file(stage_name, 'prompt')

    def get_output_path(self, stage_name: str) -> Optional[Path]:
        """
        获取指定阶段的 Output 文件路径
            
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
                
        Returns:
            Output 文件路径
        """
        return self.get_stage_file(stage_name, 'output')

    def get_schema_path(self, stage_name: str) -> Optional[Path]:
        """
        获取指定阶段的 Schema 文件路径
            
        Args:
            stage_name: 阶段名称（specify/plan/tasks）
                
        Returns:
            Schema 文件路径
        """
        return self.get_stage_file(stage_name, 'schema')

    def is_initialized(self) -> bool:
        """检查项目是否已初始化"""
        return self.config_file.exists()
