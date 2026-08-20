# Vyne Scanner Specification (v0.5.0)

The Scanner Registry is a modular plugin system. It passes the parsed root node,
raw source, and file path to each scanner and returns one flat list of findings.

*1. The Scanner Interface*
Every scanner in the src/vyne/scanners/ directory must follow a strict functional contract. This ensures the CLI can call any scanner without knowing its internal logic.

Input: `scan(ast_node, raw_code, file_path)`.

Output: A list of dictionaries, where each dictionary represents a finding.

The registry does not require a shared metadata dictionary. Individual scanners
may parse the raw source with Python `ast` when their checks require it.

The old metadata object was:

raw_code: The entire source code as a str.

libraries: A list of strings representing imported modules.

root: The Tree-sitter Node object representing the top of the syntax tree.

*2. Active Scanners & Logic*
A. Dependency Shield (dependency.py)
Logic: Extracts static, conditional, and literal dynamic imports and checks their
top-level package names against trusted namespaces and the PyPI registry.

Severity: `CRITICAL` when the registry explicitly reports that a package is missing.
Registry or network unavailability is reported as `INFO` with an `unavailable`
verification status and is not treated as a hallucinated package.

Current constraint: verification is not a versioned API signature database. A
package can exist while an imported API has changed between releases.

B. Secret Scanner (secret.py)
Logic: High-entropy string detection over quoted strings in the raw source.

Patterns: strings longer than 16 characters, without spaces, whose Shannon entropy
exceeds 4.5. This is heuristic detection, not provider-specific credential parsing.

Severity: CRITICAL. Hardcoded secrets are the #1 cause of cloud breaches in AI-generated deployments.

C. Static Auditor (static.py)
Logic: AST-based dangerous function detection for calls such as `eval`, `exec`,
and `os.system`.

Severity: `WARNING`. These functions can allow AI-generated code to execute arbitrary commands on the host machine and should be reviewed.

## 3. Finding Format

Every scanner returns findings using this structure:

```python
{
    "scanner": "SecretScanner",
    "severity": "CRITICAL",
    "line": 4,
    "message": "High entropy string detected",
    "snippet": "TOKEN = \"...\""
}
```

The CLI and API consume this same flat finding format. Exit status is controlled by
`.vynerc`; `CRITICAL` is the default blocking severity.
