"""
FormatProvider
用于生成 LLM 输出格式约束 Prompt
"""

from abc import ABC, abstractmethod


class FormatProvider(ABC):
    """
    输出格式提供器接口
    """

    @abstractmethod
    def get_format(self) -> str:
        """
        获取格式约束 Prompt

        Returns:
            格式约束字符串（用于拼接到 Prompt 中）
        """
        pass
