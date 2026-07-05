import argparse
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import VERSION
from .engine.parser import CodeParser
from .scanners.scanners import ScannerRegistry
from .utils.config import ConfigManager

console = Console()
registry = ScannerRegistry()
config = ConfigManager()

def _filter_findings_by_allowlist(findings_by_scanner: list[list[dict]], allowlist: list[str]) -> list[list[dict]]:
    """Filter out findings that match any allowlist pattern (simple substring match)."""
    if not allowlist:
        return findings_by_scanner

    filtered: list[list[dict]] = []
    for scanner_findings in findings_by_scanner:
        kept = []
        for finding in scanner_findings:
            text = "|".join([str(finding.get(k, "")) for k in ("scanner", "message", "snippet")])
            # If any allowlist pattern is a substring of the finding text, skip
            if any(pattern and pattern in text for pattern in allowlist):
                continue
            kept.append(finding)
        if kept:
            filtered.append(kept)
    return filtered

def display_header() -> None:
    """Render the CLI header."""
    console.print(
        Panel.fit(
            f"[bold green]VYNE[/bold green]\n"
            f"[bold white]v{VERSION}[/bold white]\n"
            f"[dim]Security signal for AI-built code[/dim]",
            border_style="green",
            padding=(1, 4),
        )
    )


def _build_results_table(filename: str) -> Table:
    """Constructs the Rich table schema for v0.3.0."""
    table = Table(
        title=f"Vyne Scan Results: {filename}",
        show_header=True, 
        header_style="bold green",
        expand=True
    )
    table.add_column("Severity", style="bold", width=12)
    table.add_column("Line", justify="right", style="cyan", width=6)
    table.add_column("Scanner", style="blue", width=18)
    table.add_column("Issue Details", style="white")
    return table


def _render_findings(table: Table, findings_by_scanner: list[list[dict]]) -> int:
    """Parses the v0.3.0 dictionary schema and populates the UI table."""
    count = 0
    for scanner_findings in findings_by_scanner:
        for finding in scanner_findings:
            count += 1
            
            # Extract data using the strict v0.3.0 schema
            severity = finding.get("severity", "UNKNOWN")
            line = str(finding.get("line", "?"))
            scanner = finding.get("scanner", "UnknownScanner")
            message = finding.get("message", "Unknown issue")
            snippet = finding.get("snippet", "")
            
            # Add dynamic colors based on severity
            if severity == "CRITICAL":
                sev_fmt = f"[bold red]{severity}[/bold red]"
            elif severity == "WARNING":
                sev_fmt = f"[bold yellow]{severity}[/bold yellow]"
            else:
                sev_fmt = f"[bold blue]{severity}[/bold blue]"
                
            # Combine message and snippet for a clean UI
            details = message
            if snippet:
                details += f"\n[dim italic]Code: {snippet}[/dim italic]"
                
            table.add_row(sev_fmt, line, scanner, details)
            
    return count


def run_audit(file_path: str) -> int:
    target = Path(file_path)
    if not target.exists() or not target.is_file():
        console.print(f"[bold red]Error:[/bold red] File {file_path} not found.")
        return 1

    display_header()

    # 1. Parsing Phase
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Parsing source...", total=None)
        
        parser = CodeParser(str(target))
        # v0.3.0 Standard: Extracting AST and Raw Code for the new registry signature
        ast_root = parser.parse()
        with open(target, "r", encoding="utf-8") as f:
            raw_code = f.read()

    results_table = _build_results_table(target.name)
    findings_by_scanner: list[list[dict]] = []

    # 2. Scanning Phase (Dynamic Registry Integration)
    with Progress(transient=True) as progress:
        task = progress.add_task(
            "[cyan]Scanning for vulnerabilities...",
            total=len(registry.scanners),
        )
        
        for scanner_func in registry.scanners:
            try:
                # Execute the dynamic hook: scan(ast_node, raw_code, file_path)
                findings = scanner_func(ast_root, raw_code, str(target))
                
                # Keep the nested list structure for _render_findings
                if findings:
                    findings_by_scanner.append(findings)
            except Exception as e:
                console.print(f"[bold yellow]Warning:[/bold yellow] Scanner module crashed - {e}")
                
            progress.advance(task)

    # 3. Rendering Phase
    # Apply project allowlist from .vynerc (if present)
    allowlist = config.get_project_allowlist()
    findings_by_scanner = _filter_findings_by_allowlist(findings_by_scanner, allowlist)

    findings_count = _render_findings(results_table, findings_by_scanner)
    if findings_count > 0:
        console.print(results_table)
        console.print(
            f"\n[bold red]Vyne flagged {findings_count} potential risks.[/bold red]"
        )
        return 1

    console.print(
        "\n[bold green]Vyne found no major hallucinations or leaks.[/bold green]"
    )
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Vyne CLI")
    parser.add_argument("file", nargs='+', help="Path(s) to the Python file(s) to audit")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Vyne {VERSION}",
    )
    args = parser.parse_args()
    # Support multiple files passed from pre-commit
    exit_codes = []
    for f in args.file:
        exit_codes.append(run_audit(f))
    # If any run returned non-zero, exit non-zero
    return 1 if any(code != 0 for code in exit_codes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
