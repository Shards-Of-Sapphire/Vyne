from vyne.cli import _filter_findings_by_allowlist, run_audit
from vyne.scanners.scanners import ScannerRegistry
from vyne.scanners import dependency
from vyne.utils.config import ConfigManager
from vyne.utils.vdi import check_package


def test_registry_returns_one_flat_findings_list():
    registry = ScannerRegistry()
    registry.scanners = [
        lambda ast, code, path: [{"severity": "WARNING", "scanner": "test"}],
        lambda ast, code, path: [{"severity": "CRITICAL", "scanner": "test"}],
    ]

    findings = registry.run_all(None, "", "snippet.py")

    assert findings == [
        {"severity": "WARNING", "scanner": "test"},
        {"severity": "CRITICAL", "scanner": "test"},
    ]


def test_config_blocks_critical_by_default():
    config = ConfigManager("missing-vyne-config.yaml")

    assert config.get_blocking_severities() == {"CRITICAL"}
    assert config.should_block([{"severity": "WARNING"}]) is False
    assert config.should_block([{"severity": "CRITICAL"}]) is True


def test_config_allows_custom_blocking_severities():
    config = ConfigManager("missing-vyne-config.yaml")
    config.vyne_rc = {"ignore": [], "block_on": ["CRITICAL", "HIGH"]}

    assert config.get_blocking_severities() == {"CRITICAL", "HIGH"}
    assert config.should_block([{"severity": "HIGH"}]) is True


def test_allowlist_filter_preserves_flat_findings():
    findings = [
        {"scanner": "SecretScanner", "message": "known test token", "severity": "CRITICAL"},
        {"scanner": "StaticScanner", "message": "unsafe call", "severity": "WARNING"},
    ]

    filtered = _filter_findings_by_allowlist(findings, ["known test token"])

    assert filtered == [findings[1]]


def test_vdi_distinguishes_missing_package():
    result = check_package(
        "not-installed-package",
        lookup=lambda name: {"status": "missing", "data": None},
    )

    assert result["verification_status"] == "missing"
    assert result["pypi_exists"] is False


def test_vdi_distinguishes_unavailable_registry():
    result = check_package(
        "private-package",
        lookup=lambda name: {"status": "unavailable", "data": None},
    )

    assert result["verification_status"] == "unavailable"
    assert result["pypi_exists"] is None
    assert result["confidence"] == 0.0


def test_dependency_scanner_does_not_call_trusted_namespace(monkeypatch):
    monkeypatch.setattr(
        dependency,
        "check_package",
        lambda name: (_ for _ in ()).throw(AssertionError("trusted import was checked")),
    )

    findings = dependency.scan(None, "import os\n", "snippet.py")

    assert findings == []


def test_cli_warning_does_not_fail_by_default(monkeypatch):
    source = "tests/conftest.py"

    class FakeParser:
        def __init__(self, path):
            self.path = path

        def parse(self):
            return None

    class FakeRegistry:
        scanners = [object()]

        def run_all(self, ast_root, raw_code, file_path):
            return [{"severity": "WARNING", "scanner": "TestScanner", "message": "test warning"}]

    monkeypatch.setattr("vyne.cli.CodeParser", FakeParser)
    monkeypatch.setattr("vyne.cli.registry", FakeRegistry())
    monkeypatch.setattr("vyne.cli.config", ConfigManager("missing-vyne-config.yaml"))

    assert run_audit(source) == 0


def test_cli_critical_fails_by_default(monkeypatch):
    source = "tests/conftest.py"

    class FakeParser:
        def __init__(self, path):
            self.path = path

        def parse(self):
            return None

    class FakeRegistry:
        scanners = [object()]

        def run_all(self, ast_root, raw_code, file_path):
            return [{"severity": "CRITICAL", "scanner": "TestScanner", "message": "test issue"}]

    monkeypatch.setattr("vyne.cli.CodeParser", FakeParser)
    monkeypatch.setattr("vyne.cli.registry", FakeRegistry())
    monkeypatch.setattr("vyne.cli.config", ConfigManager("missing-vyne-config.yaml"))

    assert run_audit(source) == 1
