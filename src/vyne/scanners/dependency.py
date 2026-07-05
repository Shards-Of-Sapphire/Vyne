# src/vyne/scanners/dependency.py

import ast
from typing import List
from ..utils.vdi import check_package


def _extract_imports_from_ast(raw_code: str) -> List[dict]:
    imports = []
    try:
        tree = ast.parse(raw_code)
    except Exception:
        # Fallback: naive line scan
        lines = raw_code.splitlines()
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith("import "):
                parts = s.split()
                if len(parts) >= 2:
                    imports.append({"name": parts[1].split('.')[0], "line": i + 1, "conditional": False})
            elif s.startswith("from "):
                parts = s.split()
                if len(parts) >= 2:
                    imports.append({"name": parts[1].split('.')[0], "line": i + 1, "conditional": False})
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"name": alias.name.split('.')[0], "line": node.lineno, "conditional": False})
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module:
                imports.append({"name": module.split('.')[0], "line": node.lineno, "conditional": False})
        elif isinstance(node, ast.Try):
            # detect conditional imports within try/except
            for inner in node.body:
                if isinstance(inner, ast.Import):
                    for alias in inner.names:
                        imports.append({"name": alias.name.split('.')[0], "line": inner.lineno, "conditional": True})
                elif isinstance(inner, ast.ImportFrom):
                    if inner.module:
                        imports.append({"name": inner.module.split('.')[0], "line": inner.lineno, "conditional": True})
        elif isinstance(node, ast.Call):
            # importlib.import_module('name') detection
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == 'import_module':
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    imports.append({"name": node.args[0].value.split('.')[0], "line": node.lineno, "conditional": True})

    return imports


def scan(ast_node, raw_code: str, file_path: str) -> List[dict]:
    findings = []

    imports = _extract_imports_from_ast(raw_code)
    for imp in imports:
        name = imp.get("name")
        line = imp.get("line", 0)
        conditional = imp.get("conditional", False)

        v = check_package(name)

        if not v.get("pypi_exists"):
            findings.append({
                "scanner": "DependencyScanner",
                "severity": "CRITICAL",
                "line": line,
                "message": f"Package '{name}' not found on PyPI — likely hallucinated",
                "snippet": name,
                "confidence": v.get("confidence", 0.95),
            })
        elif v.get("semver_major_mismatch"):
            findings.append({
                "scanner": "DependencyScanner",
                "severity": "HIGH",
                "line": line,
                "message": f"Installed version ({v.get('installed_version')}) of '{name}' differs in major version from PyPI latest ({v.get('pypi_latest')}) — potential API change",
                "snippet": name,
                "confidence": v.get("confidence", 0.7),
            })
        else:
            # If import is conditional and package not installed locally, flag as WARNING
            if conditional and not v.get("installed"):
                findings.append({
                    "scanner": "DependencyScanner",
                    "severity": "WARNING",
                    "line": line,
                    "message": f"Conditional or dynamic import of '{name}' detected; not installed in environment",
                    "snippet": name,
                    "confidence": v.get("confidence", 0.35),
                })

    return findings

