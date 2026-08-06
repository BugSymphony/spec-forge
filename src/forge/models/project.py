# 项目检测 — 查找 SpecForge 项目根目录
from pathlib import Path
from typing import Optional


def find_project_root(start: Optional[Path] = None) -> Optional[Path]:
    """向上遍历目录查找 .specforge/，返回项目根目录路径"""
    current = (start or Path.cwd()).resolve()
    for _ in range(100):  # 最多上溯 100 层
        if (current / ".specforge").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent
    return None
