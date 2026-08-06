"""
gen-cli-ref.py — 从 Click 命令定义自动生成 CLI 参考文档初版

用法:
    python scripts/gen-cli-ref.py > docs/cli-reference-orgin.md

依赖:
    - click（项目运行时依赖）

输出:
    紧凑表格格式的 CLI 命令参考文档。
"""

import click
from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from forge.cli.main import main


def collect():
    result = []

    def walk(group, prefix=""):
        for name, cmd in group.commands.items():
            full_name = f"{prefix} {name}".strip() if prefix else name
            entry = {
                "name": full_name,
                "group": prefix if prefix else "root",
                "description": cmd.help or "",
                "params": [],
            }
            for p in cmd.params:
                if isinstance(p, click.Argument):
                    entry["params"].append(
                        {"name": p.name, "required": p.required, "type": "argument"}
                    )
                elif isinstance(p, click.Option):
                    choices = p.type.choices if hasattr(p.type, "choices") else []
                    entry["params"].append(
                        {
                            "name": ", ".join(p.opts),
                            "type": "flag" if p.is_flag else "option",
                            "required": p.required,
                            "choices": choices,
                        }
                    )
            if hasattr(cmd, "commands") and cmd.commands:
                walk(cmd, full_name)
                continue
            result.append(entry)

    walk(main)
    return result


def generate():
    cmds = collect()
    print("# CLI 命令参考\n")

    groups = {}
    for c in cmds:
        groups.setdefault(c["group"], []).append(c)

    for gname in sorted(groups.keys()):
        print(f"## {gname}\n")
        print("| 命令 | 说明 |")
        print("|------|------|")
        for c in groups[gname]:
            print(f"| `specforge {c['name']}` | {c['description']} |")
        print()

    print("---\n### 参数详情\n")
    for c in cmds:
        if c["params"]:
            print(f"#### `specforge {c['name']}`\n")
            print("| 参数 | 必需 | 说明 |")
            print("|------|------|------|")
            for p in c["params"]:
                req = "是" if p["required"] else "否"
                choices = (
                    ", ".join(f"`{x}`" for x in p.get("choices", []))
                    if p.get("choices")
                    else ""
                )
                print(f"| `{p['name']}` | {req} | {choices} |")
            print()


if __name__ == "__main__":
    generate()
