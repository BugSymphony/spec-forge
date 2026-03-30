"""
/specify 命令处理
生成结构化 Spec 文档
"""
import click
from typing import Optional
from ..agents.spec_agent import SpecAgent

from ..exceptions import YAMLParseError, RenderError
from forge.llm.factory import init_llm
from ..utils.logging import logger


def handle_specify(
        content_type: str,
        idea: Optional[str] = None,
        no_prompt: bool = False,
        llm_provider: str = None
):
    logger.info(f"\n[bold blue]✨ SpecForge - Spec 生成器[/bold blue]\n")

    # 1. 获取用户输入
    if not idea and not no_prompt:
        idea = _interactive_input(content_type)

    if not idea:
        logger.error("错误：未提供创意想法")
        return

    # 2. 初始化 SpecAgent
    llm = init_llm(provider=llm_provider)
    agent = SpecAgent(llm=llm)

    # 3. 澄清
    if not no_prompt:
        questions = agent.clarify(user_input=idea, content_type=content_type)

        if questions:
            idea = _handle_clarification(idea, questions)

    logger.info(f"\n💡 Idea:\n{idea}")

    # 4. 生成 Spec
    try:
        spec_content = agent.generate(
            user_input=idea,
            content_type=content_type
        )

        if not spec_content:
            logger.error("错误：Spec 生成失败")
            return

    except YAMLParseError as e:
        logger.error(f"YAML 解析失败：{e}")
        return
    except RenderError as e:
        logger.error(f"模板渲染失败：{e}")
        return
    except Exception as e:
        logger.error(f"错误：{e}")
        return

    # 5. 提示下一步
    logger.info("\n[bold]下一步:[/]")
    logger.info("  forge plan ")
    logger.info("  forge tasks ")


def _interactive_input(content_type: str) -> str:
    """
    交互式输入

    Args:
        content_type: 内容类型

    Returns:
        用户输入的创意想法
    """
    logger.info(f"[dim]为 {content_type} 输入创意想法（或输入 'help' 查看示例）:[/dim]")

    idea = click.prompt("💡 Idea", type=str)

    if idea.lower() == 'help':
        examples = {
            'novel': "一个少年发现拥有魔法能力，必须阻止黑暗领主复活古代邪神",
            'article': "AI 对未来编程工作的影响和应对策略",
            'comic': "高中生侦探和他的助手解决校园谜团的故事"
        }

        example = examples.get(content_type, "我的创意故事")
        logger.info(f"\n[dim]示例：{example}[/dim]")
        idea = click.prompt("💡 Idea", type=str, default=example)

    return idea


def _handle_clarification(idea: str, questions: list) -> str:
    """
    处理澄清问题
    """

    logger.warning("❓ 需要澄清以下问题:")

    answers = []

    for i, q in enumerate(questions, 1):
        logger.info(f"\nQ{i}: {q}")

        answer = click.prompt(
            "你的回答（可回车跳过）",
            default="",
            show_default=False
        )

        if answer:
            answers.append(f"{q}: {answer}")

    if answers:
        idea = idea + "\n\n补充信息：\n" + "\n".join(answers)

    return idea
