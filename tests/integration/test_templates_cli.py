# templates 命令集成测试
import pytest
from click.testing import CliRunner
from forge.cli.main import main


class TestTemplatesCommand:
    def test_templates_no_project(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(main, ["templates"], obj={})
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_templates_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["templates", "--help"], obj={})
        assert result.exit_code == 0
        assert "按阶段分组" in result.output
