"""Tests for _install_skills in scaffolding.py."""
import pytest
import yaml
from pathlib import Path

from forge.services.scaffolding import _install_skills, COMMAND_FILES
from forge.models.backend import BackendAdapter, OutputConfig


def _make_skills_output(skills_dir: str = ".test/skills", enabled: bool = True):
    return OutputConfig(type="skills", dir=skills_dir, invoke_separator="-", enabled=enabled)


def _make_backend(skills_dir: str = ".test/skills", with_skills: bool = True):
    """Helper to create a BackendAdapter with skills output."""
    outputs = [OutputConfig(type="slash_commands", dir=".test/commands", invoke_separator=".", enabled=True)]
    if with_skills:
        outputs.append(OutputConfig(type="skills", dir=skills_dir, invoke_separator="-", enabled=False))
    return BackendAdapter(
        key="testbe", name="TestBackend", detect_type="cli", detect_cmd="test",
        command_prefix="specforge", outputs=outputs,
    )


def _make_command_file(commands_dir: Path, name: str, frontmatter: dict | None = None, body: str = ""):
    """Helper to create a command .md file."""
    if frontmatter is None:
        frontmatter = {"description": f"{name} command"}
    fm_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{fm_text}\n---\n{body}\n"
    (commands_dir / f"{name}.md").write_text(content, encoding="utf-8")


class TestInstallSkills:

    def test_installs_skills(self, tmp_path):
        project_dir = tmp_path / "project"
        plugins_root = tmp_path / "plugins"
        cmd_dir = plugins_root / "_default" / "commands"
        cmd_dir.mkdir(parents=True)
        for name in COMMAND_FILES:
            _make_command_file(cmd_dir, name, body="Skill body")

        backend = _make_backend(".test/skills")
        output_cfg = _make_skills_output(".test/skills")
        files_created: list[Path] = []
        warnings: list[str] = []

        _install_skills(project_dir, backend, output_cfg, "novel", plugins_root, files_created, warnings)

        skills_dir = project_dir / ".test" / "skills"
        assert skills_dir.is_dir()
        for name in COMMAND_FILES:
            skill_file = skills_dir / f"specforge-{name}" / "SKILL.md"
            assert skill_file.is_file(), f"Missing {skill_file}"

    def test_skips_existing_skills(self, tmp_path):
        project_dir = tmp_path / "project"
        plugins_root = tmp_path / "plugins"
        cmd_dir = plugins_root / "_default" / "commands"
        cmd_dir.mkdir(parents=True)
        for name in COMMAND_FILES:
            _make_command_file(cmd_dir, name, body="body")

        backend = _make_backend(".test/skills")
        output_cfg = _make_skills_output(".test/skills")

        # Pre-create one skill
        skill_dir = project_dir / ".test" / "skills" / "specforge-specify"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("existing")

        files_created: list[Path] = []
        warnings: list[str] = []
        _install_skills(project_dir, backend, output_cfg, "novel", plugins_root, files_created, warnings)

        assert any("已存在" in w for w in warnings)

    def test_exits_on_missing_source(self, tmp_path):
        project_dir = tmp_path / "project"
        plugins_root = tmp_path / "plugins"
        cmd_dir = plugins_root / "_default" / "commands"
        cmd_dir.mkdir(parents=True)
        _make_command_file(cmd_dir, "specify", body="body")

        backend = _make_backend(".test/skills")
        output_cfg = _make_skills_output(".test/skills")
        files_created: list[Path] = []
        warnings: list[str] = []

        with pytest.raises(ValueError):
            _install_skills(project_dir, backend, output_cfg, "novel", plugins_root, files_created, warnings)

    def test_skill_uses_original_description(self, tmp_path):
        project_dir = tmp_path / "project"
        plugins_root = tmp_path / "plugins"
        cmd_dir = plugins_root / "_default" / "commands"
        cmd_dir.mkdir(parents=True)
        original_desc = "从自然语言描述创建功能规格说明"
        for name in COMMAND_FILES:
            desc = original_desc if name == "specify" else f"{name} description"
            _make_command_file(cmd_dir, name, {"description": desc}, body=f"Skill body for {name}")

        backend = _make_backend(".test/skills")
        output_cfg = _make_skills_output(".test/skills")
        files_created: list[Path] = []
        warnings: list[str] = []

        _install_skills(project_dir, backend, output_cfg, "novel", plugins_root, files_created, warnings)

        skill_file = project_dir / ".test" / "skills" / "specforge-specify" / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        assert "name: specforge-specify" in content
        assert "author: specforge" in content
        assert "Skill body for specify" in content
        # Original description IS preserved (no longer replaced by SKILL_DESCRIPTIONS)
        assert original_desc in content
