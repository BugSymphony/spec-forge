import yaml
import re
from typing import Tuple, Any, Optional

from forge.utils.logging import logger
from forge.llm.types import Message


class YAMLFixAgent:
    """
    YAML 自动修复 Agent

    作用：
    1. 修复 LLM 输出的不合法 YAML
    2. 尽可能不依赖 LLM
    3. 最后用 LLM 兜底
    """

    def __init__(self, llm=None):
        self.llm = llm

    def fix(self, content: str) -> Tuple[Optional[Any], str]:
        """
        修复 YAML

        Returns: 解析后的数据, 修复后的字符串
        """

        # 1. 直接尝试解析
        data = self._try_parse(content)
        if data:
            return data, content

        # 2. 规则修复
        fixed = self._rule_based_fix(content)
        data = self._try_parse(fixed)
        if data:
            return data, fixed

        # 3. LLM 修复
        logger.debug("LLM 尝试修复")
        if self.llm:
            fixed = self._llm_fix(content)
            logger.debug(f"LLM 尝试修复结果: {fixed}")
            data = self._try_parse(fixed)
            if data:
                return data, fixed

        return None, content

    def _try_parse(self, content: str):
        """
        尝试解析 YAML
        """
        try:
            return yaml.safe_load(content)
        except Exception:
            return None

    def _rule_based_fix(self, content: str) -> str:
        """
        规则修复
        """
        content = self._fix_unclosed_quotes(content)
        content = self._fix_multiline_fields(content)
        content = self._fix_indentation(content)
        return content

    def _fix_unclosed_quotes(self, content: str) -> str:
        """
        修复未闭合引号
        """
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            if line.count('"') % 2 != 0:
                # 不成对 → 去掉所有 "
                line = line.replace('"', '')
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _fix_multiline_fields(self, content: str) -> str:
        """
        强制 summary 等字段为 |
        """
        pattern = re.compile(r'(summary|background|description):\s*(.*)')

        def replacer(match):
            key = match.group(1)
            value = match.group(2).strip()

            # 如果已经是 block，跳过
            if value.startswith("|"):
                return match.group(0)

            return f"{key}: |\n  {value}"

        return pattern.sub(replacer, content)

    def _fix_indentation(self, content: str) -> str:
        """
        修复缩进
        """
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # 去掉奇怪的 tab
            line = line.replace("\t", "  ")
            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def _llm_fix(self, content: str) -> str:
        """
        LLM 尝试修复
        """

        prompt = f"""
你是 YAML 修复专家。

请修复下面的 YAML，使其：
1. 语法完全正确
2. 所有字符串闭合
3. 长文本使用 | 块格式
4. 不改变原始语义

你的输出必须为合法的 YAML 格式。

不要包含任何解释、说明或额外文本。
只输出 YAML 内容。

禁止使用 Markdown 代码块（如 ```yaml）。
不要添加任何额外格式。

确保输出可以被 yaml.safe_load() 直接解析。

---
{content}
---
"""

        try:
            resp = self.llm.chat([Message(role="user", content=prompt)])
            return resp.content
        except Exception as e:
            raise Exception(f"LLM 尝试修复失败:{e}")
