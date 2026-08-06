# artifact 校验器单元测试
import pytest
from pathlib import Path
from forge.services.artifact_validator import validate_stage, ValidateResult


class TestArtifactValidator:
    def test_validate_constitution_pass(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        (tmp_path / "specs" / "test-feature").mkdir(parents=True)
        result = validate_stage(tmp_path / "specs" / "test-feature", "constitution", tmp_path)
        assert result.passed
        assert result.missing == []

    def test_validate_constitution_fail(self, tmp_path):
        (tmp_path / "specs" / "test-feature").mkdir(parents=True)
        result = validate_stage(tmp_path / "specs" / "test-feature", "constitution", tmp_path)
        assert not result.passed
        assert ".specforge/constitution.md" in result.missing

    def test_validate_specify(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        result = validate_stage(feature_dir, "specify", tmp_path)
        assert result.passed

    def test_validate_plan(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        (feature_dir / "plan.md").write_text("...")
        (feature_dir / "build").mkdir()
        result = validate_stage(feature_dir, "plan", tmp_path)
        assert result.passed
        assert len(result.missing) == 0

    def test_validate_plan_missing_build(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        (feature_dir / "plan.md").write_text("...")
        result = validate_stage(feature_dir, "plan", tmp_path)
        assert not result.passed
        assert "build/" in result.missing

    def test_validate_plan_not_checking_build_internals(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        (feature_dir / "plan.md").write_text("...")
        (feature_dir / "build").mkdir()
        result = validate_stage(feature_dir, "plan", tmp_path)
        assert result.passed

    def test_validate_clarify(self, tmp_path):
        # clarify 无新增 artifact，但累积校验仍需前序阶段全部通过
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        result = validate_stage(feature_dir, "clarify", tmp_path)
        assert result.passed

    def test_validate_tasks(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        (feature_dir / "plan.md").write_text("...")
        (feature_dir / "build").mkdir()
        (feature_dir / "tasks.md").write_text("...")
        result = validate_stage(feature_dir, "tasks", tmp_path)
        assert result.passed

    def test_validate_tasks_missing(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        (feature_dir / "plan.md").write_text("...")
        (feature_dir / "build").mkdir()
        result = validate_stage(feature_dir, "tasks", tmp_path)
        assert not result.passed
        assert "tasks.md" in result.missing

    def test_validate_checklist_warning(self, tmp_path):
        (tmp_path / ".specforge").mkdir()
        (tmp_path / ".specforge" / "constitution.md").write_text("...")
        feature_dir = tmp_path / "specs" / "test-feature"
        feature_dir.mkdir(parents=True)
        (feature_dir / "spec.md").write_text("...")
        result = validate_stage(feature_dir, "checklist", tmp_path)
        assert result.passed
        assert "checklists/" in result.warnings

    def test_validate_invalid_stage(self, tmp_path):
        result = validate_stage(tmp_path, "invalid", tmp_path)
        assert not result.passed
