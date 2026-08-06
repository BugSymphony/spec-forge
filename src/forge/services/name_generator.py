# 名称生成器 — 短名提取 + 编号计算
import re
import datetime
from pathlib import Path


# 英文停用词列表（参考 create-new-feature.sh）
_STOP_WORDS = {
    "i", "a", "an", "the", "to", "for", "of", "in", "on", "at", "by",
    "with", "from", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "could", "can", "may", "might", "must", "shall", "this", "that",
    "these", "those", "my", "your", "our", "their", "want", "need",
    "add", "get", "set",
}


def generate_short_name(description: str) -> str:
    """从 description 自动提取短名"""
    # 检测是否主要为中文
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', description)
    if len(chinese_chars) >= 3 and len(chinese_chars) >= len(description) * 0.5:
        # 中文为主 → 取前 2-4 个中文字符
        short = "".join(chinese_chars[:4])
        return short if len(short) >= 2 else description[:4]

    # 英文处理：小写 → 去标点 → 过滤停用词 → ≥3 字符词 → 取 3-4 词
    clean = re.sub(r'[^a-z0-9]', ' ', description.lower())
    words = [w for w in clean.split() if w]
    meaningful = []
    for w in words:
        if w in _STOP_WORDS or len(w) < 3:
            # 检查是否为原始文本中的大写缩写
            if re.search(rf'\b{w.upper()}\b', description):
                meaningful.append(w.lower())
        else:
            meaningful.append(w)
    if meaningful:
        max_words = 4 if len(meaningful) >= 4 else 3
        result = "-".join(meaningful[:max_words])
        return result[:40].rstrip("-") if len(result) > 40 else result

    # 回退：取前 3 个非空词
    fallback = [w for w in words if w][:3]
    if fallback:
        return "-".join(fallback)[:40]
    return "feature"


def compute_next_number(specs_dir: Path) -> int:
    """顺序编号：检查 specs/ 已有目录，取最大编号 + 1"""
    if not specs_dir.is_dir():
        return 1
    highest = 0
    for child in specs_dir.iterdir():
        if not child.is_dir():
            continue
        m = re.match(r'^(\d{3,})-', child.name)
        if not m:
            continue
        # 跳过时间戳格式
        if re.match(r'^\d{8}-\d{6}-', child.name):
            continue
        num = int(m.group(1))
        if num > highest:
            highest = num
    return highest + 1


def build_dir_name(prefix: str, short_name: str) -> str:
    """拼接目录名：<prefix>-<short_name>"""
    return f"{prefix}-{short_name}"


def generate_timestamp_prefix() -> str:
    """生成时间戳前缀 YYYYMMDD-HHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def validate_short_name(name: str) -> str:
    """校验并清理短名：去特殊字符、转小写"""
    name = re.sub(r'\s+', '-', name)  # 空格 → 连字符
    name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff-]', '', name)
    name = re.sub(r'-{2,}', '-', name)
    name = name.strip('-')
    return name.lower() if name.isascii() or not re.search(r'[\u4e00-\u9fff]', name) else name
