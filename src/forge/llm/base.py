"""
LLM 抽象基类
所有 LLM 客户端必须实现此接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .types import Message, Tool, LLMResponse


class BaseLLM(ABC):
    """LLM 抽象基类"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
       初始化 LLM 客户端

       Args:
           api_key: API 密钥
           **kwargs: 其他配置参数
       """

        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def chat(
            self,
            messages: List[Message],
            tools: Optional[List[Tool]] = None,
            **kwargs
    ) -> LLMResponse:
        """
        聊天接口

        Args:
            messages: 聊天消息列表
            tools: 工具列表
            **kwargs: 其他配置参数

        Returns:
            LLM 响应内容
        """

        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置是否完整

        Returns:
            True 如果配置有效
        """

        pass
