# 脚手架服务 — specforge init 核心逻辑
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from forge.models.content_type import discover_plugins
from forge.models.backend import load_registry, BackendAdapter, OutputConfig
from forge.models.config import RuntimeConfig, save_config
from forge.__resources import get_bundled_path
from forge import __version__

# 制品模板文件名列表（按顺序）
TEMPLATE_FILES = ["spec", "plan", "tasks", "checklist", "constitution"]

# Agent 命令文件名列表（按顺序）
COMMAND_FILES = [
    "constitution", "specify", "clarify", "plan",
    "tasks", "checklist", "analyze", "implement", "review",
]


@dataclass
class InitResult:
    """init 操作结果"""
    project_dir: Path
    content_type: str
    backend: Optional[str]
    files_created: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _get_template_source(plugins_root: Path, content_type: str, filename: str) -> Optional[Path]:
    """两级回退获取模板文件路径"""
    specific = plugins_root / content_type / "templates" / f"{filename}.md"
    if specific.is_file():
        return specific
    default = plugins_root / "_default" / "templates" / f"{filename}.md"
    if default.is_file():
        return default
    return None


def _get_command_source(plugins_root: Path, content_type: str, filename: str) -> Optional[Path]:
    """两级回退获取命令文件路径"""
    specific = plugins_root / content_type / "commands" / f"{filename}.md"
    if specific.is_file():
        return specific
    default = plugins_root / "_default" / "commands" / f"{filename}.md"
    if default.is_file():
        return default
    return None


def _write_file(path: Path, content: str, files_created: list[Path]):
    """写入文件并记录到文件清单"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    files_created.append(path)


def _copy_file(src: Path, dst: Path, files_created: list[Path]):
    """复制文件并记录"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    files_created.append(dst)


def rollback(files_created: list[Path]):
    """回滚：删除已创建的所有文件和目录"""
    for fp in sorted(files_created, key=lambda p: len(str(p)), reverse=True):
        try:
            if fp.is_file() or fp.is_symlink():
                fp.unlink(missing_ok=True)
            elif fp.is_dir():
                shutil.rmtree(fp)
        except OSError:
            pass


def _install_commands(project_dir: Path, backend: BackendAdapter, output_cfg: OutputConfig,
                      content_type: str, plugins_root: Path,
                      files_created: list[Path], warnings: list[str]):
    """安装 slash_commands / rules 类型的命令文件到后端输出目录"""
    output_dir = project_dir / output_cfg.dir
    sep = output_cfg.invoke_separator
    for name in COMMAND_FILES:
        cmd_src = _get_command_source(plugins_root, content_type, name)
        if cmd_src is None:
            raise ValueError(
                f"命令文件缺失: {name}.md"
                f"（内容类型 '{content_type}' 和 _default 均未找到）"
            )
        dest_filename = f"{backend.command_prefix}{sep}{name}.md"
        dest_path = output_dir / dest_filename
        if dest_path.exists():
            warnings.append(f"命令文件已存在，跳过: {dest_path}")
            continue
        _copy_file(cmd_src, dest_path, files_created)


def _install_skills(project_dir: Path, backend: BackendAdapter, output_cfg: OutputConfig,
                    content_type: str, plugins_root: Path,
                    files_created: list[Path], warnings: list[str]):
    """安装 skills 类型的 SKILL.md 到后端 skills 目录

    从命令文件读取内容，保留原始 frontmatter 的 description，
    转换为子目录结构 specforge-{stage}/SKILL.md。
    """
    skills_dir = project_dir / output_cfg.dir
    skills_dir.mkdir(parents=True, exist_ok=True)

    for name in COMMAND_FILES:
        cmd_src = _get_command_source(plugins_root, content_type, name)
        if cmd_src is None:
            raise ValueError(f"技能命令文件缺失: {name}.md")

        content = cmd_src.read_text(encoding="utf-8")
        description = ""

        # 解析原始 YAML frontmatter，提取 description
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    if isinstance(fm, dict):
                        description = fm.get("description", "")
                except yaml.YAMLError:
                    pass
                body = parts[2].strip()
            else:
                body = content
        else:
            body = content

        skill_name = f"{backend.command_prefix}-{name}"

        # 构造 SKILL.md
        frontmatter_data = {
            "name": skill_name,
            "description": description,
            "compatibility": "Requires SpecForge project structure with .specforge/ directory",
            "metadata": {
                "author": "specforge",
                "source": f"plugins/{content_type}/commands/{name}.md",
            },
        }
        frontmatter_text = yaml.safe_dump(frontmatter_data, allow_unicode=True, sort_keys=False).strip()
        skill_content = (
            f"---\n"
            f"{frontmatter_text}\n"
            f"---\n\n"
            f"{body}\n"
        )

        skill_dir = skills_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"

        if skill_file.exists():
            warnings.append(f"技能文件已存在，跳过: {skill_file}")
            continue

        skill_file.write_text(skill_content, encoding="utf-8")
        files_created.append(skill_dir)
        files_created.append(skill_file)


