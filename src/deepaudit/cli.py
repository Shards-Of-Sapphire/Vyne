import argparse
from pathlib import Path
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from deepaudit import VERSION
from deepaudit.engine.parser import CodeParser
from deepaudit.engine.parser import CodeParser
from deepaudit.scanners.scanners import ScannerRegistry

console = Console()
registry = ScannerRegistry()

def display_header() -> None:
    """Render the CLI header."""
    console.print(
        Panel.fit(
            f"[bold blue]SAPPHIRE[/bold blue]\n"
            f"[bold white]DeepAudit v{VERSION}[/bold white]\n"
            f"[dim]The X-Ray for AI-Generated Code[/dim]",
            border_style="blue",
            padding=(1, 4),
        )
    )


def _build_results_table(filename: str) -> Table:
    """Constructs the Rich table schema for v0.3.0."""
    table = Table(
        title=f"Security Audit: {filename}", 
        show_header=True, 
        header_style="bold magenta",
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
    findings_count = _render_findings(results_table, findings_by_scanner)
    if findings_count > 0:
        console.print(results_table)
        console.print(
            f"\n[bold red]Audit Failed:[/bold red] Found {findings_count} potential risks."
        )
        return 1

    console.print(
        "\n[bold green]Audit Passed:[/bold green] No major hallucinations or leaks detected."
    )
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="DeepAudit CLI")
    parser.add_argument("file", help="Path to the Python file to audit")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"DeepAudit {VERSION}",
    )
    args = parser.parse_args()
    return run_audit(args.file)


if __name__ == "__main__":
    raise SystemExit(main())
