"""
/tasks 命令处理
从 Plan 和 Spec 生成任务清单
"""
from ..config import ProjectConfig
from ..agents.tasks_agent import TasksAgent
from ..exceptions import RenderError, YAMLParseError
from ..llm.factory import init_llm
from ..utils.logging import logger


def handle_tasks(
        content_type: str,
        llm_provider: str = None
):
    """
    处理 tasks 命令
    
    Args:
        content_type: 内容类型
        llm_client: LLM 客户端名称（openai|deepseek）
    """
    logger.info(f"\n[bold blue]✨ SpecForge - Tasks 生成器[/bold blue]\n")

    # 1. 从配置获取 content_type（如果未提供）
    if not content_type:
        config = ProjectConfig()
        content_type = config.get_content_type()
        logger.info(f"[dim]从配置加载内容类型：{content_type}[/dim]")

    # 2. 生成 Tasks
    logger.step("正在生成任务清单...")

    llm = init_llm(provider=llm_provider)
    agent = TasksAgent(llm=llm)
    try:

        tasks_content = agent.generate(
            content_type=content_type
        )

        if not tasks_content:
            logger.error("错误：Plan 生成失败")
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

    # 提示下一步
    logger.info("\n[bold]下一步:[/]")
    logger.info("  forge implement")
