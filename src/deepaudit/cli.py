import sys
from rich.console import Console
from rich.panel import Panel
from deepaudit.engine.parser import get_ast_metadata
from deepaudit.scanners.dependency import verify_package

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: deepaudit <file.py>[/yellow]")
        return

    file_path = sys.argv[1]
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    console.print(Panel(f"DeepAudit MVP Scanning: [bold cyan]{file_path}[/bold cyan]"))

    # Execute X-Ray
    metadata = get_ast_metadata(code)
    
    # Run Dependency Shield
    for lib in metadata['libraries']:
        exists, msg = verify_package(lib)
        if not exists:
            console.print(f"❌ [bold red]HALLUCINATION ALERT:[/bold red] '{lib}' {msg}")
        else:
            console.print(f"✅ [green]VERIFIED:[/green] {lib} ({msg})")

if __name__ == "__main__":
    main()