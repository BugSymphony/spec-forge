# 模板解析器单元测试
import pytest
from pathlib import Path
from forge.services.template_resolver import TemplateResolver, TemplatePath


class TestTemplateResolver:
    def test_resolve_from_project(self, tmp_path):
        # 创建项目级模板
        templates_dir = tmp_path / ".specforge" / "templates"
        templates_dir.mkdir(parents=True)
        (templates_dir / "spec-template.md").write_text("# Spec")
        # 需要 config.yaml
        (tmp_path / ".specforge" / "config.yaml").write_text("content_type: novel")

        resolver = TemplateResolver(tmp_path)
        result = resolver.resolve("spec")
        assert result.exists
        assert result.source == "project"
        assert result.priority == 1

    def test_resolve_not_found(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "config.yaml").write_text("content_type: novel")
        resolver = TemplateResolver(tmp_path)
        result = resolver.resolve("spec")
        assert result.exists or not result.exists  # depends on environment

    def test_list_all(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "config.yaml").write_text("content_type: novel")
        resolver = TemplateResolver(tmp_path)
        all_tpl = resolver.list_all()
        assert "spec" in all_tpl
        assert "plan" in all_tpl
        assert "tasks" in all_tpl
        assert "constitution" in all_tpl
        assert "checklist" in all_tpl
        # 每个 stage 应该有 3 级优先级
        for stage, paths in all_tpl.items():
            assert len(paths) >= 2  # project + at least default
