# specforge version — 版本信息命令
import sys
import platform
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from forge import __version__

console = Console()


def version_command():
    """输出版本和构建信息"""
    console.print()
    console.print(Panel.fit(
        "[bold]SpecForge[/bold] — 规范驱动（SDD）内容生成引擎",
        border_style="blue",
    ))

    console.print(f"  版本:       [cyan]{__version__}[/cyan]")

    # 构建日期
    try:
        build_date = __build_date__  # type: ignore[name-defined]
    except NameError:
        build_date = "开发构建"

    # Git commit
    git_commit = "开发构建"
    try:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        git_head = repo_root / ".git" / "HEAD"
        if git_head.is_file():
            ref = git_head.read_text().strip()
            if ref.startswith("ref: "):
                ref_path = repo_root / ".git" / ref[5:]
                if ref_path.is_file():
                    git_commit = ref_path.read_text().strip()[:8]
            else:
                git_commit = ref[:8]
    except Exception:
        pass

    console.print(f"  构建日期:   [dim]{build_date}[/dim]")
    console.print(f"  Git Commit: [dim]{git_commit}[/dim]")
    console.print(f"  平台:       [dim]{platform.platform()}[/dim]")
    console.print(f"  Python:     [dim]{sys.version.split()[0]}[/dim]")
    console.print()
