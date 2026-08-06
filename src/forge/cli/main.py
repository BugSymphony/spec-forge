# specforge CLI 主命令组
import click
from pathlib import Path
from forge import __version__


@click.group(name="specforge")
@click.version_option(version=__version__, prog_name="SpecForge")
@click.pass_context
def main(ctx: click.Context):
    """SpecForge — 规范驱动（SDD）内容生成引擎

    初始化项目、管理内容类型插件与 AI 后端集成、Feature 工作流管理。
    """
    ctx.ensure_object(dict)


@main.command("version")
def version_cmd():
    """查看版本和构建信息"""
    from forge.cli.version import version_command
    version_command()


@main.command("init")
@click.option("--type", "content_type", help="内容类型 (novel|article|comic|video)")
@click.option("--backend", "backend_key", help="AI 后端 (opencode|cursor|claude_code)")
@click.option("--force", is_flag=True, help="强制重新初始化，清空已有 .specforge/ 目录")
@click.option("--plugins-dir", "plugins_dir", type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path), default=None, help="外部插件集合目录")
@click.option("--ai-skills", is_flag=True, help="安装 AI agent skills 到后端 skills 目录")
def init_cmd(content_type: str, backend_key: str, force: bool, plugins_dir: Path | None, ai_skills: bool):
    """初始化 SpecForge 运行时项目"""
    from forge.cli.init import init_command
    init_command(content_type, backend_key, force, plugins_dir, ai_skills)


@main.command("check")
def check_cmd():
    """校验本地开发环境（后端工具、模板完整性、文件系统权限）"""
    from forge.cli.check import check_command
    check_command()


@main.group("backend")
def backend_group():
    """后端集成管理（列表、安装、卸载、切换）"""
    pass


@backend_group.command("list")
def backend_list():
    """列出可用后端及其安装状态"""
    from forge.cli.backend import list_command
    list_command()


@backend_group.command("install")
@click.argument("key")
def backend_install(key: str):
    """安装指定后端到当前项目"""
    from forge.cli.backend import install_command
    install_command(key)


@backend_group.command("uninstall")
@click.argument("key", required=False)
def backend_uninstall(key: str | None):
    """卸载当前（或指定）后端"""
    from forge.cli.backend import uninstall_command
    uninstall_command(key)


@backend_group.command("switch")
@click.argument("key")
def backend_switch(key: str):
    """切换到其他后端"""
    from forge.cli.backend import switch_command
    switch_command(key)


# ==================== Feature 管理命令组 ====================

@main.command("use")
@click.argument("feature")
def use_cmd(feature: str):
    """切换活动 feature（支持精确全名/短名后缀/编号前缀匹配）"""
    from forge.cli.feature import use_command
    use_command(feature)


@main.command("list")
@click.option("--detail", is_flag=True, help="显示完整路径和阶段文档存在状态")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def list_cmd(detail: bool, json_output: bool):
    """列出所有 feature"""
    from forge.cli.feature import list_command
    list_command(detail, json_output)


@main.command("show")
@click.argument("feature", required=False)
@click.option("--paths-only", is_flag=True, help="仅输出路径键值对")
@click.option("--artifact", "artifact", default=None, help="输出指定文档的原始内容")
@click.option("--stage", "stage", default=None, help="按阶段过滤 artifact 列表")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def show_cmd(feature: str, paths_only: bool, artifact: str, stage: str, json_output: bool):
    """显示 feature 完整路径信息和 artifact 列表"""
    from forge.cli.feature import show_command
    show_command(feature, paths_only, artifact, stage, json_output)


# ==================== new 命令 ====================

@main.command("new")
@click.argument("description")
@click.option("--short-name", default=None, help="自定义短名 (2-4 词)")
@click.option("--number", type=int, default=None, help="手动指定编号 (正整数, 1-9999)")
@click.option("--timestamp", is_flag=True, help="使用时间戳前缀替代顺序编号")
@click.option("--dry-run", is_flag=True, help="计算名称和路径但不创建")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def new_cmd(description: str, short_name: str, number: int, timestamp: bool, dry_run: bool, json_output: bool):
    """创建新的 feature"""
    from forge.cli.new import new_command
    new_command(description, short_name, number, timestamp, dry_run, json_output)


# ==================== validate 命令 ====================

@main.command("validate")
@click.argument("feature", required=False)
@click.option("--stage", required=True, help="校验到哪个阶段（必填）")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def validate_cmd(feature: str, stage: str, json_output: bool):
    """校验 feature 到指定阶段的 artifact 完整性"""
    from forge.cli.validate import validate_command
    validate_command(feature, stage, json_output)


# ==================== setup 命令组 ====================

@main.group("setup")
def setup_group():
    """初始化 SDD 阶段环境"""
    pass


@setup_group.command("plan")
@click.option("--force", is_flag=True, help="强制覆盖已存在的 plan.md")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def setup_plan(force: bool, json_output: bool):
    """初始化 plan 环境（创建 plan.md + build/ 目录）"""
    from forge.cli.setup import setup_plan_command
    setup_plan_command(force, json_output)


@setup_group.command("tasks")
@click.option("--force", is_flag=True, help="强制覆盖已存在的 tasks.md")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def setup_tasks(force: bool, json_output: bool):
    """初始化 tasks 环境（创建 tasks.md）"""
    from forge.cli.setup import setup_tasks_command
    setup_tasks_command(force, json_output)


# ==================== templates 命令 ====================

@main.command("templates")
@click.option("--json", "json_output", is_flag=True, help="JSON 格式输出")
def templates_cmd(json_output: bool):
    """按阶段分组查看模板解析路径"""
    from forge.cli.templates import templates_command
    templates_command(json_output)
