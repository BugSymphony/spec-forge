# specforge check — 环境校验命令
import sys

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from forge.services.checker import check_environment

console = Console()


def check_command():
    """校验本地开发环境"""
    result = check_environment()

    # 渲染结果
    console.print()
    console.print(Panel.fit(
        "[bold]环境检查结果[/bold]",
        border_style="blue",
    ))

    # 后端工具状态
    console.print()
    console.print("[bold]后端工具状态:[/bold]")
    table = Table(show_header=True)
    table.add_column("状态", width=4)
    table.add_column("工具", width=16)
    table.add_column("版本", width=16)
    table.add_column("备注", width=12)

    for t in result.tools:
        if t.status == "available":
            icon = "[green]●[/green]"
            note = "✓ 可用"
        elif t.status == "ide_skipped":
            icon = "[dim]○[/dim]"
            note = "[dim]IDE 内置 - 跳过[/dim]"
        else:
            icon = "[red]●[/red]"
            note = "[red]✗ 未安装[/red]"

        table.add_row(icon, t.name, t.version or "-", note)

    console.print(table)

    # 项目内额外检查
    if result.in_project:
        console.print()
        console.print("[bold]项目模板:[/bold]")
        if result.templates_ok:
            console.print("  [green]✓ 模板完整[/green] (5 个文件)")
        else:
            for e in result.errors:
                if "模板" in e:
                    console.print(f"  [red]✗ {e}[/red]")

        console.print("[bold]项目宪法:[/bold]")
        if result.constitution_ok:
            console.print("  [green]✓ .specforge/constitution.md 存在[/green]")
        else:
            console.print("  [red]✗ .specforge/constitution.md 缺失[/red]")

    # 文件系统
    console.print()
    console.print("[bold]文件系统:[/bold]")
    if result.writable:
        console.print("  [green]✓ 可写[/green]")
    else:
        console.print("  [red]✗ 不可写[/red]")

    if not result.in_project:
        console.print()
        console.print("[yellow]提示: 当前目录不是 SpecForge 项目[/yellow]")
        console.print("运行 [cyan]specforge init[/cyan] 创建新项目")

    console.print()

    # 存在任何错误时 exit 1
    sys.exit(1 if result.errors else 0)
