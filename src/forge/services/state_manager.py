# 状态管理器 — 持久化当前活动 feature 到 .specforge/state.yaml
import sys
from pathlib import Path
from typing import Optional

from forge.models.feature_state import (
    FeatureState, StateFileCorruptedError, load_state, save_state,
)
from forge.models.project import find_project_root


class StateManager:
    """Feature 状态管理器"""

    def __init__(self, project_root: Path):
        self._project_root = project_root

    def get_current_feature(self) -> Optional[str]:
        """获取当前活动 feature 的目录名（如 '002-payment'），含目录存在性校验"""
        try:
            state = load_state(self._project_root)
        except StateFileCorruptedError as e:
            raise StateFileCorruptedError(str(e))
        name = state.current_feature
        if name is not None:
            feature_dir = self._project_root / "specs" / name
            if not feature_dir.is_dir():
                self.clear_current_feature()
                print(f"提示: 活动 feature '{name}' 目录不存在，已自动清除", file=sys.stderr)
                return None
        return name

    def set_current_feature(self, feature_name: str) -> None:
        """设置当前活动 feature（feature_name 不含 specs/ 前缀）"""
        feature_dir = self._project_root / "specs" / feature_name
        if not feature_dir.is_dir():
            raise FeatureNotFoundError(f"feature 目录不存在: specs/{feature_name}")
        state = FeatureState(current_feature=feature_name)
        save_state(self._project_root, state)

    def clear_current_feature(self) -> None:
        """清空当前活动 feature"""
        state = FeatureState(current_feature=None)
        save_state(self._project_root, state)


class FeatureNotFoundError(Exception):
    """feature 目录不存在"""
    pass
