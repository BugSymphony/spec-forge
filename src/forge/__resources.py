# 内置资源访问 — 兼容开发期和发行包两种模式
import sys
from pathlib import Path

def _get_repo_root() -> Path:
    """获取仓库根目录（开发期使用）"""
    return Path(__file__).resolve().parent.parent.parent

def get_bundled_path() -> Path:
    """返回内置数据根路径（plugins/ 和 backends/ 的父目录）

    优先使用包内 _bundled/（发行包模式），回退到仓库根目录（开发期模式）
    """
    # 尝试 importlib.resources 访问发行包内置数据
    if sys.version_info >= (3, 9):
        try:
            from importlib.resources import files as _resources_files
            bundled = _resources_files("forge") / "_bundled"
            if bundled.is_dir():
                return bundled
        except (ImportError, TypeError, FileNotFoundError, AttributeError):
            pass

    # 回退：开发期直接使用仓库根目录
    return _get_repo_root()
