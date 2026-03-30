"""
OpenAI LLM 客户端实现
"""

import os
from typing import List, Optional
from openai import OpenAI

from .base import BaseLLM
from .types import Message, Tool, LLMResponse
from ..exceptions import LLMError


class OpenAIClient(BaseLLM):
    """OpenAI API 客户端"""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        初始化 OpenAI 客户端

        Args:
            api_key: OpenAI API 密钥，默认从环境变量 OPENAI_API_KEY 读取
            **kwargs: 其他配置参数
                - model: 模型名称，默认 "gpt-4"
                - temperature: 温度参数，默认 0.7
                - max_tokens: 最大输出 token 数，默认 10000
        """

        # 尝试从环境变量获取 API key
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        super().__init__(api_key, **kwargs)

        # 设置默认配置
        self.model = kwargs.get("model", "gpt-4o-mini")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 8192)

        if not self.api_key:
            raise ValueError(
                "OpenAI API key 未设置。\n"
                "请设置环境变量：export OPENAI_API_KEY='your-key'\n"
                "或在初始化时传入：输入提示词OpenAIClient(api_key='your-key')"
            )

        self.client = OpenAI(api_key=self.api_key)

    def chat(
            self,
            messages: List[Message],
            tools: Optional[List[Tool]] = None,
            **kwargs
    ) -> LLMResponse:

        openai_messages = [m.to_dict() for m in messages]

        params = {
            "model": kwargs.get("model", self.model),
            "messages": openai_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
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
            error_msg = f"OpenAI API 调用失败：{str(e)}"
            raise LLMError(error_msg)

        message = response.choices[0].message

        # Tool Calls
        if hasattr(message, "tool_calls") and message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append({
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                })
            return LLMResponse(tool_calls=tool_calls)

        return LLMResponse(content=message.content)

    def validate_config(self) -> bool:
        return self.api_key is not None
