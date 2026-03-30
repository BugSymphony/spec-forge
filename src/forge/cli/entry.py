"""
SpecForge CLI 入口点
"""
from pathlib import Path

import click
import yaml

from forge.commands import handle_implement, handle_tasks, handle_plan, handle_specify
from forge.commands.init import list_content_types, handle_init
from forge.utils.logging import logger


@click.group()
@click.version_option(version="0.1.0", prog_name="forge")
def main():
    """SpecForge - 规范驱动的内容生成系统"""
    pass


@main.command()
@click.option('--type', 'content_type', required=True, help='内容类型：novel|article|comic|video')
@click.option('--force', is_flag=True, help='强制覆盖已存在的配置')
def init(content_type, force):
    """初始化项目，加载指定内容类型的配置"""

    handle_init(
        content_type=content_type,
        force=force
    )


@main.command()
@click.option('--list', 'list_types', is_flag=True, help='列出所有内容类型')
def types(list_types):
    """查看可用的内容类型"""

    if list_types:
        list_content_types()
    else:
        # 显示当前项目类型
        from pathlib import Path
        config_file = Path(".forge/config.yaml")
        if config_file.exists():
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"当前项目类型：[bold cyan]{config.get('content_type', 'unknown')}[/bold cyan]")
        else:
            logger.warning("当前目录未初始化，请使用 forge init --type=<type> 初始化")


@main.command()
@click.option('--idea', default=None, help='创意想法描述')
@click.option('--no-prompt', is_flag=True, help='禁用交互模式')
@click.option('--llm', default='deepseek', help='使用的 LLM: openai|deepseek')
def specify(idea, no_prompt, llm):
    """生成结构化 Spec 文档（需要先执行 forge init）"""

    # 检查是否已初始化
    config_file = Path(".forge/config.yaml")
    if not config_file.exists():
        logger.info("[red]❌ 项目未初始化[/red]")
        logger.info("💡 请先运行：[bold]forge init --type=<类型>[/bold]")
        logger.info("\n可用类型:")
        logger.info("  - novel   (小说)")
        logger.info("  - article (文章)")
        logger.info("  - comic   (漫画)")
        logger.info("  - video   (视频)")
        return

    # 读取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    content_type = config.get('content_type')

    handle_specify(
        content_type=content_type,
        idea=idea,
        no_prompt=no_prompt,
        llm_provider=llm
    )


@main.command()
@click.option('--type', 'content_type', required=False, help='内容类型（可选，从配置读取）')
@click.option('--output', default=None, help='自定义输出路径')
@click.option('--llm', default='deepseek', help='使用的 LLM: openai|deepseek')
def plan(content_type, output, llm):
    """从 Spec 生成技术计划"""

    handle_plan(
        content_type=content_type
        , llm_provider=llm
    )


@main.command()
@click.option('--type', 'content_type', help='内容类型')
@click.option('--llm', default='deepseek', help='使用的 LLM: openai|deepseek')
def tasks(content_type, llm):
    """从 Plan 生成任务清单"""

    handle_tasks(
        content_type=content_type,
        llm_provider=llm
    )


@main.command()
@click.option('--mode', default='loop', type=click.Choice(['single', 'loop']),
              help='执行模式：single(单步) | loop(循环)')
@click.option('--task', default=None, help='指定任务 ID（single 模式使用）')
@click.option('--auto', is_flag=True, help='自动确认，不询问用户（loop 模式使用）')
@click.option('--llm', default='deepseek', help='使用的 LLM: openai|deepseek')
def implement(mode, task, auto, llm):
    """执行 tasks.md 中的任务，生成最终产物"""

    handle_implement(
        mode=mode,
        task_id=task,
        auto_confirm=auto,
        llm_provider=None  # 在 implement 中根据 llm 参数初始化
    )


if __name__ == '__main__':
    main()
