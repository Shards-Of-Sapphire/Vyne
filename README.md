# Vyne

Security signal for AI-built code.

Status: `v0.5.0`

## What Vyne does

Vyne detects hallucinated imports, risky execution patterns, and hardcoded secrets in AI-generated Python code.

This scope is intentionally bounded: Vyne focuses on statically-verifiable issues in Python code such as:

- dependencies that cannot be verified in the package registry
- dangerous execution calls such as `eval`, `exec`, and `os.system`
- hardcoded secrets and high-entropy tokens

It combines Tree-sitter parsing with lightweight scanners so teams can review generated Python code before it ships. Its results are bounded static-analysis signals, not a guarantee that code is safe.

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

By default, only `CRITICAL` findings fail the command. Configure a stricter gate in
`.vynerc` when needed:

```yaml
block_on:
- CRITICAL
- HIGH
```

Registry outages are reported as `INFO` and `unavailable`; they are not treated as
evidence that a dependency is hallucinated.

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

See [the threat model](src/vyne/docs/THREAT_MODEL.md) for supported attack classes,
known blind spots, and the limits of deterministic scanning.

## Project layout

- `src/vyne`: Python package, scanners, API, and shared utilities
- `web`: Next.js dashboard
- `tools`: developer automation and documentation helpers
