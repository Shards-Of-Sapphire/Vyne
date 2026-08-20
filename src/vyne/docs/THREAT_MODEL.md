# Vyne Threat Model

## Purpose

Vyne is a bounded static-analysis tool for AI-generated Python code. It identifies
patterns that can be evaluated from source code and local or registry metadata before
execution.

## In scope

- Imports of packages that the configured registry explicitly reports as missing.
- Static, conditional, and literal `importlib.import_module` dependency references.
- Dangerous execution calls detected by the static scanner.
- High-entropy quoted strings that may contain hardcoded secrets.
- Findings and exit decisions produced by the deterministic scanner pipeline.

## Explicitly out of scope

- General logic correctness, business-rule errors, and off-by-one bugs.
- Runtime behavior, exploitability, reachability, and environmental configuration.
- API compatibility across package versions without a versioned API signature database.
- Dynamic imports whose module name is not a literal string.
- Attributes added at runtime through monkey-patching or framework initialization.
- Secrets assembled from multiple values, fetched at runtime, or hidden by encoding.
- Complete coverage of provider-specific credentials; the secret scanner is heuristic.

## Ouroboros loop limitation

The deterministic feedback loop can only revisit findings that the scanners already
know how to produce. Re-running the pipeline does not discover classes of issues that
are outside the scanner rules. A clean result therefore means that no configured
scanner produced a finding; it does not mean that the code is safe or bug-free.

## Verification uncertainty

When the package registry is unavailable, Vyne reports an `INFO` finding with an
`unavailable` verification status. It does not convert an outage into evidence of a
hallucinated dependency. A package reported as missing is still a high-confidence
signal, but users should review private indexes and project configuration before
blocking a build.
