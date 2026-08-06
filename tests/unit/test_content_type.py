"""Tests for content_type.py plugin discovery with plugin.yaml and extra_roots."""
import pytest
import yaml
from pathlib import Path
from forge.models.content_type import discover_plugins, ContentType


def _make_plugin_dir(parent: Path, name: str, meta: dict | None = None,
                      has_templates: bool = True, has_commands: bool = True) -> Path:
    """Helper to create a minimal plugin directory."""
    plugin_dir = parent / name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    if meta is not None:
        (plugin_dir / "plugin.yaml").write_text(yaml.dump(meta), encoding="utf-8")
    if has_templates:
        (plugin_dir / "templates").mkdir(exist_ok=True)
    if has_commands:
        (plugin_dir / "commands").mkdir(exist_ok=True)
    return plugin_dir


class TestDiscoverPluginsMeta:

    def test_parses_plugin_yaml(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "name_cn": "小说", "description": "长篇创作"})
        types = discover_plugins(tmp_path)
        assert "novel" in types
        assert types["novel"].name_cn == "小说"
        assert types["novel"].description == "长篇创作"

    def test_falls_back_without_plugin_yaml(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", None)
        types = discover_plugins(tmp_path)
        assert "novel" in types
        assert types["novel"].name_cn == "novel"
        assert types["novel"].description == ""

    def test_key_mismatch_exits(self, tmp_path):
        _make_plugin_dir(tmp_path, "game", {"key": "gaming", "name_cn": "游戏"})
        with pytest.raises(ValueError):
            discover_plugins(tmp_path)

    def test_skips_hidden_dirs(self, tmp_path):
        _make_plugin_dir(tmp_path, "_default", {"key": "_default", "name_cn": "默认"})
        types = discover_plugins(tmp_path)
        assert "_default" not in types

    def test_skips_missing_templates(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "name_cn": "小说"}, has_templates=False)
        types = discover_plugins(tmp_path)
        assert "novel" not in types

    def test_skips_missing_commands(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "name_cn": "小说"}, has_commands=False)
        types = discover_plugins(tmp_path)
        assert "novel" not in types

    def test_name_cn_optional(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "description": "desc"})
        types = discover_plugins(tmp_path)
        assert types["novel"].name_cn == "novel"


class TestDiscoverPluginsExtraRoots:

    def test_extra_roots_merged(self, tmp_path):
        internal = tmp_path / "internal"
        internal.mkdir()
        _make_plugin_dir(internal, "novel", {"key": "novel", "name_cn": "内建小说"})

        external = tmp_path / "external"
        external.mkdir()
        _make_plugin_dir(external, "game", {"key": "game", "name_cn": "游戏"})

        types = discover_plugins(internal, extra_roots=[external])
        assert "novel" in types
        assert "game" in types
        assert len(types) == 2

    def test_extra_roots_external_overrides(self, tmp_path):
        internal = tmp_path / "internal"
        internal.mkdir()
        _make_plugin_dir(internal, "novel", {"key": "novel", "name_cn": "内建小说"})

        external = tmp_path / "external"
        external.mkdir()
        _make_plugin_dir(external, "novel", {"key": "novel", "name_cn": "外部小说"})

        types = discover_plugins(internal, extra_roots=[external])
        assert types["novel"].name_cn == "外部小说"

    def test_extra_roots_none_default(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "name_cn": "小说"})
        types = discover_plugins(tmp_path)
        assert "novel" in types
        assert len(types) == 1

    def test_extra_roots_missing_dir(self, tmp_path):
        _make_plugin_dir(tmp_path, "novel", {"key": "novel", "name_cn": "小说"})
        missing = tmp_path / "nonexistent"
        types = discover_plugins(tmp_path, extra_roots=[missing])
        assert "novel" in types
        assert len(types) == 1

    def test_empty_plugins_root(self, tmp_path):
        types = discover_plugins(tmp_path)
        assert len(types) == 0
