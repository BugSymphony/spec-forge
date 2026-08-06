# specforge backend — 后端管理命令
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from forge.services.backend_manager import (
    list_backends, install_backend, uninstall_backend, switch_backend,
)

console = Console()


def list_command():
    """列出可用后端"""
    result = list_backends()

    console.print()
    console.print(Panel.fit(
        "[bold]可用后端[/bold]",
        border_style="blue",
    ))

    table = Table(show_header=result.in_project)
    table.add_column("状态", width=4)
    table.add_column("后端", width=16)
    table.add_column("名称", width=16)
    if result.in_project:
        table.add_column("备注", width=16)

    for b in result.backends:
        if result.in_project:
            if b.active:
                icon = "[cyan]◉[/cyan]"
                note = "✓ 当前激活"
            elif b.installed:
                icon = "[green]●[/green]"
                note = "已安装"
            else:
                icon = "[dim]○[/dim]"
                note = "未安装"
            table.add_row(icon, b.key, b.name, note)
        else:
            icon = "□"
            table.add_row(icon, b.key, b.name)

    console.print(table)

    if result.in_project:
        console.print()
        console.print("使用 [cyan]specforge backend install <key>[/cyan] 安装后端")
    console.print()


def install_command(key: str):
    """安装后端"""
    try:
        install_backend(key)
        console.print()
        console.print(f"[green]✓ 后端 '{key}' 安装完成[/green]")
        console.print()
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


def uninstall_command(key: str | None):
    """卸载后端"""
    try:
        uninstall_backend(key)
        console.print()
        console.print(f"[green]✓ 后端 '{key or '当前'}' 已卸载[/green]")
        console.print()
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)


def switch_command(key: str):
    """切换后端"""
    try:
        switch_backend(key)
        console.print()
        console.print(f"[green]✓ 已切换到后端 '{key}'[/green]")
        console.print()
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]错误: {e}[/red]")
        sys.exit(1)
