"""
YamlFormatProvider
用于生成 YAML 输出约束 Prompt
"""

from typing import Optional
from .format_provider import FormatProvider


class YamlFormatProvider(FormatProvider):
    def __init__(
            self,
            schema: Optional[str] = None,
            language: str = "en",  # en / zh
            strict: bool = True
    ):
        """
        Args:
            schema: YAML Schema 内容
            language: 语言（en / zh）
            strict: 是否严格模式
        """
        self.schema = schema or ""
        self.language = language
        self.strict = strict

    def get_format(self) -> str:
        if self.language == "zh":
            return self._get_zh_format()
        return self._get_en_format()

    # =========================
    # English
    # =========================
    def _get_en_format(self) -> str:
        base = """
Your response must be in valid YAML format.

Do not include any explanations, comments, or additional text.
Only output YAML content.

Do NOT include markdown code blocks (no ```yaml).
Do NOT wrap the output in any formatting.

Ensure the YAML can be parsed by yaml.safe_load() without errors.
"""

        strict_part = """
You MUST:
- Follow the schema structure exactly
- Include all required fields
- Use correct data types

Do NOT:
- Add extra fields not defined in the schema
- Omit required fields
""" if self.strict else ""

        schema_part = f"""
Here is the YAML Schema your output must adhere to:

{self.schema}
""" if self.schema else ""

        return base + strict_part + schema_part

    # =========================
    # 中文
    # =========================
    def _get_zh_format(self) -> str:
        base = """
你的输出必须为合法的 YAML 格式。

不要包含任何解释、说明或额外文本。
只输出 YAML 内容。

禁止使用 Markdown 代码块（如 ```yaml）。
不要添加任何额外格式。

确保输出可以被 yaml.safe_load() 直接解析。
"""

        strict_part = """
你必须：
- 严格遵循 Schema 结构
- 包含所有必填字段
- 使用正确的数据类型

禁止：
- 添加 Schema 未定义字段
- 缺少必填字段
""" if self.strict else ""

        schema_part = f"""
以下是必须遵循的 YAML Schema：
\"""yaml
{self.schema}
\"""
""" if self.schema else ""

        return base + strict_part + schema_part
