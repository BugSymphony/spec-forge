# pytest fixtures for SpecForge 测试
import tempfile
import json
import shutil
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project():
    """临时项目目录，测试后自动清理"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_registry():
    """测试用后端注册表"""
    return {
        "backends": [
            {
                "key": "opencode",
                "name": "OpenCode",
                "detect_type": "cli",
                "detect_cmd": "opencode",
                "command_prefix": "specforge",
                "outputs": [
                    {"type": "slash_commands", "dir": ".opencode/commands", "invoke_separator": "."}
                ]
            },
            {
                "key": "cursor",
                "name": "Cursor",
                "detect_type": "cli",
                "detect_cmd": "cursor",
                "command_prefix": "specforge",
                "outputs": [
                    {"type": "rules", "dir": ".cursor/rules", "invoke_separator": "-"}
                ]
            },
            {
                "key": "claude_code",
                "name": "Claude Code",
                "detect_type": "ide",
                "detect_cmd": "",
                "command_prefix": "specforge",
                "outputs": [
                    {"type": "slash_commands", "dir": ".claude/commands", "invoke_separator": "."}
                ]
            },
        ]
    }


@pytest.fixture
def sample_registry_file(tmp_path, sample_registry):
    """写入临时 registry.json 并返回路径"""
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(sample_registry, ensure_ascii=False, indent=2))
    return path


@pytest.fixture
def sample_plugin_root(tmp_path):
    """创建最小插件目录结构用于测试"""
    plugins = tmp_path / "plugins"
    # _default 插件
    default = plugins / "_default"
    default.joinpath("templates").mkdir(parents=True)
    default.joinpath("commands").mkdir(parents=True)
    # novel 插件
    novel = plugins / "novel"
    novel.joinpath("templates").mkdir(parents=True)
    novel.joinpath("commands").mkdir(parents=True)
    return plugins
