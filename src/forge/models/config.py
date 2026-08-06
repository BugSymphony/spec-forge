# RuntimeConfig 模型 — .specforge/config.yaml 读写
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RuntimeConfig:
    """运行时项目配置文件（.specforge/config.yaml）"""
    forge_version: str = "0.1.0"
    project_version: str = "0.1.0"
    content_type: str = ""
    backend: Optional[str] = None


def load_config(path: Path) -> RuntimeConfig:
    """从 .specforge/config.yaml 读取配置"""
    if not path.is_file():
        return RuntimeConfig()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return RuntimeConfig(
        forge_version=data.get("forge_version", "0.1.0"),
        project_version=data.get("project_version", "0.1.0"),
        content_type=data.get("content_type", ""),
        backend=data.get("backend"),
    )


def save_config(config: RuntimeConfig, path: Path):
    """将配置写入 .specforge/config.yaml"""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "forge_version": config.forge_version,
        "project_version": config.project_version,
        "content_type": config.content_type,
        "backend": config.backend,
    }
    path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")
