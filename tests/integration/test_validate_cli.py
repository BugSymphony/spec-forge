# validate 命令集成测试
import json
import pytest
from click.testing import CliRunner
from forge.cli.main import main


class TestValidateCommand:
    def test_validate_no_project(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            main, ["validate", "001-test", "--stage", "constitution"], obj={}
        )
        assert result.exit_code == 1
        assert "不是 SpecForge 项目" in result.output

    def test_validate_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["validate", "--help"], obj={})
        assert result.exit_code == 0
        assert "校验 feature" in result.output
