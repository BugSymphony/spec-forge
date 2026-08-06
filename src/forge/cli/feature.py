# feature 命令组 — list / show / use
import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from forge.cli._utils import require_project, ProjectNotFoundError
from forge.services.state_manager import StateManager, FeatureNotFoundError
from forge.services.feature_scanner import FeatureScanner, AmbiguousFeatureError

console = Console()




def _resolve_feature(feature_arg, manager, scanner):
    """解析 feature 参数——优先使用用户输入，否则回退到状态管理器"""
    if feature_arg:
        return scanner.resolve(feature_arg)
    current = manager.get_current_feature()
    if current is None:
        console.print(
            "[red]Error: 未指定 feature 且无活动 feature。"
            "请使用 specforge use <feature> 或指定 feature 名称[/red]"
        )
        sys.exit(1)
    return current


def use_command(feature):
    """切换到指定 feature"""
    project_root = require_project()
    manager = StateManager(project_root)
    scanner = FeatureScanner(project_root)

    try:
        name = scanner.resolve(feature)
    except AmbiguousFeatureError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except FeatureNotFoundError as e:
        console.print(f"[red]Error: 未找到 feature '{feature}'[/red]")
        sys.exit(1)

    current = manager.get_current_feature()
    if current == name:
        console.print(f"[yellow]提示: '{name}' 已是当前活动 feature[/yellow]")
        return

    try:
        manager.set_current_feature(name)
    except FeatureNotFoundError:
        console.print(f"[red]Error: feature 目录不存在: specs/{name}[/red]")
        sys.exit(1)

    console.print(f"[green]✓ 已切换到 feature '{name}'[/green]")


def list_command(detail, json_output):
    """列出所有 feature"""
    project_root = require_project()
    manager = StateManager(project_root)
    scanner = FeatureScanner(project_root)

    active = manager.get_current_feature()
    features = scanner.scan(active_feature=active)

    if json_output:
        result = {
            "features": [
                {
                    "name": f.name,
                    "path": str(f.path),
                    "number": f.number,
                    "active": f.is_active,
                    "stages": (
                        scanner.get_detail_stages(f.path, project_root) if detail else {}
                    ),
                }
                for f in features
            ],
            "total": len(features),
        }
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if not features:
        console.print("[dim](No features found)[/dim]")
        return

    if detail:
        table = Table(title=f"Features (共 {len(features)} 个)")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="dim")
        table.add_column("C", justify="center")
        table.add_column("S", justify="center")
        table.add_column("P", justify="center")
        table.add_column("T", justify="center")

        for f in features:
            stages = scanner.get_detail_stages(f.path, project_root)
            prefix = "◉ " if f.is_active else "  "
            table.add_row(
                f"{prefix}{f.name}",
                str(f.path),
                "✓" if stages.get("constitution") else "✗",
                "✓" if stages.get("spec") else "✗",
                "✓" if stages.get("plan") else "✗",
                "✓" if stages.get("tasks") else "✗",
            )
        console.print(table)
    else:
        names = []
        for f in features:
            if f.is_active:
                names.append(f"[bold cyan]◉ {f.name}[/bold cyan]")
            else:
                names.append(f"  {f.name}")
        console.print(f"Features (共 {len(features)} 个):\n")
        for n in names:
            console.print(n)


