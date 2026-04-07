import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

console = Console()

try:
    import vyne
    console.print("[bold green]✅ Success![/bold green] Vyne package is resolved.")
    console.print(f"Location: [cyan]{vyne.__file__}[/cyan]")
except ImportError:
    console.print(
        "[bold red]Error:[/bold red] Vyne not found. "
        "Install the package or add src to PYTHONPATH."
    )

try:
    load_dotenv(PROJECT_ROOT / ".env")
    console.print("[bold green]✅ Success![/bold green] python-dotenv is working.")
except Exception as exc:
    console.print(f"[bold red]Error:[/bold red] Dotenv failed: {exc}")
