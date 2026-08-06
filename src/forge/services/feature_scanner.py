# Feature 扫描器 — specs/ 目录扫描 + 三级匹配
import re
from pathlib import Path
from typing import Optional

from forge.models.feature_record import FeatureRecord

# 关键 artifact 检查清单（用于 list --detail 和 FeatureRecord）
_DETAIL_ARTIFACTS = [
    ("constitution", ".specforge/constitution.md"),
    ("spec", "spec.md"),
    ("plan", "plan.md"),
    ("tasks", "tasks.md"),
]

# 全量 artifact 检查清单（用于 show 默认输出）
_FULL_ARTIFACTS = [
    (".specforge/constitution.md", False),
    ("spec.md", False),
    ("plan.md", False),
    ("build/", True),
    ("build/research.md", False),
    ("build/data-model.md", False),
    ("build/contracts/", True),
    ("build/quickstart.md", False),
    ("tasks.md", False),
    ("checklists/", True),
]


class FeatureScanner:
    """Feature 扫描器"""

    def __init__(self, project_root: Path):
        self._project_root = project_root

    @property
    def specs_dir(self) -> Path:
        return self._project_root / "specs"

    def scan(self, active_feature: Optional[str] = None) -> list[FeatureRecord]:
        """扫描 specs/ 目录返回所有 feature"""
        specs = self.specs_dir
        if not specs.is_dir():
            return []
        records = []
        for child in sorted(specs.iterdir()):
            if not child.is_dir():
                continue
            name = child.name
            record = FeatureRecord(
                name=name,
                path=child,
                number=FeatureRecord._extract_number(name),
                prefix_type=FeatureRecord._detect_prefix_type(name),
                artifacts=self._scan_artifacts(child),
                is_active=(name == active_feature),
            )
            records.append(record)
        return records

    def _scan_artifacts(self, feature_dir: Path) -> dict:
        """扫描单个 feature 的 artifact 存在状态"""
        result = {}
        for art_path, is_dir in _FULL_ARTIFACTS:
            full_path = feature_dir / art_path
            # .specforge/constitution.md 使用项目级路径
            if art_path.startswith(".specforge"):
                full_path = self._project_root / art_path
            if is_dir:
                result[art_path] = full_path.is_dir()
            else:
                result[art_path] = full_path.is_file()
        return result

    def resolve(self, user_input: str) -> str:
        """三级匹配：精确全名 → 短名后缀 → 编号前缀 → 返回 feature 目录名"""
        all_names = self._list_feature_names()

        # 1. 精确全名匹配
        if user_input in all_names:
            return user_input

        # 2. 短名后缀匹配
        suffix_matches = [
            n for n in all_names
            if "-" in n and n.split("-", 1)[1] == user_input
        ]
        if len(suffix_matches) == 1:
            return suffix_matches[0]
        if len(suffix_matches) > 1:
            raise AmbiguousFeatureError(user_input, suffix_matches)

        # 3. 编号前缀匹配
        try:
            num = int(user_input)
            prefix_matches = [
                n for n in all_names
                if FeatureRecord._extract_number(n) == num
            ]
            if len(prefix_matches) == 1:
                return prefix_matches[0]
            if len(prefix_matches) > 1:
                raise AmbiguousFeatureError(user_input, prefix_matches)
        except ValueError:
            pass

        raise FeatureNotFoundError(user_input)

    def exists(self, name: str) -> bool:
        """检查 feature 目录是否存在"""
        return (self.specs_dir / name).is_dir()

    def get_detail_stages(self, feature_dir: Path, project_root: Path) -> dict:
        """获取 4 阶段摘要（用于 list --detail）"""
        result = {}
        for stage, art_path in _DETAIL_ARTIFACTS:
            if stage == "constitution":
                full_path = project_root / art_path
            else:
                full_path = feature_dir / art_path
            result[stage] = full_path.is_file() if not art_path.endswith("/") else full_path.is_dir()
        return result

    def _list_feature_names(self) -> list[str]:
        """列出所有 feature 目录名"""
        specs = self.specs_dir
        if not specs.is_dir():
            return []
        return sorted([d.name for d in specs.iterdir() if d.is_dir()])


class FeatureNotFoundError(Exception):
    """feature 未找到"""
    def __init__(self, query: str):
        self.query = query
        super().__init__(f"未找到 feature '{query}'")


class AmbiguousFeatureError(Exception):
    """匹配到多个 feature"""
    def __init__(self, query: str, matches: list[str]):
        self.query = query
        self.matches = matches
        msg = f"'{query}' 匹配到多个 feature: {', '.join(matches)}。请指定完整名称"
        super().__init__(msg)
