from typing import Optional

import yaml

from .base_agent import BaseAgent
from ..config.constants import Stage, ContentType
from ..utils.logging import logger


class TasksAgent(BaseAgent):
    """
    Tasks 阶段：任务拆解
    """

    def generate(self, content_type: str = ContentType.DEFAULT) -> Optional[str]:
        return self.run_stage(
            stage=Stage.TASKS,
            content_type=content_type,
            context={}
        )

    def save(self, stage, output, data):
        super().save(stage, output, data)
        # 保存原始 YAML 数据到 tasks_data.yaml
        tasks_data_path = self.specs_manager.get_tasks_data_path(must_exist=False)
        if tasks_data_path:
            with open(tasks_data_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            logger.success(f"Tasks 数据已保存：{tasks_data_path}")
