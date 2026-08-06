# 状态管理器单元测试
import pytest
import yaml
from pathlib import Path
from forge.models.feature_state import load_state, save_state, FeatureState, StateFileCorruptedError
from forge.services.state_manager import StateManager, FeatureNotFoundError


class TestFeatureState:
    def test_load_default_when_file_missing(self, tmp_path):
        state = load_state(tmp_path)
        assert state.current_feature is None
        assert state.version == 1

    def test_save_and_load(self, tmp_path):
        state = FeatureState(current_feature="002-payment")
        save_state(tmp_path, state)
        loaded = load_state(tmp_path)
        assert loaded.current_feature == "002-payment"

    def test_load_corrupted_yaml(self, tmp_path):
        state_dir = tmp_path / ".specforge"
        state_dir.mkdir()
        (state_dir / "state.yaml").write_text("\t\t::: not valid yaml \x00")
        with pytest.raises(StateFileCorruptedError, match="格式损坏"):
            load_state(tmp_path)

    def test_load_unsupported_version(self, tmp_path):
        state_dir = tmp_path / ".specforge"
        state_dir.mkdir()
        (state_dir / "state.yaml").write_text(yaml.dump({"version": 99, "current_feature": "test"}))
        with pytest.raises(StateFileCorruptedError, match="不支持的状态文件版本"):
            load_state(tmp_path)

    def test_atomic_write(self, tmp_path):
        state = FeatureState(current_feature="test")
        save_state(tmp_path, state)
        assert (tmp_path / ".specforge" / "state.yaml").is_file()
        # tmp file should be cleaned up
        assert not (tmp_path / ".specforge" / ".state.yaml.tmp").is_file()


class TestStateManager:
    def test_get_current_feature_empty(self, tmp_path):
        manager = StateManager(tmp_path)
        assert manager.get_current_feature() is None

    def test_set_and_get(self, tmp_path):
        # 创建 feature 目录
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        manager = StateManager(tmp_path)
        manager.set_current_feature("002-payment")
        assert manager.get_current_feature() == "002-payment"

    def test_set_nonexistent(self, tmp_path):
        manager = StateManager(tmp_path)
        with pytest.raises(FeatureNotFoundError):
            manager.set_current_feature("nonexistent")

    def test_get_with_deleted_directory(self, tmp_path):
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        manager = StateManager(tmp_path)
        manager.set_current_feature("002-payment")
        # 删除目录
        import shutil
        shutil.rmtree(tmp_path / "specs" / "002-payment")
        # 应该自动清除
        assert manager.get_current_feature() is None
