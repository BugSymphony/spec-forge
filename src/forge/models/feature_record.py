# FeatureRecord 模型 — feature 扫描结果
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class FeatureRecord:
    """单个 feature 的运行时记录"""
    name: str                                  # feature 目录全名（如 002-payment）
    path: Path                                 # 完整文件系统路径
    number: Optional[int] = None               # 编号前缀（timestamp 模式为 None）
    prefix_type: str = "sequential"            # sequential 或 timestamp
    artifacts: dict = field(default_factory=dict)  # 各关键 artifact 存在状态
    is_active: bool = False                    # 是否为当前活动 feature

    @staticmethod
    def _extract_number(dirname: str) -> Optional[int]:
        """从目录名提取编号前缀"""
        m = re.match(r'^(\d+)-', dirname)
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def _detect_prefix_type(dirname: str) -> str:
        """检测编号类型"""
        if re.match(r'^\d{8}-\d{6}-', dirname):
            return "timestamp"
        return "sequential"
