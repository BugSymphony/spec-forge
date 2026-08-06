# new 命令 — 创建新 feature
import json
import sys
import shutil
from pathlib import Path

import click
from rich.console import Console

from forge.cli._utils import require_project, ProjectNotFoundError
from forge.services.state_manager import StateManager
from forge.services.name_generator import (
    generate_short_name, compute_next_number, build_dir_name,
    generate_timestamp_prefix, validate_short_name,
)
from forge.services.template_resolver import TemplateResolver

console = Console()




def new_command(description, short_name, number, timestamp, dry_run, json_output):
    """创建新 feature"""
    project_root = require_project()
    specs_dir = project_root / "specs"

    # 参数校验
    if not description or not description.strip():
        console.print("[red]Error: 必须提供 feature 描述[/red]")
        sys.exit(1)
    description = description.strip()

    # --number 校验
    if number is not None:
        if timestamp:
            console.print(
                "[yellow]Warning: --number 在 --timestamp 模式下被忽略[/yellow]"
            )
            number = None
        else:
            try:
                number = int(number)
                if number < 1 or number > 9999:
                    console.print(
                        "[red]Error: --number 必须为正整数 (1-9999)[/red]"
                    )
                    sys.exit(1)
            except (ValueError, TypeError):
                console.print("[red]Error: --number 必须为正整数[/red]")
                sys.exit(1)

    # 计算短名
    if short_name:
        short_name = validate_short_name(short_name)
        if not short_name:
            console.print("[red]Error: --short-name 无效（仅含停用词或空字符串）[/red]")
            sys.exit(1)
    else:
        short_name = generate_short_name(description)

    # 计算编号/前缀
    if timestamp:
        prefix = generate_timestamp_prefix()
        number_val = None
    else:
        if number:
            number_val = number
        else:
            number_val = compute_next_number(specs_dir)
        prefix = f"{number_val:03d}"

    dir_name = build_dir_name(prefix, short_name)
    feature_dir = specs_dir / dir_name

    # --dry-run
    if dry_run:
        if json_output:
            console.print(json.dumps({
                "name": dir_name,
                "path": str(feature_dir),
                "number": number_val if not timestamp else None,
                "short_name": short_name,
                "dry_run": True,
                "spec_file": str(feature_dir / "spec.md"),
            }, ensure_ascii=False, indent=2))
        else:
            console.print(f"[bold][DRY RUN] 将创建 feature:[/bold]")
            console.print(f"  目录: {feature_dir}")
            console.print(f"  spec:  {feature_dir / 'spec.md'}")
        return

    # 检查目录冲突
    if feature_dir.exists():
        console.print(
            f"[red]Error: 目录已存在 '{dir_name}'。"
            f"请使用 --number 或 --short-name 修改名称[/red]"
        )
        sys.exit(1)

    # 创建目录 + 拷贝 spec-template
    try:
        specs_dir.mkdir(parents=True, exist_ok=True)
        feature_dir.mkdir()

        resolver = TemplateResolver(project_root)
        template = resolver.resolve("spec")
        if not template.exists:
            console.print(
                "[red]Error: spec-template 未找到。"
                "请检查 .specforge/templates/ 和内置模板[/red]"
            )
            shutil.rmtree(feature_dir)
            sys.exit(2)

        spec_file = feature_dir / "spec.md"
        shutil.copy2(Path(template.path), spec_file)

    except Exception as e:
        # 回滚
        if feature_dir.exists():
            shutil.rmtree(feature_dir)
        console.print(f"[red]Error: 创建 feature 失败: {e}[/red]")
        sys.exit(2)

    # 设为活动 feature
    manager = StateManager(project_root)
    manager.set_current_feature(dir_name)

    if json_output:
        console.print(json.dumps({
            "name": dir_name,
            "path": str(feature_dir),
            "number": number_val if not timestamp else None,
            "short_name": short_name,
            "spec_file": str(spec_file),
        }, ensure_ascii=False, indent=2))
    else:
        console.print(f"[green]✓ 已创建 feature: {dir_name}[/green]")
        console.print(f"  spec.md 已就绪。")
        console.print(
            f"\n[dim]下一步: 已自动切换活动 feature 到 '{dir_name}'[/dim]"
        )
