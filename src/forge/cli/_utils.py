"""CLI 工具函数"""

import sys
from pathlib import Path

from forge.models.project import find_project_root


class ProjectNotFoundError(RuntimeError):
    """当前目录不是 SpecForge 项目"""
    pass


def require_project(exit_on_error: bool = True) -> Path:
    """验证当前目录在 SpecForge 项目内，返回项目根目录

    Args:
        exit_on_error: 如果为 True，打印错误并调用 sys.exit(1)；否则抛出异常
    """
    root = find_project_root()
    if root is None:
        if exit_on_error:
            print("Error: 当前目录不是 SpecForge 项目。请先执行 specforge init", file=sys.stderr)
            sys.exit(1)
        raise ProjectNotFoundError(
            "当前目录不是 SpecForge 项目。请先执行 specforge init"
        )
    return root