def show_command(feature, paths_only, artifact, stage, json_output):
    """显示 feature 详情"""
    project_root = require_project()
    manager = StateManager(project_root)
    scanner = FeatureScanner(project_root)

    try:
        name = _resolve_feature(feature, manager, scanner)
    except AmbiguousFeatureError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except FeatureNotFoundError as e:
        console.print(f"[red]Error: 未找到 feature '{feature}'[/red]")
        sys.exit(1)

    feature_dir = project_root / "specs" / name

    # --paths-only 模式
    if paths_only:
        spec_path = feature_dir / "spec.md"
        plan_path = feature_dir / "plan.md"
        tasks_path = feature_dir / "tasks.md"
        output = {
            "REPO_ROOT": str(project_root),
            "FEATURE_DIR": str(feature_dir),
            "FEATURE_SPEC": str(spec_path),
            "FEATURE_PLAN": str(plan_path),
            "FEATURE_TASKS": str(tasks_path),
        }
        if json_output:
            console.print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            for k, v in output.items():
                console.print(f"{k}={v}")
        return

    # --artifact 模式
    if artifact:
        # 无后缀自动匹配：递归搜索 FEATURE_DIR 和 build/
        art_path = _resolve_artifact_path(artifact, feature_dir, project_root)
        if art_path is None:
            console.print(f"[red]Error: artifact '{artifact}' 不存在于 feature '{name}' 中[/red]")
            sys.exit(1)

        if json_output:
            _show_artifact_json(art_path)
        else:
            _show_artifact_raw(art_path)
        return

    # 默认显示模式
    artifacts = scanner._scan_artifacts(feature_dir)
    artifacts_list = [
        (k, v) for k, v in artifacts.items()
    ]

    # --stage 过滤模式
    if stage:
        from forge.models.artifact_map import ARTIFACT_MAP, STAGE_ORDER
        if stage not in STAGE_ORDER:
            console.print(
                f"[red]Error: 无效的 stage '{stage}'。"
                f"可选: {', '.join(STAGE_ORDER)}[/red]"
            )
            sys.exit(1)

        # 构建该阶段对应的 artifact 路径集合
        stage_paths = set()
        for s in STAGE_ORDER:
            for art in ARTIFACT_MAP.get(s, []):
                stage_paths.add(art.path)
            if s == stage:
                break
        artifacts_list = [(k, v) for k, v in artifacts_list if k in stage_paths]

    if json_output:
        result = {
            "feature": name,
            "path": str(feature_dir),
            "artifacts": [
                {"path": k, "exists": v} for k, v in artifacts_list
            ],
        }
        if stage:
            result["stage"] = stage
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Feature: {name}[/bold]")
    console.print(f"路径: {feature_dir}")

    stage_label = f" (stage: {stage})" if stage else ""
    console.print(f"\n[bold]Artifacts{stage_label}:[/bold]")
    for art_path, exists in artifacts_list:
        icon = "[green]✓[/green]" if exists else "[red]✗[/red]"
        console.print(f"  {icon} {art_path}")


def _resolve_artifact_path(artifact_name: str, feature_dir: Path, project_root: Path):
    """无后缀自动匹配 artifact 路径，递归搜索 feature_dir 和 build/"""
    # 扩展名匹配列表
    extensions = ["", ".md", ".yaml", ".json"]
    for ext in extensions:
        candidate = artifact_name + ext
        # 先在根目录搜索
        root_path = feature_dir / candidate
        if root_path.exists():
            return root_path
        # 在 build/ 子目录搜索
        build_dir = feature_dir / "build"
        if build_dir.is_dir():
            build_path = build_dir / candidate
            if build_path.exists():
                return build_path
        # .specforge/ 路径（如 constitution）
        specforge_path = project_root / ".specforge" / candidate
        if specforge_path.exists():
            return specforge_path
    return None


def _show_artifact_raw(art_path: Path):
    """输出 artifact 原始内容"""
    if art_path.is_dir():
        console.print(f"[yellow]提示: '{art_path.name}' 是一个目录[/yellow]")
        return
    try:
        content = art_path.read_text(encoding="utf-8")
        console.print(content)
    except Exception as e:
        console.print(f"[red]Error: 读取文件失败: {e}[/red]")
        sys.exit(2)


def _show_artifact_json(art_path: Path):
    """输出 artifact JSON（解析 frontmatter）"""
    if art_path.is_dir():
        result = {"artifact": str(art_path), "type": "directory", "frontmatter": {}, "body": ""}
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    try:
        content = art_path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(2)

    # 解析 frontmatter（使用 python-frontmatter）
    try:
        import frontmatter
        post = frontmatter.loads(content)
        result = {
            "artifact": str(art_path),
            "frontmatter": dict(post.metadata) if post.metadata else {},
            "body": post.content,
        }
    except Exception:
        # frontmatter 解析失败 → 返回原始内容
        result = {
            "artifact": str(art_path),
            "frontmatter": {},
            "body": content,
        }
    console.print(json.dumps(result, ensure_ascii=False, indent=2))
