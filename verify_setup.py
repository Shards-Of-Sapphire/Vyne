import sys
from dotenv import load_dotenv
import tree_sitter
from rich.console import Console

console = Console()

try:
    import deepaudit
    console.print("[bold green]✅ Success![/bold green] DeepAudit package is resolved.")
    console.print(f"📍 Location: [cyan]{deepaudit.__file__}[/cyan]")
except ImportError:
    console.print("[bold red]❌ Error:[/bold red] DeepAudit not found. Did you run 'pip install -e .'?")

try:
    load_dotenv()
    console.print("[bold green]✅ Success![/bold green] python-dotenv is working.")
except Exception as e:
    console.print(f"[bold red]❌ Error:[/bold red] Dotenv failed: {e}")