# BackendAdapter 模型 — 后端注册表解析
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OutputConfig:
    """后端输出介质配置"""
    type: str              # slash_commands / rules / skills / custom
    dir: str               # 输出目录相对路径
    invoke_separator: str  # 文件名分隔符：slash_commands 用 .，rules/skills 用 -
    enabled: bool = True   # 是否默认输出（skills 默认关闭，需 --ai-skills 启用）


@dataclass
class BackendAdapter:
    """AI 编码助手后端注册信息"""
    key: str
    name: str
    detect_type: str           # cli / ide
    detect_cmd: str            # CLI 检测命令，仅 detect_type=cli 时有效
    command_prefix: str        # 命令文件前缀（固定 specforge）
    outputs: list[OutputConfig] = field(default_factory=list)


def load_registry(registry_path: Path) -> dict[str, BackendAdapter]:
    """解析 backends/registry.json，返回后端字典"""
    if not registry_path.is_file():
        return {}

    data = json.loads(registry_path.read_text(encoding="utf-8"))
    backends: dict[str, BackendAdapter] = {}

    for item in data.get("backends", []):
        key = item["key"]
        outputs = [
            OutputConfig(
                type=o["type"],
                dir=o["dir"],
                invoke_separator=o["invoke_separator"],
                enabled=o.get("enabled", True),
            )
            for o in item.get("outputs", [])
        ]
        backends[key] = BackendAdapter(
            key=key,
            name=item["name"],
            detect_type=item["detect_type"],
            detect_cmd=item.get("detect_cmd", ""),
            command_prefix=item["command_prefix"],
            outputs=outputs,
        )

    return backends
