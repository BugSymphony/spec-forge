# specforge init — 项目脚手架命令
import sys
from pathlib import Path

import click
import questionary
from rich.console import Console
from rich.panel import Panel

from forge.models.content_type import discover_plugins
from forge.models.backend import load_registry
from forge.services.scaffolding import init_project, TEMPLATE_FILES, COMMAND_FILES
from forge.__resources import get_bundled_path

console = Console()


def _interactive_select(bundled_path: Path, plugins_dir: Path | None = None) -> tuple[str, str | None, bool]:
    """交互式选单：选择内容类型和后端，返回 (content_type, backend_key, ai_skills)"""
    # 加载可选项（内建 + 外部插件合并）
    extra_roots = []
    if plugins_dir is not None and plugins_dir.is_dir():
        extra_roots.append(plugins_dir)
    types = discover_plugins(bundled_path / "plugins", extra_roots=extra_roots if extra_roots else None)
    if not types:
        click.echo("错误: 未发现任何内容类型插件", err=True)
        sys.exit(1)

    type_keys = list(types.keys())
    type_names = [f"{t.name_cn} ({t.key})" for t in types.values()]

    registry = load_registry(bundled_path / "backends" / "registry.json")
    backend_keys = list(registry.keys())
    backend_names = [f"{b.name} ({b.key})" for b in registry.values()]

    # 选内容类型
    content_type = questionary.select(
        "请选择内容类型:",
        choices=[
            questionary.Choice(title=type_names[i], value=type_keys[i])
            for i in range(len(type_keys))
        ],
    ).ask()
    if content_type is None:
        click.echo("已取消")
        sys.exit(0)

    # 选后端
    backend_choice = questionary.select(
        "请选择 AI 后端:",
        choices=[
            questionary.Choice(title=backend_names[i], value=backend_keys[i])
            for i in range(len(backend_keys))
        ],
    ).ask()
    if backend_choice is None:
        click.echo("已取消")
        sys.exit(0)

    # 询问是否安装 skills（仅当后端支持 skills 时）
    ai_skills = False
    backend = registry.get(backend_choice)
    if backend and any(cfg.type == "skills" for cfg in backend.outputs):
        ai_skills = questionary.select(
            "也安装 AI agent skills 吗？",
            choices=[
                questionary.Choice(title="否", value=False),
                questionary.Choice(title="是", value=True),
            ],
        ).ask()

    return content_type, backend_choice, ai_skills


def init_command(content_type: str | None, backend_key: str | None, force: bool, plugins_dir: Path | None = None, ai_skills: bool = False):
    """初始化 SpecForge 运行时项目"""
    bundled = get_bundled_path()
    project_dir = Path.cwd()

    # 参数校验：--type 和 --backend 必须同时提供
    if (content_type and not backend_key) or (backend_key and not content_type):
        click.echo("错误: --type 和 --backend 必须同时指定", err=True)
        sys.exit(1)

    # 参数校验：--ai-skills 需要 --backend
    if ai_skills and not backend_key:
        click.echo("错误: --ai-skills requires --backend to be specified", err=True)
        sys.exit(1)

    # 交互模式 vs 参数模式
    if not content_type:
        content_type, backend_key, ai_skills = _interactive_select(bundled, plugins_dir)

    try:
        result = init_project(project_dir, content_type, backend_key, force, plugins_dir, ai_skills)

        # 输出成功信息
        console.print()
        console.print(Panel.fit(
            "[bold green]✓ 项目初始化成功[/bold green]",
            title="SpecForge"
        ))

        # 基本信息
        console.print(f"  内容类型: [cyan]{result.content_type}[/cyan]")
        console.print(f"  AI 后端:  [cyan]{result.backend or '未选择'}[/cyan]")

        # 产物模板列表
        console.print()
        console.print("[bold]产物模板[/bold] (.specforge/templates/):")
        for name in TEMPLATE_FILES:
            console.print(f"  • [green]{name}-template.md[/green]")

        # Agent 命令列表
        if result.backend:
            bundled_p = bundled
            registry = load_registry(bundled_p / "backends" / "registry.json")
            backend = registry.get(result.backend)
            if backend:
                console.print()
                for output_cfg in backend.outputs:
                    if output_cfg.type == "slash_commands":
                        console.print(f"[bold]Agent 命令[/bold] ({output_cfg.dir}/):")
                        for name in COMMAND_FILES:
                            console.print(f"  • [green]{backend.command_prefix}{output_cfg.invoke_separator}{name}.md[/green]")
                    elif output_cfg.type == "skills":
                        console.print(f"[bold]Agent Skills[/bold] ({output_cfg.dir}/):")
                        for name in COMMAND_FILES:
                            console.print(f"  • [green]{backend.command_prefix}-{name}/SKILL.md[/green]")

        # 警告
        if result.warnings:
            console.print()
            for w in result.warnings:
                console.print(f"  [yellow]提示: {w}[/yellow]")

        console.print()
        console.print("[bold]下一步:[/bold]")
        console.print("  [cyan]specforge check[/cyan]  — 校验环境就绪")

    except FileExistsError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"错误: 初始化失败 - {e}", err=True)
        sys.exit(2)
