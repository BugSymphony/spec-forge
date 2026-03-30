from typing import Optional
import yaml
from pathlib import Path

from .base_agent import BaseAgent
from ..config.constants import ContentType, Stage


class SpecAgent(BaseAgent):
    """
    Spec 阶段：生成规格
    """

    def generate(self, user_input: str, content_type: str = ContentType.DEFAULT) -> Optional[str]:
        context = {
            "user_input": user_input
        }

        return self.run_stage(
            stage=Stage.SPEC,
            content_type=content_type,
            context=context
        )

    def clarify(self, user_input: str, content_type: str = ContentType.DEFAULT, max_questions: int = 8) -> Optional[
        str]:
        """
        检测需要澄清的问题（暂时基于配置文件）
        
        Args:
            user_input: 用户想法
            content_type: 内容类型
            max_questions: 最大问题数（默认 8 个）
        
        Returns:
            需要澄清的问题列表
        """
        questions = []

        # 1. 加载配置文件
        config_path = Path(__file__).parent.parent / 'config' / 'clarify_config.yaml'
        if not config_path.exists():
            # 配置文件不存在时使用默认规则
            return self._clarify_default(user_input, content_type, max_questions)

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 2. 获取对应内容类型的规则
        clarify_rules = config.get('clarify_rules', {})
        content_rules = clarify_rules.get(content_type, {})

        if not content_rules:
            return questions

        # 3. 应用规则生成问题
        rules = content_rules.get('rules', [])
        for rule in rules:
            keywords = rule.get('keywords', [])
            question = rule.get('question', '')
            priority = rule.get('priority', 999)

            # 检查是否包含任何关键词
            if not any \
                        (k in user_input for k in keywords):
                questions.append({
                    'question': question,
                    'priority': priority
                })

        # 4. 按优先级排序
        questions.sort(key=lambda x: x['priority'])

        # 5. 限制问题数量
        questions = questions[:max_questions]

        # 6. 只返回问题文本
        return [q['question'] for q in questions]
