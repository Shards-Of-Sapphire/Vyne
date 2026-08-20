# 🏛️ Vyne Backend Architecture

## 1. Core Philosophy

Vyne is a bounded, modular static-analysis tool for AI-generated Python code. The
current implementation prioritizes deterministic findings over claims of complete
security coverage.

## 2. The Execution Pipeline

Every audit must follow this strict sequence:

1. **Ingestion:** CLI reads the target file as UTF-8.
2. **AST Parsing (The X-Ray):** `engine/parser.py` generates a Tree-sitter CST.
3. **Scanner Execution:** The registry invokes each scanner with the parsed root,
   raw source, and file path.
4. **Reporting:** The CLI, API, and dashboard consume one flat list of findings.

## 3. Data Schema: The Finding Object

Every finding uses this minimum structure:

```python
{
    "scanner": "DependencyScanner",
    "severity": "CRITICAL",
    "line": 1,
    "message": "Description of the finding",
    "snippet": "Relevant source line"
}
```

Scanner functions receive `scan(ast_node, raw_code, file_path)`. They may parse the
raw source independently when a check requires Python's `ast` module.
