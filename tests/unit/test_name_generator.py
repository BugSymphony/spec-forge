# 名称生成器单元测试
import pytest
from pathlib import Path
from forge.services.name_generator import (
    generate_short_name, compute_next_number, build_dir_name,
    generate_timestamp_prefix, validate_short_name,
)


class TestNameGenerator:
    def test_generate_short_name_english(self):
        short = generate_short_name("Add user authentication system")
        assert "user" in short
        assert "authentication" in short
        assert len(short.split("-")) <= 4

    def test_generate_short_name_chinese(self):
        short = generate_short_name("添加用户认证功能")
        assert len(short) >= 2
        assert len(short) <= 4

    def test_generate_short_name_filter_stop_words(self):
        short = generate_short_name("I want to build a new feature")
        assert "want" not in short
        assert "add" not in short  # "add" is in stop words
        assert "feature" in short or "build" in short

    def test_compute_next_number_empty(self, tmp_path):
        assert compute_next_number(tmp_path) == 1

    def test_compute_next_number_existing(self, tmp_path):
        (tmp_path / "001-core").mkdir()
        (tmp_path / "002-payment").mkdir()
        (tmp_path / "005-later").mkdir()
        # 添加非匹配目录
        (tmp_path / "not-a-feature").mkdir()
        assert compute_next_number(tmp_path) == 6

    def test_compute_next_number_skips_timestamp(self, tmp_path):
        (tmp_path / "001-core").mkdir()
        (tmp_path / "20260529-120000-something").mkdir()
        assert compute_next_number(tmp_path) == 2

    def test_build_dir_name(self):
        assert build_dir_name("002", "payment") == "002-payment"
        assert build_dir_name("20260529-120000", "fix") == "20260529-120000-fix"

    def test_timestamp_format(self):
        ts = generate_timestamp_prefix()
        assert len(ts) == 15
        assert ts[8] == '-'

    def test_validate_short_name(self):
        # validate_short_name 只保留 a-zA-Z0-9 中文和 -
        assert validate_short_name("User Auth") == "user-auth"
        assert validate_short_name("test--name") == "test-name"
        assert validate_short_name("---hello---") == "hello"
        # 空格转 -
        result = validate_short_name("user auth")
        assert "user" in result and "auth" in result

    def test_validate_short_name_chinese(self):
        result = validate_short_name("支付功能")
        assert "支付" in result or "付功能" in result or result == "支付功能"
