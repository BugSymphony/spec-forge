# Feature 扫描器单元测试
import pytest
from pathlib import Path
from forge.services.feature_scanner import FeatureScanner, AmbiguousFeatureError, FeatureNotFoundError


class TestFeatureScanner:
    def test_scan_empty(self, tmp_path):
        scanner = FeatureScanner(tmp_path)
        assert scanner.scan() == []

    def test_scan_features(self, tmp_path):
        (tmp_path / "specs" / "001-core").mkdir(parents=True)
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        (tmp_path / "specs" / "not-a-feature").mkdir(parents=True)
        scanner = FeatureScanner(tmp_path)
        records = scanner.scan(active_feature="002-payment")
        assert len(records) == 3
        assert records[0].name == "001-core"
        assert records[0].number == 1
        assert not records[0].is_active
        assert records[1].name == "002-payment"
        assert records[1].is_active

    def test_resolve_exact(self, tmp_path):
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        scanner = FeatureScanner(tmp_path)
        assert scanner.resolve("002-payment") == "002-payment"

    def test_resolve_suffix(self, tmp_path):
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        scanner = FeatureScanner(tmp_path)
        assert scanner.resolve("payment") == "002-payment"

    def test_resolve_prefix(self, tmp_path):
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        (tmp_path / "specs" / "001-core").mkdir(parents=True)
        scanner = FeatureScanner(tmp_path)
        assert scanner.resolve("2") == "002-payment"
        assert scanner.resolve("1") == "001-core"

    def test_resolve_ambiguous(self, tmp_path):
        specs = tmp_path / "specs"
        specs.mkdir()
        (specs / "002-payment").mkdir()
        (specs / "003-payment").mkdir()  # both end with -payment
        scanner = FeatureScanner(tmp_path)
        with pytest.raises(AmbiguousFeatureError):
            scanner.resolve("payment")

    def test_resolve_not_found(self, tmp_path):
        scanner = FeatureScanner(tmp_path)
        with pytest.raises(FeatureNotFoundError):
            scanner.resolve("nonexistent")

    def test_exists(self, tmp_path):
        (tmp_path / "specs" / "002-payment").mkdir(parents=True)
        scanner = FeatureScanner(tmp_path)
        assert scanner.exists("002-payment")
        assert not scanner.exists("nonexistent")
