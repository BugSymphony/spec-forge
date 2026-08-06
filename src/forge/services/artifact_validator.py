# artifact 校验器 — 按 stage 累积校验 artifact 完整性
from pathlib import Path

from forge.models.artifact_map import ARTIFACT_MAP, STAGE_ORDER


class ValidateResult:
    """校验结果"""
    def __init__(self, stage: str, feature: str = None):
        self.stage = stage
        self.feature = feature
        self.passed = True
        self.artifacts = []        # list[{name, path, exists, required}]
        self.missing = []           # 缺失的 required artifact 名称
        self.warnings = []          # 缺失的非 required artifact 名称


def validate_stage(feature_dir: Path, stage: str, project_root: Path) -> ValidateResult:
    """按阶段累积校验 feature artifact 完整性"""
    if stage not in STAGE_ORDER:
        result = ValidateResult(stage)
        result.passed = False
        result.missing.append(f"无效的 stage: {stage}")
        return result

    result = ValidateResult(stage, feature=feature_dir.name)
    stage_index = STAGE_ORDER.index(stage)

    # 累积迭代到目标阶段
    checked_paths = set()
    for idx in range(stage_index + 1):
        s = STAGE_ORDER[idx]
        for art in ARTIFACT_MAP.get(s, []):
            # 避免重复检查同名 artifact
            if art.path in checked_paths:
                continue
            checked_paths.add(art.path)

            # 构建完整路径
            if art.path.startswith(".specforge"):
                full_path = project_root / art.path
            else:
                full_path = feature_dir / art.path

            exists = full_path.is_dir() if art.is_dir else full_path.is_file()

            result.artifacts.append({
                "name": art.name,
                "path": art.path,
                "exists": exists,
                "required": art.required,
            })

            if not exists:
                if art.required:
                    result.missing.append(art.path)
                    result.passed = False
                else:
                    result.warnings.append(art.path)

    return result
