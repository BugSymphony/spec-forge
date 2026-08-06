# 模板解析器 — 3 级模板搜索链
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from forge.__resources import get_bundled_path
from forge.models.config import load_config


@dataclass
class TemplatePath:
    """单个模板文件的解析路径记录"""
    stage: str                     # 阶段名
    priority: int                  # 搜索优先级
    source: str                    # 来源类型：project/content_type/default
    path: str                      # 文件系统路径
    exists: bool = False           # 文件是否存在


class TemplateResolver:
    """模板文件解析器——按优先级链搜索"""

    # 5 个阶段与模板名的映射
    STAGE_TEMPLATES = {
        "constitution": "constitution",
        "spec": "spec",
        "plan": "plan",
        "tasks": "tasks",
        "checklist": "checklist",
    }

    def __init__(self, project_root: Path):
        self._project_root = project_root
        self._content_type = self._load_content_type(project_root)
        self._bundled_root = self._get_bundled_root()

    def _load_content_type(self, project_root: Path) -> str:
        """加载项目内容类型"""
        config_path = project_root / ".specforge" / "config.yaml"
        if config_path.is_file():
            config = load_config(config_path)
            if config.content_type:
                return config.content_type
        return "_default"

    def _get_bundled_root(self) -> Optional[Path]:
        """获取发行包内置插件根目录"""
        try:
            return get_bundled_path() / "plugins"
        except Exception:
            return None

    def resolve(self, template_name: str) -> TemplatePath:
        """按优先级搜索模板，返回第一个存在的路径"""
        # 1. 项目级 .specforge/templates/<name>-template.md
        project_template = (
            self._project_root / ".specforge" / "templates" /
            f"{template_name}-template.md"
        )
        if project_template.is_file():
            return TemplatePath(
                stage=template_name, priority=1, source="project",
                path=str(project_template), exists=True,
            )

        # 2. 内容类型专用内置模板
        ct_template = self._resolve_bundled(template_name, self._content_type)
        if ct_template:
            return ct_template

        # 3. 通用回退 _default
        default_template = self._resolve_bundled(template_name, "_default")
        if default_template:
            return default_template

        return TemplatePath(
            stage=template_name, priority=0, source="none",
            path="", exists=False,
        )

    def _resolve_bundled(self, template_name: str, plugin: str) -> Optional[TemplatePath]:
        """在发行包内置插件中搜索模板"""
        if self._bundled_root is None:
            return None
        template_file = self._bundled_root / plugin / "templates" / f"{template_name}.md"
        priority = 2 if plugin == self._content_type else 3
        source = "content_type" if plugin == self._content_type else "default"
        return TemplatePath(
            stage=template_name, priority=priority, source=source,
            path=str(template_file), exists=template_file.is_file(),
        )

    def list_all(self) -> dict[str, list[TemplatePath]]:
        """列出所有模板在所有优先级的解析状态"""
        result = {}
        for stage, tpl_name in self.STAGE_TEMPLATES.items():
            paths = []

            # 优先级 1: 项目级
            p = self._project_root / ".specforge" / "templates" / f"{tpl_name}-template.md"
            paths.append(TemplatePath(
                stage=stage, priority=1, source="project",
                path=str(p), exists=p.is_file(),
            ))

            # 优先级 2: 内容类型
            if self._bundled_root:
                ct = self._bundled_root / self._content_type / "templates" / f"{tpl_name}.md"
                paths.append(TemplatePath(
                    stage=stage, priority=2, source="content_type",
                    path=str(ct), exists=ct.is_file(),
                ))

            # 优先级 3: _default
            if self._bundled_root:
                df = self._bundled_root / "_default" / "templates" / f"{tpl_name}.md"
                paths.append(TemplatePath(
                    stage=stage, priority=3, source="default",
                    path=str(df), exists=df.is_file(),
                ))

            result[stage] = paths
        return result

    # 9 个 SDD 阶段命令名
    CMD_STAGES = [
        "constitution", "specify", "clarify", "plan",
        "tasks", "checklist", "analyze", "implement", "review",
    ]

    # 已注册的内容类型
    KNOWN_TYPES = ["_default", "novel", "article", "comic", "video"]

    def resolve_command_coverage(self) -> dict[str, list[dict]]:
        """扫描各内容类型的 commands/ 目录，生成命令覆盖矩阵"""
        if self._bundled_root is None:
            return {}

        result = {}
        for stage in self.CMD_STAGES:
            entries = []
            for ctype in self.KNOWN_TYPES:
                cmd_file = self._bundled_root / ctype / "commands" / f"{stage}.md"
                if ctype == "_default":
                    entries.append({
                        "content_type": ctype,
                        "source": "self",
                        "exists": cmd_file.is_file(),
                    })
                else:
                    ct_cmd = self._bundled_root / ctype / "commands" / f"{stage}.md"
                    if ct_cmd.is_file():
                        entries.append({
                            "content_type": ctype,
                            "source": "dedicated",
                            "exists": True,
                        })
                    else:
                        entries.append({
                            "content_type": ctype,
                            "source": "fallback",
                            "exists": False,
                        })
            result[stage] = entries
        return result

    def get_coverage_summary(self) -> dict:
        """返回各内容类型的命令覆盖统计"""
        coverage = self.resolve_command_coverage()
        summary = {}
        for ctype in self.KNOWN_TYPES:
            dedicated = 0
            for stage, entries in coverage.items():
                for e in entries:
                    if e["content_type"] == ctype:
                        if ctype == "_default" and e["exists"]:
                            dedicated += 1
                        elif ctype != "_default" and e["source"] == "dedicated":
                            dedicated += 1
            summary[ctype] = {
                "total_stages": len(self.CMD_STAGES),
                "dedicated": dedicated,
                "fallback": len(self.CMD_STAGES) - dedicated if ctype != "_default" else 0,
            }
        return summary
