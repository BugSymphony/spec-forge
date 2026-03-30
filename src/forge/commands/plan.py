"""
/plan 命令处理
从 Spec 生成技术计划
"""
from typing import Optional

from ..agents.plan_agent import PlanAgent
from ..config.project_config import ProjectConfig
from ..exceptions import RenderError, YAMLParseError
from ..llm.factory import init_llm
from ..utils.logging import logger


def handle_plan(
        content_type: Optional[str] = None,
        llm_provider: str = None
):
    """
    处理 plan 命令
    
    Args:
        content_type: 内容类型（可选，从配置读取）
        spec: Spec 文件路径（可选）
    """
    logger.info(f"\n[bold blue]✨ SpecForge - Plan 生成器[/bold blue]\n")

    # 1. 从配置获取 content_type（如果未提供）
    if not content_type:
        config = ProjectConfig()
        content_type = config.get_content_type()
        logger.info(f"[dim]从配置加载内容类型：{content_type}[/dim]")

    # 2. 生成 Plan
    logger.step("正在生成技术计划...")

    llm = init_llm(provider=llm_provider)
    agent = PlanAgent(llm=llm)
    try:

        plan_content = agent.generate(
            content_type=content_type
        )

        if not plan_content:
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
    logger.info(f"\n[bold]下一步:[/]")
    logger.info(f"  forge tasks")
