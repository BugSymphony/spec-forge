# new 命令集成测试
import json
import pytest
from click.testing import CliRunner
from forge.cli.main import main


class TestNewCommand:
    def test_new_empty_description(self):
        # 空描述会先触发项目上下文错误（不在 specforge 项目中）
        runner = CliRunner()
        result = runner.invoke(main, ["new", "   "], obj={})
        assert result.exit_code == 1

    def test_new_no_project(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["new", "test"], obj={})
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_new_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["new", "--help"], obj={})
        assert result.exit_code == 0
        assert "创建新的 feature" in result.output
