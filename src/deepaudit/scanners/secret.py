import re

def scan_for_secrets(code_content):
    """
    Scans for high-entropy strings that look like API Keys or Tokens.
    """
    # Patterns for common 2026 API keys
    patterns = {
        "Generic API Key": r'(?:key|api|token|secret|pass|auth)[-_]?(?:key|api|token|secret|pass|auth)?["\']?\s*[:=]\s*["\']([A-Za-z0-9-_]{20,})["\']',
        "GitHub Fine-grained Token": r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}',
        "AWS Access Key": r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])'
    }

    findings = []
    for name, regex in patterns.items():
        matches = re.finditer(regex, code_content, re.IGNORECASE)
        for match in matches:
            findings.append({
                "type": "SECRET_LEAK",
                "label": name,
                "snippet": f"...{match.group(0)[:15]}***..." # Obfuscate for safety
            })
    return findings