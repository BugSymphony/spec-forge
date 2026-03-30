from typing import Optional

from .base_agent import BaseAgent
from ..config.constants import Stage, ContentType


class PlanAgent(BaseAgent):
    """
    Plan 阶段：生成执行计划
    """

    def generate(self, user_input: str = "", content_type: str = ContentType.DEFAULT) -> Optional[str]:
        context = {
            "user_input": user_input
        }

        return self.run_stage(
            stage=Stage.PLAN,
            content_type=content_type,
            context=context
        )
