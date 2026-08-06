# 环境校验服务 — specforge check
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from forge.models.backend import load_registry, BackendAdapter
from forge.models.project import find_project_root
from forge.__resources import get_bundled_path

# 有效的模板文件列表（不含 -template 后缀）
REQUIRED_TEMPLATES = ["spec", "plan", "tasks", "checklist", "constitution"]


@dataclass
class ToolStatus:
    """单个工具检测状态"""
    key: str
    name: str
    status: str          # available / not_found / ide_skipped
    detect_type: str     # cli / ide
    version: Optional[str] = None


@dataclass
class CheckResult:
    """check 操作结果"""
    tools: list[ToolStatus] = field(default_factory=list)
    templates_ok: Optional[bool] = None     # 仅项目内有效
    constitution_ok: Optional[bool] = None  # 仅项目内有效
    writable: bool = True
    in_project: bool = False
    errors: list[str] = field(default_factory=list)


def _check_cli_tool(backend: BackendAdapter) -> ToolStatus:
    """检测 CLI 工具是否已安装"""
    cmd = backend.detect_cmd
    if not shutil.which(cmd):
        return ToolStatus(
            key=backend.key, name=backend.name,
            status="not_found", detect_type="cli",
        )
    try:
        result = subprocess.run(
            [cmd, "--version"], capture_output=True, text=True, timeout=5,
        )
        version = result.stdout.strip().split("\n")[0] if result.stdout else "unknown"
        return ToolStatus(
            key=backend.key, name=backend.name,
            status="available", detect_type="cli", version=version,
        )
    except Exception:
        return ToolStatus(
            key=backend.key, name=backend.name,
            status="not_found", detect_type="cli",
        )


def check_environment(project_dir: Optional[Path] = None) -> CheckResult:
    """校验本地开发环境

    Args:
        project_dir: 项目根目录，None 时自动查找，找不到则按项目外模式执行

    Returns:
        CheckResult
    """
    result = CheckResult()

    if project_dir is None:
        project_dir = find_project_root()

    result.in_project = project_dir is not None

    # 1. 检测后端工具
    bundled = get_bundled_path()
    registry = load_registry(bundled / "backends" / "registry.json")
    for backend in registry.values():
        if backend.detect_type == "ide":
            result.tools.append(ToolStatus(
                key=backend.key, name=backend.name,
                status="ide_skipped", detect_type="ide",
            ))
        else:
            result.tools.append(_check_cli_tool(backend))

    # 2. 模板完整性（仅项目内）
    if result.in_project:
        templates_dir = project_dir / ".specforge" / "templates"
        missing = []
        for name in REQUIRED_TEMPLATES:
            fp = templates_dir / f"{name}-template.md"
            if not fp.is_file():
                missing.append(name)
        result.templates_ok = len(missing) == 0
        if missing:
            result.errors.append(f"模板不完整: 缺少 {', '.join(missing)}")

        # 3. constitution.md 检查
        constitution_path = project_dir / ".specforge" / "constitution.md"
        result.constitution_ok = constitution_path.is_file()
        if not result.constitution_ok:
            result.errors.append("constitution.md 缺失")

    # 4. 文件系统写权限
    if result.in_project:
        test_dir = project_dir / ".specforge" / ".tmp_check"
        test_dir.mkdir(parents=True, exist_ok=True)
    else:
        test_dir = Path.cwd()

    try:
        test_file = test_dir / ".write_test"
        test_file.write_text("ok")
        test_file.unlink()
        if result.in_project:
            test_dir.rmdir()
    except Exception:
        result.writable = False
        result.errors.append("文件系统不可写")

    return result
