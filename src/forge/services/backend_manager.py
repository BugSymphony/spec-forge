# 后端管理服务 — specforge backend
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from forge.cli._utils import require_project
from forge.models.backend import load_registry, BackendAdapter
from forge.models.config import load_config, save_config
from forge.models.project import find_project_root
from forge.services.scaffolding import _get_command_source
from forge.__resources import get_bundled_path

# 命令文件名列表
COMMAND_FILES = [
    "constitution", "specify", "clarify", "plan",
    "tasks", "checklist", "analyze", "implement", "review",
]


@dataclass
class BackendStatus:
    """后端列表状态"""
    key: str
    name: str
    installed: bool = False
    active: bool = False


@dataclass
class BackendListResult:
    """backend list 结果"""
    backends: list[BackendStatus] = field(default_factory=list)
    in_project: bool = False


def _require_project():
    """确保在 SpecForge 项目内执行，否则抛出异常"""
    root = find_project_root()
    if root is None:
        raise RuntimeError("当前目录不是 SpecForge 项目。请先执行 specforge init")


def list_backends() -> BackendListResult:
    """列出所有可用后端"""
    bundled = get_bundled_path()
    registry = load_registry(bundled / "backends" / "registry.json")
    result = BackendListResult()

    root = find_project_root()
    result.in_project = root is not None

    current_backend = None
    if result.in_project:
        config = load_config(root / ".specforge" / "config.yaml")
        current_backend = config.backend

    for key, backend in registry.items():
        status = BackendStatus(key=key, name=backend.name)
        if result.in_project:
            status.installed = current_backend == key
            status.active = current_backend == key
        result.backends.append(status)

    return result


def install_backend(key: str):
    """安装后端到当前项目"""
    root = require_project(exit_on_error=False)

    bundled = get_bundled_path()
    registry = load_registry(bundled / "backends" / "registry.json")

    if key not in registry:
        available = ", ".join(registry.keys())
        raise ValueError(f"不支持的后端 '{key}'。可用: {available}")

    config = load_config(root / ".specforge" / "config.yaml")

    # 检查是否已有其他后端
    if config.backend and config.backend != key:
        raise RuntimeError(
            f"已安装后端 '{config.backend}'。"
            f"请先运行 specforge backend uninstall 或 specforge backend switch {key}"
        )

    # 检查是否重复安装
    if config.backend == key:
        raise RuntimeError(f"后端 '{key}' 已安装，无需重复操作")

    # 写入命令文件
    backend = registry[key]
    plugins_root = bundled / "plugins"
    for output_cfg in backend.outputs:
        output_dir = root / output_cfg.dir
        sep = output_cfg.invoke_separator
        for name in COMMAND_FILES:
            src = _get_command_source(plugins_root, config.content_type, name)
            if src is None:
                raise ValueError(f"命令文件缺失: {name}.md")
            dest_path = output_dir / f"{backend.command_prefix}{sep}{name}.md"
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_path)

    # 更新 config.yaml
    config.backend = key
    save_config(config, root / ".specforge" / "config.yaml")


def uninstall_backend(key: str | None = None):
    """卸载后端"""
    root = require_project(exit_on_error=False)

    bundled = get_bundled_path()
    registry = load_registry(bundled / "backends" / "registry.json")
    config = load_config(root / ".specforge" / "config.yaml")

    target_key = key or config.backend
    if target_key is None:
        raise RuntimeError("当前无已安装的后端")

    if target_key not in registry:
        raise ValueError(f"不支持的后端 '{target_key}'")

    backend = registry[target_key]

    # 清空命令文件
    for output_cfg in backend.outputs:
        output_dir = root / output_cfg.dir
        sep = output_cfg.invoke_separator
        for name in COMMAND_FILES:
            cmd_file = output_dir / f"{backend.command_prefix}{sep}{name}.md"
            cmd_file.unlink(missing_ok=True)

    # 更新 config
    config.backend = None
    save_config(config, root / ".specforge" / "config.yaml")


def switch_backend(key: str):
    """切换到指定后端"""
    root = require_project(exit_on_error=False)

    bundled = get_bundled_path()
    registry = load_registry(bundled / "backends" / "registry.json")

    if key not in registry:
        available = ", ".join(registry.keys())
        raise ValueError(f"不支持的后端 '{key}'。可用: {available}")

    config = load_config(root / ".specforge" / "config.yaml")

    # 相同后端，无需切换
    if config.backend == key:
        raise RuntimeError(f"已在目标后端 '{key}'，无需切换")

    # 先卸载旧后端
    if config.backend:
        uninstall_backend(config.backend)

    # 再安装新后端
    install_backend(key)
