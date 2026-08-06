# Feature CLI 集成测试
import json
import pytest
from click.testing import CliRunner
from forge.cli.main import main


class TestListCommand:
    def test_list_no_project(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["list"], obj={})
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_list_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["list", "--help"], obj={})
        assert result.exit_code == 0
        assert "列出所有" in result.output


class TestShowCommand:
    def test_show_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["show", "--help"], obj={})
        assert result.exit_code == 0
        assert "paths-only" in result.output


class TestUseCommand:
    def test_use_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["use", "--help"], obj={})
        assert result.exit_code == 0
        assert "切换活动 feature" in result.output
