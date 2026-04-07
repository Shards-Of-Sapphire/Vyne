# src/vyne/scanners/static.py

import ast

def scan(ast_node, raw_code: str, file_path: str) -> list[dict]:
    """Performs static analysis to catch dangerous execution functions using AST parsing."""
    findings = []

    # Dangerous functions that should rarely be used in AI-generated code
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'os.system', 'subprocess.Popen', 'subprocess.call',
        'subprocess.run', 'os.popen', 'os.execvp', 'os.execv', 'os.execlp'
    }

    class DangerousCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.findings = []

        def visit_Call(self, node):
            # Check direct function calls
            if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_FUNCTIONS:
                self._add_finding(node, node.func.id)
            # Check attribute access calls (e.g., os.system, subprocess.Popen)
            elif isinstance(node.func, ast.Attribute):
                full_name = self._get_full_attr_name(node.func)
                if full_name in DANGEROUS_FUNCTIONS:
                    self._add_finding(node, full_name)
            self.generic_visit(node)

        def _get_full_attr_name(self, node):
            """Get the full dotted name of an attribute access."""
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}.{node.attr}"
            elif isinstance(node.value, ast.Attribute):
                return f"{self._get_full_attr_name(node.value)}.{node.attr}"
            return node.attr

        def _add_finding(self, node, func_name):
            # Get line number and source code snippet
            lines = raw_code.splitlines()
            line_num = getattr(node, 'lineno', 1) - 1  # Convert to 0-based
            snippet = lines[line_num].strip() if line_num < len(lines) else ""

            self.findings.append({
                "scanner": "StaticScanner",
                "severity": "WARNING",
                "line": line_num + 1,  # Convert back to 1-based
                "message": f"Dangerous dynamic execution function detected: '{func_name}()'",
                "snippet": snippet,
                "confidence": 0.9
            })

    # Parse and analyze the AST
    try:
        tree = ast.parse(raw_code, filename=file_path)
        visitor = DangerousCallVisitor()
        visitor.visit(tree)
        findings.extend(visitor.findings)
    except SyntaxError:
        # Fallback to string-based detection if AST parsing fails
        findings.extend(_fallback_string_detection(raw_code))

    return findings


def _fallback_string_detection(raw_code: str) -> list[dict]:
    """Fallback string-based detection for when AST parsing fails."""
    findings = []
    DANGEROUS_FUNCTIONS = {"eval(", "exec(", "os.system(", "subprocess.Popen("}

    lines = raw_code.splitlines()
    for i, line in enumerate(lines):
        line_clean = line.strip()

        # Ignore comments
        if line_clean.startswith("#"):
            continue

        for func in DANGEROUS_FUNCTIONS:
            if func in line_clean:
                findings.append({
                    "scanner": "StaticScanner",
                    "severity": "WARNING",
                    "line": i + 1,
                    "message": f"Dangerous dynamic execution function detected: '{func}'",
                    "snippet": line_clean,
                    "confidence": 0.7  # Lower confidence for string matching
                })
    return findings
