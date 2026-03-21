# 🔍 DeepAudit Scanner Specification

*1. Scanner Structure*
Every scanner in `src/deepaudit/scanners/` must be a standalone module. It should contain a primary function that accepts the `metadata` object and returns a `findings` list.

*2. Severity Levels*
Findings must be categorized by impact:
* **CRITICAL:** Direct security breach (e.g., Hardcoded Secret, Hallucinated Dependency).
* **HIGH:** Dangerous logic (e.g., `eval()`, `os.system()`).
* **MEDIUM:** Best practice violations (e.g., Unsafe library versions).
* **LOW:** Informational or "Vibe Check" warnings.

*3. Standard Return Format*
```python
{
    "type": "CATEGORY_NAME",
    "severity": "CRITICAL/HIGH/MEDIUM/LOW",
    "issue": "Short description of the flaw",
    "fix": "Specific advice on how to resolve the issue",
    "snippet": "The offending code fragment (obfuscated if sensitive)"
}
```
*4. Hallucination Logic*
​When verifying dependencies, the scanner must differentiate between:
​404: Confirmed Hallucination (Critical).
​Timeout: Registry Unreachable (Warning).
​200: Verified (Pass).
