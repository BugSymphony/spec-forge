# setup 命令集成测试
import pytest
from click.testing import CliRunner
from forge.cli.main import main


class TestSetupCommand:
    def test_setup_plan_no_project(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "plan"], obj={})
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_setup_tasks_no_project(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "tasks"], obj={})
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_setup_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--help"], obj={})
        assert result.exit_code == 0
        assert "初始化 SDD 阶段环境" in result.output
