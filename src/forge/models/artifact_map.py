# ArtifactMap 常量 — 8 阶段累积校验 artifact 清单
from dataclasses import dataclass


@dataclass
class Artifact:
    """单个制品文件/目录"""
    name: str                        # 制品标识名（如 spec、plan、tasks）
    path: str                        # 相对 FEATURE_DIR 的路径（如 spec.md、build/contracts/）
    required: bool = True            # 是否为必需 artifact
    is_dir: bool = False             # 是否为目录 artifact
    stage: str = ""                  # 所属阶段

    def __hash__(self):
        return hash((self.name, self.path, self.stage))


# 8 阶段累积校验 artifact 清单
ARTIFACT_MAP: dict[str, list[Artifact]] = {
    "constitution": [
        Artifact("constitution", ".specforge/constitution.md", required=True, stage="constitution"),
    ],
    "specify": [
        Artifact("spec", "spec.md", required=True, stage="specify"),
    ],
    "clarify": [
        # 纯流程阶段，无 artifact
    ],
    "checklist": [
        Artifact("checklists", "checklists/", required=False, is_dir=True, stage="checklist"),
    ],
    "plan": [
        Artifact("plan", "plan.md", required=True, stage="plan"),
        Artifact("build", "build/", required=True, is_dir=True, stage="plan"),
    ],
    "tasks": [
        Artifact("tasks", "tasks.md", required=True, stage="tasks"),
    ],
    "analyze": [
        # 纯流程阶段，无 artifact
    ],
    "implement": [
        # 完整校验，等同于 tasks 阶段
    ],
}

STAGE_ORDER = [
    "constitution", "specify", "clarify", "checklist",
    "plan", "tasks", "analyze", "implement",
]
