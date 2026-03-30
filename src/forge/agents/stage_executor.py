"""
StageExecutor
负责执行一个完整阶段的生成流程

流程：
prompt -> llm -> yaml -> render
"""

from typing import Dict, Any

from forge import YAMLParseError
from forge.agents.yaml_fix_agent import YAMLFixAgent
from forge.utils.logging import logger


class StageExecutor:
    def __init__(self, agent):
        self.agent = agent
        self.fix_agent = YAMLFixAgent(llm=self.agent.getLLM())

    def execute(
            self,
            stage: str,
            content_type: str,
            context: Dict[str, Any]
    ) -> str:
        # 1. 构建 Prompt
        prompt = self.agent.build_prompt(stage, content_type, context)
        # logger.debug(prompt)

        # 2. 调用 LLM
        response = self.agent.call_llm(prompt)
        # logger.debug(response)

        # 3. 解析 YAML
        try:
            data = self.agent.parse_yaml(response)
        except Exception as e:
            logger.warning(f"YAML 解析失败:{e}")
            logger.step("正在尝试 YAML 修复...")
            # 修复
            data, fixed_content = self.fix_agent.fix(response)

            if not data:
                raise Exception(f"YAML 修复失败:{e}")

        # 4. schema 验证
        is_valid, errors = self.agent.schema_validate(stage, content_type, data)
        if not is_valid:
            raise YAMLParseError(f"YAML 验证失败: {errors}")

        # 5. 渲染输出
        template_path = self.agent.get_output_template(stage, content_type)
        output = self.agent.render(template_path, data)

        # 6. 持久化
        self.agent.save(stage, output, data)

        return output
