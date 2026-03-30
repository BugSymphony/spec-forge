"""
LLM 通用类型定义
"""

from typing import List, Dict, Any, Optional


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content
        }


class Tool:
    def __init__(
            self,
            name: str,
            description: str,
            parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_openai(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class LLMResponse:
    def __init__(
            self,
            content: Optional[str] = None,
            tool_calls: Optional[List[Dict[str, Any]]] = None
    ):
        self.content = content
        self.tool_calls = tool_calls or []

    def has_tool_call(self) -> bool:
        return len(self.tool_calls) > 0
