# validate 命令 — 校验 feature artifact 完整性
import json
import sys

import click
from rich.console import Console

from forge.cli._utils import require_project, ProjectNotFoundError
from forge.models.artifact_map import STAGE_ORDER
from forge.services.state_manager import StateManager, FeatureNotFoundError
from forge.services.feature_scanner import FeatureScanner, AmbiguousFeatureError
from forge.services.artifact_validator import validate_stage

console = Console()




def validate_command(feature, stage, json_output):
    """校验 feature artifact 完整性"""
    if not stage:
        console.print(
            "[red]Error: --stage 参数必须指定。"
            f"可选: {', '.join(STAGE_ORDER)}[/red]"
        )
        sys.exit(1)

    if stage not in STAGE_ORDER:
        console.print(
            f"[red]Error: 无效的 stage '{stage}'。"
            f"可选: {', '.join(STAGE_ORDER)}[/red]"
        )
        sys.exit(1)

    project_root = require_project()
    manager = StateManager(project_root)
    scanner = FeatureScanner(project_root)

    try:
        if feature:
            name = scanner.resolve(feature)
        else:
            name = manager.get_current_feature()
    except AmbiguousFeatureError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except FeatureNotFoundError as e:
        console.print(f"[red]Error: 未找到 feature '{feature}'[/red]")
        sys.exit(1)

    if name is None:
        console.print(
            "[red]Error: 未指定 feature 且无活动 feature。"
            "请使用 specforge use <feature> 或指定 feature 名称[/red]"
        )
        sys.exit(1)

    feature_dir = project_root / "specs" / name

    # 纯流程阶段（无 artifact）
    if stage in ("clarify", "analyze"):
        if json_output:
            console.print(json.dumps({
                "feature": name, "stage": stage, "passed": True,
                "artifacts": [], "missing": [], "warnings": [],
            }, ensure_ascii=False, indent=2))
        else:
            console.print(f"[green]✓ 校验 feature '{name}' 到 stage '{stage}': 通过[/green]")
            console.print("[dim]此阶段无 artifact 校验需求[/dim]")
        sys.exit(0)

    result = validate_stage(feature_dir, stage, project_root)

    if json_output:
        console.print(json.dumps({
            "feature": name,
            "stage": stage,
            "passed": result.passed,
            "artifacts": result.artifacts,
            "missing": result.missing,
            "warnings": result.warnings,
        }, ensure_ascii=False, indent=2))
    else:
        if result.passed:
            total = len(result.artifacts)
            console.print(
                f"[green]✓ 校验 feature '{name}' 到 stage '{stage}': 通过[/green]"
            )
            console.print(f"所有必需 artifact 存在 ({total}/{total})。")
            if result.warnings:
                console.print(f"[yellow]警告: 缺失可选 artifact: {', '.join(result.warnings)}[/yellow]")
        else:
            console.print(
                f"[red]✗ 校验 feature '{name}' 到 stage '{stage}': 未通过[/red]"
            )
            if result.missing:
                console.print(f"\n缺失的必需 artifact:")
                for m in result.missing:
                    console.print(f"  [red]✗[/red] {m}")
            if result.warnings:
                console.print(f"\n缺失的可选 artifact (警告):")
                for w in result.warnings:
                    console.print(f"  [yellow]⚠[/yellow] {w}")
            passed_count = sum(1 for a in result.artifacts if a["exists"] and a["required"])
            required_total = sum(1 for a in result.artifacts if a["required"])
            console.print(
                f"\n通过: {passed_count}/{required_total}"
                f"{f' | 警告: {len(result.warnings)}' if result.warnings else ''}"
            )

    sys.exit(0 if result.passed else 1)
