# ContentType 模型 — 内容类型插件发现
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ContentType:
    """内容类型插件定义，通过扫描 plugins/ 目录自动发现"""
    key: str
    name: str
    name_cn: str = ""
    description: str = ""


def _read_plugin_metadata(plugin_dir: Path) -> dict | None:
    """读取 plugin.yaml 元数据"""
    meta_file = plugin_dir / "plugin.yaml"
    if not meta_file.is_file():
        return None
    try:
        data = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return None
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"插件元数据文件格式不合法: {meta_file}\n  {e}")


def _scan_plugins_root(plugins_root: Path) -> dict[str, ContentType]:
    """扫描单个插件集合根目录，返回已发现的内容类型字典"""
    types: dict[str, ContentType] = {}
    if not plugins_root.is_dir():
        return types

    for entry in sorted(plugins_root.iterdir()):
        if not entry.is_dir():
            continue
        # 跳过 _default 和隐藏目录
        if entry.name.startswith("_") or entry.name.startswith("."):
            continue
        # 必须包含 templates/ 和 commands/ 才视为合法内容类型
        tmpl = entry / "templates"
        cmds = entry / "commands"
        if not (tmpl.is_dir() and cmds.is_dir()):
            continue

        name_cn = entry.name
        description = ""

        # 尝试读取 plugin.yaml
        meta = _read_plugin_metadata(entry)
        if meta is None:
            # 无 plugin.yaml：使用目录名作为默认值（过渡/回退兼容）
            types[entry.name] = ContentType(key=entry.name, name=entry.name, name_cn=entry.name, description="")
            continue

        meta_key = meta.get("key", "")
        if meta_key != entry.name:
            raise ValueError(f"插件目录名 '{entry.name}' 与 plugin.yaml 中的 key '{meta_key}' 不一致")

        name_cn = meta.get("name_cn", entry.name)
        description = meta.get("description", "")

        types[entry.name] = ContentType(
            key=entry.name,
            name=entry.name,
            name_cn=name_cn,
            description=description,
        )

    return types


def discover_plugins(plugins_root: Path, extra_roots: list[Path] | None = None) -> dict[str, ContentType]:
    """扫描 plugins/ 目录及可选的外部目录，返回已发现的内容类型字典

    多个来源存在同名插件时，外部目录优先。
    """
    if extra_roots is None:
        extra_roots = []

    # 先扫描内建目录
    merged: dict[str, ContentType] = _scan_plugins_root(plugins_root)

    # 再扫描外部目录，外部覆盖内建
    for root in extra_roots:
        if not root.is_dir():
            continue
        external = _scan_plugins_root(root)
        for key, ct in external.items():
            merged[key] = ct

    return merged
