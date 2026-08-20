# Vyne

Security signal for AI-built code.

Status: `v0.5.0`

## What Vyne does

Vyne detects hallucinated imports, phantom attributes, and hardcoded secrets in AI-generated Python code.

This scope is intentionally bounded: Vyne focuses on statically-verifiable issues in Python code such as:

- hallucinated or suspicious dependencies (import-time mismatches)
- phantom or misspecified attributes on imported modules
- hardcoded secrets and high-entropy tokens

It combines Tree-sitter parsing with lightweight scanners so teams can review generated code before it ships.

## How it works

1. Parse the target file into a syntax tree with Tree-sitter.
2. Run focused scanners across the AST and raw source.
3. Return structured findings to the CLI, API, or dashboard.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
python verify_setup.py
pip install -e .
```

Run a scan:

```bash
vyne tests/v0.3.1_test.py
```

## Local development

Start the API:

```bash
uvicorn vyne.api.main:app --reload
```

Start the dashboard:

```bash
cd web
npm install
npm run dev
```

## Verification

```bash
pytest tests/
```

## Project layout

- `src/vyne`: Python package, scanners, API, and shared utilities
- `web`: Next.js dashboard
- `tools`: developer automation and documentation helpers
