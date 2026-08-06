# templates 命令 — 查看模板解析路径
import json
import sys

import click
from rich.console import Console
from rich.table import Table

from forge.cli._utils import require_project, ProjectNotFoundError
from forge.services.template_resolver import TemplateResolver

console = Console()




def templates_command(json_output):
    """按阶段分组显示模板解析路径"""
    project_root = require_project()
    resolver = TemplateResolver(project_root)
    all_templates = resolver.list_all()

    if json_output:
        coverage = resolver.resolve_command_coverage()
        summary = resolver.get_coverage_summary()
        result = {
            "templates": {},
            "commands": {},
            "coverage_summary": summary,
        }
        for stage, paths in all_templates.items():
            result["templates"][stage] = [
                {
                    "priority": p.priority,
                    "source": p.source,
                    "path": p.path,
                    "exists": p.exists,
                }
                for p in paths
            ]
        for stage, entries in coverage.items():
            result["commands"][stage] = entries
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    console.print("[bold]模板解析路径:[/bold]\n")
    stage_cn = {
        "constitution": "constitution",
        "spec": "spec",
        "plan": "plan",
        "tasks": "tasks",
        "checklist": "checklist",
    }

    priority_labels = {1: "project/", 2: "content_type/", 3: "default/"}

    for stage, paths in all_templates.items():
        label = stage_cn.get(stage, stage)
        console.print(f"[bold cyan]# {label}[/bold cyan]")
        for p in sorted(paths, key=lambda x: x.priority):
            icon = "[green]✓[/green]" if p.exists else "[red]✗[/red]"
            tag = priority_labels.get(p.priority, f"P{p.priority}/")
            console.print(f"  {icon}  {tag:15s} {p.path}")
        console.print()

    # 命令覆盖状态展示
    coverage = resolver.resolve_command_coverage()
    summary = resolver.get_coverage_summary()
    type_cn = {"_default": "默认(通用)", "novel": "小说", "article": "文章", "comic": "漫画", "video": "短剧"}

    console.print("[bold]命令覆盖状态 (9 阶段 × 各内容类型):[/bold]\n")

    cmd_table = Table(show_header=True, header_style="bold cyan")
    cmd_table.add_column("阶段", style="cyan")
    types_list = [t for t in resolver.KNOWN_TYPES if t != "_default"]
    for ct in types_list:
        cmd_table.add_column(type_cn.get(ct, ct), justify="center")

    for stage in resolver.CMD_STAGES:
        row = [stage]
        for ct in types_list:
            if coverage and stage in coverage:
                entry = next((e for e in coverage[stage] if e["content_type"] == ct), None)
                if entry and entry["source"] == "dedicated":
                    row.append("[green]专用[/green]")
                else:
                    row.append("回退")
            else:
                row.append("—")
        cmd_table.add_row(*row)

    console.print(cmd_table)
    console.print()

    console.print("[bold]覆盖统计:[/bold]")
    for ct in resolver.KNOWN_TYPES:
        s = summary.get(ct, {})
        ded = s.get("dedicated", 0)
        fb = s.get("fallback", 0)
        total = s.get("total_stages", 9)
        name = type_cn.get(ct, ct)
        if ct == "_default":
            console.print(f"  [green]{name}[/green]: {ded}/{total} (自给)")
        else:
            fb_count = total - ded
            console.print(f"  {name}: {ded} 专用 + {fb_count} 回退 ({ded+fb_count}/{total})")
