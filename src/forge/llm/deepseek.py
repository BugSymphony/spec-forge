"""
DeepSeek Client（OpenAI兼容）
"""

import os
from typing import List, Optional
from openai import OpenAI

from .base import BaseLLM
from .types import Message, Tool, LLMResponse
from ..exceptions import LLMError


class DeepSeekClient(BaseLLM):
    """
    DeepSeek Client
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API 密钥，默认从环境变量 DEEPSEEK_API_KEY 读取
            **kwargs: 其他配置参数
                - model: 模型名称，默认 "deepseek-chat"
        """

        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")

        super().__init__(api_key, **kwargs)

        # 设置默认配置
        self.model = kwargs.get("model", "deepseek-chat")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 8192)
        self.base_url = kwargs.get("base_url", "https://api.deepseek.com/v1")

        if not self.api_key:
            raise ValueError(
                "DeepSeek API key 未设置。\n"
                "请设置环境变量：export DEEPSEEK_API_KEY='your-key'\n"
                "或在初始化时传入：DeepSeekClient(api_key='your-key')"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def chat(
            self,
            messages: List[Message],
            tools: Optional[List[Tool]] = None,
            **kwargs
    ) -> LLMResponse:
        """
        调用 DeepSeek API 生成内容

        Args:
            messages: 输入提示词
            tools: 工具列表
            **kwargs: 覆盖默认生成参数

        Returns:
            生成的文本内容
        """

        params = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
        }

        if tools:
            params["tools"] = [t.to_openai() for t in tools]

        try:
            response = self.client.chat.completions.create(**params)
        except ImportError:
            raise ImportError(
                "openai 库未安装。\n"
                "请运行：pip install openai"
            )
        except Exception as e:
            # 错误处理
            error_msg = f"DeepSeek API 调用失败：{str(e)}"
            raise LLMError(error_msg)

        message = response.choices[0].message

        if hasattr(message, "tool_calls") and message.tool_calls:
            return LLMResponse(tool_calls=[
                {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
                for tc in message.tool_calls
            ])

        return LLMResponse(content=message.content)

    def validate_config(self) -> bool:
        return self.api_key is not None
