import pytest
from deepaudit.scanners.dependency import verify_package
from deepaudit.scanners.secret import scan_for_secrets

# --- Test 1: Dependency Verification ---
def test_verify_real_package():
    # 'requests' is a pillar of the internet; it should always be True
    exists, msg = verify_package("requests")
    assert exists is True
    assert "Verified" in msg

def test_verify_fake_package():
    # This package definitely doesn't exist
    exists, msg = verify_package("this_is_a_hallucinated_package_12345")
    assert exists is False
    assert "HALLUCINATION" in msg

# --- Test 2: Secret Leak Detection ---
def test_scan_for_github_token():
    fake_code = 'token = "github_pat_11A2B3C4D5E6F7G8H9I0J1_K2L3M4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7A8B9C0"'
    findings = scan_for_secrets(fake_code)
    assert len(findings) > 0
    assert findings[0]['label'] == "GitHub Fine-grained Token"

def test_scan_no_secrets():
    clean_code = 'print("Hello Sapphire!")'
    findings = scan_for_secrets(clean_code)
    assert len(findings) == 0