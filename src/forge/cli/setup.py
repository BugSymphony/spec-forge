# setup 命令组 — 初始化 SDD 阶段环境
import json
import sys
import shutil
from pathlib import Path

import click
from rich.console import Console

from forge.cli._utils import require_project, ProjectNotFoundError
from forge.models.artifact_map import STAGE_ORDER
from forge.services.state_manager import StateManager
from forge.services.template_resolver import TemplateResolver
from forge.services.artifact_validator import validate_stage

console = Console()




def _get_feature_dir(project_root: Path) -> Path:
    """获取当前活动 feature 目录"""
    manager = StateManager(project_root)
    name = manager.get_current_feature()
    if name is None:
        console.print(
            "[red]Error: 无活动 feature。请使用 specforge use <feature>[/red]"
        )
        sys.exit(1)
    return project_root / "specs" / name


def setup_plan_command(force, json_output):
    """初始化 plan 环境"""
    project_root = require_project()
    feature_dir = _get_feature_dir(project_root)
    name = feature_dir.name

    # 前置校验：constitution.md + spec.md 存在
    constitution = project_root / ".specforge" / "constitution.md"
    spec = feature_dir / "spec.md"
    missing = []
    if not constitution.is_file():
        missing.append(".specforge/constitution.md")
    if not spec.is_file():
        missing.append("spec.md")
    if missing:
        console.print(
            f"[red]Error: 前置校验失败，缺少: {', '.join(missing)}[/red]"
        )
        sys.exit(1)

    files_created = []

    # 创建 build/ 目录（幂等）
    build_dir = feature_dir / "build"
    if not build_dir.is_dir():
        build_dir.mkdir()
        files_created.append(str(build_dir))

    # 拷贝 plan-template → plan.md
    plan_file = feature_dir / "plan.md"
    if plan_file.is_file() and not force:
        console.print(
            "[yellow]提示: plan.md 已存在，跳过不覆盖（使用 --force 强制覆盖）[/yellow]"
        )
    else:
        resolver = TemplateResolver(project_root)
        template = resolver.resolve("plan")
        if not template.exists:
            console.print(
                "[red]Error: plan-template 未找到。"
                "请检查 .specforge/templates/ 和内置模板[/red]"
            )
            sys.exit(2)
        shutil.copy2(Path(template.path), plan_file)
        files_created.append(str(plan_file))

    if json_output:
        console.print(json.dumps({
            "FEATURE": name,
            "FEATURE_SPEC": str(spec),
            "IMPL_PLAN": str(plan_file),
            "SPECS_DIR": str(feature_dir),
        }, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]✓ 已初始化 plan 环境:[/green]")
        for f in files_created:
            console.print(f"  + {Path(f).name}")


def setup_tasks_command(force, json_output):
    """初始化 tasks 环境"""
    project_root = require_project()
    feature_dir = _get_feature_dir(project_root)
    name = feature_dir.name

    # 前置校验：plan 阶段 artifact 完整性
    result = validate_stage(feature_dir, "plan", project_root)
    if not result.passed:
        console.print(
            f"[red]Error: plan 阶段未完成。缺失: {', '.join(result.missing)}[/red]"
        )
        sys.exit(1)

    # 扫描 build/ 目录获取 AVAILABLE_DOCS
    available_docs = []
    build_dir = feature_dir / "build"
    if build_dir.is_dir():
        for item in sorted(build_dir.iterdir()):
            suffix = " (目录)" if item.is_dir() else ""
            available_docs.append(item.name)

    # 拷贝 tasks-template → tasks.md
    tasks_file = feature_dir / "tasks.md"
    if tasks_file.is_file() and not force:
        console.print(
            "[yellow]提示: tasks.md 已存在，跳过不覆盖（使用 --force 强制覆盖）[/yellow]"
        )
    else:
        resolver = TemplateResolver(project_root)
        template = resolver.resolve("tasks")
        if not template.exists:
            console.print(
                "[red]Error: tasks-template 未找到。"
                "请检查 .specforge/templates/ 和内置模板[/red]"
            )
            sys.exit(2)

        # 获取 tasks-template 路径
        tasks_template_path = str(Path(template.path))
        shutil.copy2(Path(template.path), tasks_file)
    # 确定 TASKS_TEMPLATE 路径
    resolver = TemplateResolver(project_root)
    tpl = resolver.resolve("tasks")
    tasks_template_path = str(Path(tpl.path)) if tpl.exists else ""

    if json_output:
        console.print(json.dumps({
            "FEATURE": name,
            "FEATURE_DIR": str(feature_dir),
            "AVAILABLE_DOCS": available_docs,
            "TASKS_TEMPLATE": tasks_template_path,
        }, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]✓ 已初始化 tasks 环境:[/green]")
        console.print(f"  + tasks.md")
        if available_docs:
            console.print(
                f"[dim]  可用文档 (build/): {', '.join(available_docs)}[/dim]"
            )
