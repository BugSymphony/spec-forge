"""
SpecForge 自定义异常
"""


class SpecForgeError(Exception):
    """基础异常类"""
    pass


class ConfigError(SpecForgeError):
    """配置加载失败"""
    pass


class LLMError(SpecForgeError):
    """LLM 错误"""
    pass


class SchemaError(SpecForgeError):
    """Schema 相关错误"""
    pass


class YAMLParseError(SpecForgeError):
    """YAML 解析失败"""

    def __init__(self, message: str, yaml_content: str = None):
        self.yaml_content = yaml_content
        super().__init__(message)


class RenderError(SpecForgeError):
    """模板渲染失败"""
    pass
