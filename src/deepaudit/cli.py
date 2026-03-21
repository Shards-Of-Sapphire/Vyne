import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.table import Table
from deepaudit.engine.parser import get_ast_metadata
from deepaudit.scanners.dependency import verify_package
from deepaudit.scanners.secret import scan_for_secrets
from deepaudit.scanners.secret import scan_for_secrets

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: deepaudit <file.py>[/yellow]")
        return

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Print Header
    console.print(Panel(f"DeepAudit MVP Scanning: [bold cyan]{file_path}[/bold cyan]"))

    # Execute X-Ray
    metadata = get_ast_metadata(code)

    # Scan for Secrets (Logic Flaw Detection)
    secrets = scan_for_secrets(code)
    if secrets:
        secret_table = Table(title="🔒 Confidential Data Leak Scan", style="yellow")
        secret_table.add_column("Type", style="bold red")
        secret_table.add_column("Detected Snippet")
        
        for secret in secrets:
            secret_table.add_row(secret['label'], secret['snippet'])
        
        console.print(secret_table)
    
    # Run Dependency Shield
    for lib in metadata['libraries']:
        exists, msg = verify_package(lib)
        if not exists:
            console.print(f"❌ [bold red]HALLUCINATION ALERT:[/bold red] '{lib}' {msg}")
        else:
            console.print(f"✅ [green]VERIFIED:[/green] {lib} ({msg})")

if __name__ == "__main__":
    main()