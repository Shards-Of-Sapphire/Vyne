import ast
from typing import List


def _max_loop_nesting(node: ast.AST, depth=0) -> int:
    max_depth = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While)):
            max_depth = max(max_depth, _max_loop_nesting(child, depth + 1))
        else:
            max_depth = max(max_depth, _max_loop_nesting(child, depth))
    return max_depth


def _contains_break(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Break):
            return True
    return False


def scan(ast_node, raw_code: str, file_path: str) -> List[dict]:
    findings = []
    try:
        tree = ast.parse(raw_code)
    except Exception:
        return findings

    # Detect infinite-loops: while True without any break in the loop body
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            # Check constant True test
            test = node.test
            is_true = False
            if isinstance(test, ast.Constant) and test.value is True:
                is_true = True

            if is_true and not _contains_break(node):
                findings.append({
                    "scanner": "LogicScanner",
                    "severity": "CRITICAL",
                    "line": getattr(node, "lineno", 0),
                    "message": "Infinite 'while True' loop without break detected — possible AI-generated messy logic",
                    "snippet": "while True: ...",
                    "confidence": 0.9,
                })

    # Detect deeply nested loops
    nesting = _max_loop_nesting(tree, 0)
    if nesting >= 3:
        findings.append({
            "scanner": "LogicScanner",
            "severity": "WARNING",
            "line": 1,
            "message": f"Deeply nested loops detected (nesting level = {nesting}) — consider refactoring or unit tests",
            "snippet": "nested loops",
            "confidence": 0.6,
        })

    # Detect large-range loops (range with large constant)
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            target = node.iter
            if isinstance(target, ast.Call) and getattr(target.func, 'id', '') == 'range':
                # check first arg if constant and large
                if target.args:
                    first = target.args[0]
                    try:
                        if isinstance(first, ast.Constant) and isinstance(first.value, int):
                            if first.value >= 1_000_000:
                                findings.append({
                                    "scanner": "LogicScanner",
                                    "severity": "WARNING",
                                    "line": getattr(node, 'lineno', 0),
                                    "message": f"For-loop over large range({first.value}) — may be AI-generated or require streaming",
                                    "snippet": f"for _ in range({first.value}):",
                                    "confidence": 0.5,
                                })
                    except Exception:
                        pass

    return findings
