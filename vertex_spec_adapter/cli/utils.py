"""CLI utilities for formatting, error messages, and progress indicators."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from vertex_spec_adapter.core.exceptions import VertexSpecAdapterError

console = Console()


def format_error(error: Exception, include_suggestion: bool = True) -> str:
    """
    Format error message with suggestions.
    
    Args:
        error: Exception to format
        include_suggestion: Whether to include suggested fixes
        
    Returns:
        Formatted error message
    """
    if isinstance(error, VertexSpecAdapterError):
        message = str(error)
        if include_suggestion and hasattr(error, "suggested_fix") and error.suggested_fix:
            message += f"\n  → {error.suggested_fix}"
        return message
    
    # Generic error formatting
    return str(error)


def print_error(error: Exception, include_suggestion: bool = True) -> None:
    """
    Print error message with rich formatting.
    
    Args:
        error: Exception to print
        include_suggestion: Whether to include suggested fixes
    """
    message = format_error(error, include_suggestion)
    console.print(f"[red]✗[/red] {message}", style="red")


def print_success(message: str) -> None:
    """
    Print success message with rich formatting.
    
    Args:
        message: Success message to print
    """
    console.print(f"[green]✓[/green] {message}", style="green")


def print_warning(message: str) -> None:
    """
    Print warning message with rich formatting.
    
    Args:
        message: Warning message to print
    """
    console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def print_info(message: str) -> None:
    """
    Print info message with rich formatting.
    
    Args:
        message: Info message to print
    """
    console.print(f"[blue]ℹ[/blue] {message}", style="blue")


def print_panel(content: str, title: Optional[str] = None, style: str = "blue") -> None:
    """
    Print content in a rich panel.
    
    Args:
        content: Content to display
        title: Optional panel title
        style: Panel style
    """
    console.print(Panel(content, title=title, style=style))


def create_progress(task_description: str) -> Progress:
    """
    Create a progress indicator for long-running operations.
    
    Args:
        task_description: Description of the task
        
    Returns:
        Progress context manager
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> None:
    """
    Print a formatted table.
    
    Args:
        headers: Column headers
        rows: Table rows (list of lists)
        title: Optional table title
    """
    from rich.table import Table
    
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    for header in headers:
        table.add_column(header)
    
    for row in rows:
        table.add_row(*row)
    
    console.print(table)


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Prompt user for yes/no confirmation.
    
    Args:
        prompt: Prompt message
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    default_text = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} [{default_text}]: "
    
    while True:
        try:
            response = input(full_prompt).strip().lower()
            if not response:
                return default
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            console.print("[yellow]Please enter 'y' or 'n'[/yellow]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Cancelled[/yellow]")
            return False


def prompt_input(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """
    Prompt user for input.
    
    Args:
        prompt: Prompt message
        default: Default value if user just presses Enter
        required: Whether input is required
        
    Returns:
        User input or default value
    """
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        try:
            response = input(full_prompt).strip()
            if response:
                return response
            if default:
                return default
            if not required:
                return ""
            console.print("[yellow]This field is required[/yellow]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Cancelled[/yellow]")
            raise KeyboardInterrupt("User cancelled input")


def print_step(step_number: int, total_steps: int, description: str) -> None:
    """
    Print a step indicator.
    
    Args:
        step_number: Current step number (1-based)
        total_steps: Total number of steps
        description: Step description
    """
    console.print(
        f"[cyan][{step_number}/{total_steps}][/cyan] {description}",
        style="cyan"
    )