# 输出类型 → 安装函数映射表
OUTPUT_INSTALLERS = {
    "slash_commands": _install_commands,
    "rules": _install_commands,
    "skills": _install_skills,
}


def init_project(project_dir: Path, content_type: str, backend_key: str | None,
                 force: bool = False, plugins_dir: Path | None = None,
                 ai_skills: bool = False) -> InitResult:
    """初始化 SpecForge 运行时项目

    Args:
        project_dir: 项目根目录
        content_type: 内容类型 key（novel/article/comic/video）
        backend_key: 后端 key（opencode/cursor/claude_code），可为 None
        force: 是否强制重新初始化
        plugins_dir: 外部插件集合目录，可为 None
        ai_skills: 是否启用 skills 安装（覆盖 registry 中的 enabled 设置）

    Returns:
        InitResult 包含已创建文件列表

    Raises:
        ValueError: 参数无效或模板缺失
        FileExistsError: 项目已存在且未指定 --force
    """
    files_created: list[Path] = []
    warnings: list[str] = []
    result = InitResult(
        project_dir=project_dir,
        content_type=content_type,
        backend=backend_key,
        files_created=files_created,
        warnings=warnings,
    )

    # 1. 检测项目是否已存在
    specforge_dir = project_dir / ".specforge"
    if specforge_dir.exists():
        if force:
            shutil.rmtree(specforge_dir)
        else:
            raise FileExistsError(f"项目已存在: {project_dir}。使用 --force 强制重新初始化")

    # 2. 加载插件和后端注册表
    bundled = get_bundled_path()
    plugins_root = bundled / "plugins"

    extra_roots = []
    if plugins_dir is not None:
        if not plugins_dir.is_dir():
            warnings.append(f"外部插件目录不存在，跳过: {plugins_dir}")
        else:
            extra_roots.append(plugins_dir)

    types = discover_plugins(plugins_root, extra_roots=extra_roots if extra_roots else None)
    if content_type not in types:
        available = ", ".join(types.keys()) or "无"
        raise ValueError(f"不支持的内容类型 '{content_type}'。可用: {available}")

    registry = load_registry(bundled / "backends" / "registry.json")
    if backend_key and backend_key not in registry:
        available = ", ".join(registry.keys()) or "无"
        raise ValueError(f"不支持的后端 '{backend_key}'。可用: {available}")

    try:
        # 3. 创建 .specforge/ 目录
        specforge_dir.mkdir(parents=True, exist_ok=True)

        # 4. 复制制品模板 (加 -template 后缀)
        templates_dir = specforge_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        for name in TEMPLATE_FILES:
            src = _get_template_source(plugins_root, content_type, name)
            if src is None:
                raise ValueError(f"模板文件缺失: {name}.md（内容类型 '{content_type}' 和 _default 均未找到）")
            dst = templates_dir / f"{name}-template.md"
            _copy_file(src, dst, files_created)

        # 5. 复制 constitution.md 到 .specforge/constitution.md
        constitution_src = _get_template_source(plugins_root, content_type, "constitution")
        if constitution_src is None:
            raise ValueError("宪法模板缺失: constitution.md")
        _copy_file(constitution_src, specforge_dir / "constitution.md", files_created)

        # 6. 生成 config.yaml
        config = RuntimeConfig(
            forge_version=__version__,
            project_version="0.1.0",
            content_type=content_type,
            backend=backend_key,
        )
        save_config(config, specforge_dir / "config.yaml")
        files_created.append(specforge_dir / "config.yaml")

        # 7. 按 output 类型分派安装
        if backend_key:
            backend = registry[backend_key]
            for output_cfg in backend.outputs:
                # 判断是否启用：skills 类型由 --ai-skills 控制，其他类型由 enabled 字段控制
                enabled = output_cfg.enabled
                if output_cfg.type == "skills":
                    enabled = ai_skills

                if not enabled:
                    continue

                installer = OUTPUT_INSTALLERS.get(output_cfg.type)
                if installer is None:
                    warnings.append(f"未知的输出类型 '{output_cfg.type}'，默认使用命令安装器")
                    installer = _install_commands

                installer(project_dir, backend, output_cfg, content_type, plugins_root,
                          files_created, warnings)

    except Exception:
        rollback(files_created)
        raise

    return result
