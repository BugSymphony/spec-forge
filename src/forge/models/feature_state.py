# FeatureState 模型 — .specforge/state.yaml 读写
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FeatureState:
    """状态管理器持久化的核心实体"""
    current_feature: Optional[str] = None
    version: int = 1


def load_state(project_root: Path) -> FeatureState:
    """从 .specforge/state.yaml 读取状态，文件不存在时返回默认值"""
    state_file = project_root / ".specforge" / "state.yaml"
    if not state_file.is_file():
        return FeatureState()
    try:
        data = yaml.safe_load(state_file.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        raise StateFileCorruptedError(f"状态文件格式损坏: {state_file}")
    version = data.get("version", 1)
    if version != 1:
        raise StateFileCorruptedError(
            f"不支持的状态文件版本: {version}（当前支持版本: 1）"
        )
    return FeatureState(
        current_feature=data.get("current_feature"),
        version=version,
    )


def save_state(project_root: Path, state: FeatureState) -> None:
    """原子写入 state.yaml（先写临时文件再 rename）"""
    state_dir = project_root / ".specforge"
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "state.yaml"
    tmp_file = state_dir / ".state.yaml.tmp"

    data = {"current_feature": state.current_feature, "version": state.version}
    tmp_file.write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    tmp_file.replace(state_file)


class StateFileCorruptedError(Exception):
    """state.yaml 格式损坏或版本不兼容"""
    pass
