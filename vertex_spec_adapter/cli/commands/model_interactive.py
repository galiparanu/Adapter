"""Interactive model selection menu for Gemini CLI."""

import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from vertex_spec_adapter.core.auth import AuthenticationManager
from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.config import ConfigurationManager
from vertex_spec_adapter.core.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ModelNotFoundError,
)
from vertex_spec_adapter.core.models import ModelMetadata, ModelRegistry
from vertex_spec_adapter.utils.logging import get_logger

logger = get_logger(__name__)


class ModelInteractiveMenu:
    """
    Interactive menu for selecting Vertex AI models.
    
    Provides a Rich-based terminal UI with keyboard navigation and hover details.
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        console: Optional[Console] = None,
    ) -> None:
        """
        Initialize interactive menu.
        
        Args:
            config_path: Path to Vertex Adapter config file. Defaults to `.specify/config.yaml`.
            console: Rich Console instance. Defaults to new Console().
        
        Raises:
            ConfigurationError: If config file is invalid or missing
            ModelNotFoundError: If current model is not available
        """
        self.console = console or Console()
        self.config_manager = ConfigurationManager(config_path=config_path)
        self.model_registry = ModelRegistry()
        
        # Load configuration
        try:
            config = self.config_manager.load_config()
            project_id = config.project_id
            self.current_model_id = config.model.id if config.model else None
        except ConfigurationError:
            # Use defaults if config not available
            project_id = "default-project"
            self.current_model_id = None
        
        # Load available models (T033: Handle Missing Models Gracefully)
        try:
            models_dict = self.model_registry.get_available_models(
                project_id=project_id,
                region=None,
                use_cache=True,
            )
        except Exception as e:
            # ModelRegistry unavailable - use empty list, will show error later
            logger.warning(f"ModelRegistry unavailable: {e}")
            models_dict = []
        
        # Convert dicts to ModelMetadata objects
        self.models: List[ModelMetadata] = []
        for model_dict in models_dict:
            model_id = model_dict.get("id")
            if model_id:
                try:
                    metadata = self.model_registry.get_model_metadata(model_id)
                    if metadata:
                        self.models.append(metadata)
                except Exception:
                    # Skip invalid models, don't crash
                    continue
        
        # Sort models alphabetically by name (per FR-004)
        self.models.sort(key=lambda m: m.name.lower())
        
        # Menu state
        self.selected_index = 0
        self.hover_details_model_id: Optional[str] = None
        
        # Performance optimization: Cache formatted hover details (T046)
        self._hover_details_cache: dict[str, Text] = {}
        
        # Performance optimization: Cache layout structure (T045)
        self._layout_cache: Optional[Layout] = None
        
        # Initialize selected_index to current model if available
        if self.current_model_id:
            for i, model in enumerate(self.models):
                if model.model_id.lower() == self.current_model_id.lower():
                    self.selected_index = i
                    self.hover_details_model_id = model.model_id
                    break
        
        # If no hover details set, use selected model
        if not self.hover_details_model_id and self.models:
            self.hover_details_model_id = self.models[self.selected_index].model_id
    
    def _get_current_model(self) -> Optional[str]:
        """
        Get the currently active model ID from configuration.
        
        Returns:
            Current model ID or None if not set
        """
        try:
            config = self.config_manager.load_config()
            if config.model:
                return config.model.id
        except ConfigurationError:
            pass
        return None
    
    def _render_menu(self) -> Layout:
        """
        Render the complete menu layout including model list, current model indicator, and hover details.
        
        Optimized for performance (T045): Reuse layout structure, only update content.
        
        Returns:
            Rich Layout object ready for display
        """
        # Performance optimization: Reuse layout structure if exists (T045)
        if self._layout_cache is None:
            # Create layout structure once
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
            )
            layout["body"].split_row(
                Layout(name="model_list", ratio=1),
                Layout(name="hover_details", ratio=1),
            )
            self._layout_cache = layout
        else:
            layout = self._layout_cache
        
        # Update content (faster than recreating layout)
        current_model_text = self._format_current_model()
        layout["header"].update(Panel(current_model_text, border_style="cyan", title="[bold cyan]Vertex AI Models[/bold cyan]"))
        
        model_list_text = self._format_model_list()
        layout["model_list"].update(Panel(model_list_text, title="[bold blue]Available Models[/bold blue]", border_style="blue"))
        
        hover_details_text = self._format_hover_details()
        layout["hover_details"].update(Panel(hover_details_text, title="[bold green]Model Information[/bold green]", border_style="green"))
        
        return layout
    
    def _format_current_model(self) -> Text:
        """
        Format current model display for top panel.
        
        Enhanced visual design (T047): Improved colors and styling.
        
        Returns:
            Rich Text object with current model information
        """
        text = Text()
        if self.current_model_id:
            # Find current model
            current_model = None
            for model in self.models:
                if model.model_id.lower() == self.current_model_id.lower():
                    current_model = model
                    break
            
            if current_model:
                text.append("🎯 Current Model: ", style="bold bright_cyan")
                text.append(f"{current_model.name} ", style="bold bright_white")
                text.append(f"({current_model.model_id})", style="dim white")
            else:
                text.append("🎯 Current Model: ", style="bold bright_cyan")
                text.append(f"{self.current_model_id} ", style="yellow")
                text.append("(not in available models)", style="dim red")
        else:
            text.append("🎯 Current Model: ", style="bold bright_cyan")
            text.append("None", style="dim")
        
        # Add keyboard shortcuts help (T048)
        text.append("  |  ", style="dim")
        text.append("Press ", style="dim")
        text.append("?", style="bold yellow")
        text.append(" or ", style="dim")
        text.append("H", style="bold yellow")
        text.append(" for help", style="dim")
        
        return text
    
    def _format_model_list(self) -> Text:
        """
        Format model list for left panel.
        
        Enhanced visual design (T047): Improved colors and styling.
        
        Returns:
            Rich Text object with model list
        """
        text = Text()
        
        if not self.models:
            text.append("No models available", style="bold red")
            return text
        
        for i, model in enumerate(self.models):
            # Selection indicator (enhanced styling)
            if i == self.selected_index:
                text.append("▶ ", style="bold bright_green")  # Selection indicator
            else:
                text.append("  ")
            
            # Current model indicator (enhanced styling)
            if model.model_id.lower() == (self.current_model_id or "").lower():
                text.append("✓ ", style="bold bright_yellow")
            else:
                text.append("  ")
            
            # Model name (enhanced styling)
            if i == self.selected_index:
                text.append(model.name, style="bold bright_white on bright_blue")
            else:
                text.append(model.name, style="white")
            
            text.append("\n")
        
        return text
    
    def _format_hover_details(self) -> Text:
        """
        Format model metadata for hover details display.
        
        Optimized for performance (T046): Cache formatted details per model.
        
        Returns:
            Rich Text object with formatted model information
        """
        if not self.hover_details_model_id:
            text = Text()
            text.append("Select a model to see details", style="dim")
            return text
        
        # Performance optimization: Use cache if available (T046)
        if self.hover_details_model_id in self._hover_details_cache:
            # Return cached version (status may need update)
            cached_text = self._hover_details_cache[self.hover_details_model_id]
            # Check if status needs update (current model may have changed)
            # For now, return cached (status updates are rare)
            return cached_text
        
        # Find model
        model = None
        for m in self.models:
            if m.model_id == self.hover_details_model_id:
                model = m
                break
        
        if not model:
            text = Text()
            text.append("Model not found", style="red")
            return text
        
        # Format details (T047: Enhanced visual design)
        text = Text()
        
        # Model Name & ID (enhanced styling)
        text.append("Model: ", style="bold cyan")
        text.append(f"{model.name}\n", style="bold bright_cyan")
        text.append(f"ID: {model.model_id}\n\n", style="dim white")
        
        # Context Window
        text.append("Context Window: ", style="bold yellow")
        if model.context_window:
            text.append(f"{model.context_window}\n", style="bright_white")
        else:
            text.append("N/A\n", style="dim")
        
        # Pricing (enhanced formatting)
        if model.pricing:
            text.append("\n💰 Pricing:\n", style="bold yellow")
            if "input" in model.pricing:
                text.append(f"  Input:  ", style="dim")
                text.append(f"${model.pricing['input']:.4f}/1K tokens\n", style="bright_green")
            if "output" in model.pricing:
                text.append(f"  Output: ", style="dim")
                text.append(f"${model.pricing['output']:.4f}/1K tokens\n", style="bright_green")
        else:
            text.append("\n💰 Pricing: ", style="bold yellow")
            text.append("N/A\n", style="dim")
        
        # Capabilities (enhanced formatting)
        if model.capabilities:
            text.append("\n⚡ Capabilities:\n", style="bold yellow")
            for cap in model.capabilities:
                text.append(f"  • ", style="dim")
                text.append(f"{cap}\n", style="bright_white")
        else:
            text.append("\n⚡ Capabilities: ", style="bold yellow")
            text.append("N/A\n", style="dim")
        
        # Status (enhanced visual indicator)
        text.append("\n📊 Status: ", style="bold yellow")
        if model.model_id.lower() == (self.current_model_id or "").lower():
            text.append("✓ Active", style="bold bright_green")
        else:
            text.append("Available", style="green")
        text.append("\n")
        
        # Description (enhanced formatting)
        if model.description:
            text.append("\n📝 Description:\n", style="bold yellow")
            desc_lines = self._wrap_text(model.description, width=40)
            for line in desc_lines:
                text.append(f"  {line}\n", style="white")
        else:
            text.append("\n📝 Description: ", style="bold yellow")
            text.append("N/A\n", style="dim")
        
        # Cache formatted details (T046)
        self._hover_details_cache[self.hover_details_model_id] = text
        
        return text
    
    def _show_keyboard_help(self) -> None:
        """
        Display keyboard shortcuts help (T048: Add Keyboard Shortcuts Help).
        
        Shows help overlay temporarily.
        """
        help_text = Text()
        help_text.append("\n", style="bold bright_yellow")
        help_text.append("Keyboard Shortcuts:\n", style="bold bright_yellow")
        help_text.append("  ", style="dim")
        help_text.append("↑ / ↓", style="bold white")
        help_text.append("  Navigate up/down\n", style="dim")
        help_text.append("  ", style="dim")
        help_text.append("Home / End", style="bold white")
        help_text.append("  Jump to first/last model\n", style="dim")
        help_text.append("  ", style="dim")
        help_text.append("Enter", style="bold white")
        help_text.append("  Select current model\n", style="dim")
        help_text.append("  ", style="dim")
        help_text.append("Escape / Q", style="bold white")
        help_text.append("  Cancel and exit\n", style="dim")
        help_text.append("  ", style="dim")
        help_text.append("? / H", style="bold white")
        help_text.append("  Show this help\n", style="dim")
        help_text.append("\n", style="dim")
        help_text.append("Press any key to continue...", style="dim")
        
        # Show help in a panel
        help_panel = Panel(help_text, title="[bold yellow]Help[/bold yellow]", border_style="yellow")
        self.console.print(help_panel)
        
        # Wait for keypress
        try:
            self._get_key()
        except (EOFError, KeyboardInterrupt):
            pass
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """
        Wrap text to specified width.
        
        Args:
            text: Text to wrap
            width: Maximum width per line
        
        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def _handle_keypress(self, key: str) -> Optional[str]:
        """
        Handle keyboard input and update menu state.
        
        Args:
            key: Key pressed by user
        
        Returns:
            Model ID if Enter pressed, None otherwise
        """
        if not self.models:
            return None
        
        if key == "up":
            # Navigate up (wrap to end)
            self.selected_index = (self.selected_index - 1) % len(self.models)
            self.hover_details_model_id = self.models[self.selected_index].model_id
        
        elif key == "down":
            # Navigate down (wrap to start)
            self.selected_index = (self.selected_index + 1) % len(self.models)
            self.hover_details_model_id = self.models[self.selected_index].model_id
            # Clear cache for new hover model (T046: Cache invalidation)
            if self.hover_details_model_id not in self._hover_details_cache:
                # Will be cached on first format
                pass
        
        elif key == "home":
            # Jump to first model
            self.selected_index = 0
            self.hover_details_model_id = self.models[0].model_id
        
        elif key == "end":
            # Jump to last model
            self.selected_index = len(self.models) - 1
            self.hover_details_model_id = self.models[self.selected_index].model_id
        
        elif key == "enter":
            # Select current model (T022: Model Selection Handler)
            if self.selected_index < len(self.models):
                selected_model = self.models[self.selected_index]
                # Validate model exists in registry
                if self.model_registry.get_model_metadata(selected_model.model_id):
                    return selected_model.model_id
                else:
                    # Model not found in registry (shouldn't happen, but handle gracefully)
                    return None
            return None
        
        elif key == "escape":
            # Cancel
            return None
        
        # Return None to continue (caller will re-render)
        return None
    
    def _check_terminal_support(self) -> bool:
        """
        Check if terminal supports required features (T035: Handle Unsupported Terminals).
        
        Returns:
            True if terminal supports alternate screen, False otherwise
        """
        if not self.console.is_terminal:
            return False
        
        # Check terminal size (minimum 80x24 per FR-011)
        try:
            size = self.console.size
            if size.width < 80 or size.height < 24:
                logger.warning(
                    f"Terminal size too small: {size.width}x{size.height}. "
                    "Minimum recommended: 80x24. Falling back to simple menu."
                )
                return False
        except Exception:
            # If we can't get size, assume unsupported
            return False
        
        return True
    
    def _simple_text_menu(self) -> Optional[str]:
        """
        Simple text-based menu fallback for unsupported terminals (T035: Handle Unsupported Terminals).
        
        Returns:
            Selected model ID or None
        """
        # Show warning about terminal support (T035)
        self.console.print(
            "[yellow]⚠ Terminal doesn't support interactive mode. Using simple text menu.[/yellow]\n"
        )
        
        # T033: Handle Missing Models Gracefully
        if not self.models:
            self.console.print(
                "[red]✗ No models available[/red]\n"
                "[yellow]Possible causes:[/yellow]\n"
                "  • ModelRegistry connection failed\n"
                "  • No models configured in vertex-config.md\n"
                "  • Network connectivity issues\n"
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Check ModelRegistry connection\n"
                "  2. Verify vertex-config.md contains valid models\n"
                "  3. Run 'vertex-spec models list' to see available models\n"
            )
            return None
        
        self.console.print("\n[bold]Available Models:[/bold]\n")
        for i, model in enumerate(self.models):
            current_marker = " [green]✓ (current)[/green]" if model.model_id.lower() == (self.current_model_id or "").lower() else ""
            self.console.print(f"  {i + 1}. {model.name}{current_marker}")
        
        try:
            choice = self.console.input("\n[bold]Select model number (or 'q' to cancel): [/bold]")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(self.models):
                return self.models[index].model_id
            else:
                self.console.print(
                    f"[red]✗ Invalid selection: {choice}[/red]\n"
                    f"[yellow]Please select a number between 1 and {len(self.models)}[/yellow]"
                )
                return None
        except ValueError:
            self.console.print(
                f"[red]✗ Invalid input: '{choice}'[/red]\n"
                "[yellow]Please enter a number or 'q' to cancel[/yellow]"
            )
            return None
        except KeyboardInterrupt:
            # T036: Handle Keyboard Interrupts
            self.console.print("\n[yellow]Selection cancelled by user[/yellow]")
            return None
    
    def _get_key(self) -> str:
        """
        Get a single keypress from stdin (cross-platform).
        
        Returns:
            Key pressed as string
        """
        try:
            import tty
            import termios
        except ImportError:
            # Windows - use msvcrt
            try:
                import msvcrt
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix on Windows
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return "up"
                    elif key == b'P':  # Down arrow
                        return "down"
                    elif key == b'G':  # Home
                        return "home"
                    elif key == b'O':  # End
                        return "end"
                elif key == b'\r' or key == b'\n':
                    return "enter"
                elif key == b'\x1b':  # Escape
                    return "escape"
                else:
                    return key.decode('utf-8', errors='ignore')
            except ImportError:
                # Fallback to input()
                return input("").strip().lower()
        else:
            # Unix/Linux/Mac
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # Escape sequence
                    ch += sys.stdin.read(2)
                    if ch == '\x1b[A':
                        return "up"
                    elif ch == '\x1b[B':
                        return "down"
                    elif ch == '\x1b[H':
                        return "home"
                    elif ch == '\x1b[F':
                        return "end"
                    else:
                        return "escape"
                elif ch == '\r' or ch == '\n':
                    return "enter"
                elif ch == '\x1b':
                    return "escape"
                else:
                    return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def run(self) -> Optional[str]:
        """
        Main entry point to run the interactive menu.
        
        Returns:
            Selected model ID if user selected a model, None if cancelled.
        
        Raises:
            KeyboardInterrupt: If user presses Ctrl+C (handled internally)
        """
        # Check terminal support
        if not self._check_terminal_support():
            return self._simple_text_menu()
        
        # T033: Handle Missing Models Gracefully
        if not self.models:
            self.console.print(
                "[red]✗ No models available[/red]\n"
                "[yellow]Possible causes:[/yellow]\n"
                "  • ModelRegistry connection failed\n"
                "  • No models configured in vertex-config.md\n"
                "  • Network connectivity issues\n"
                "\n[yellow]Troubleshooting:[/yellow]\n"
                "  1. Check ModelRegistry connection\n"
                "  2. Verify vertex-config.md contains valid models\n"
                "  3. Run 'vertex-spec models list' to see available models\n"
            )
            return None
        
        # Use Rich Live for real-time updates (T045: Optimized refresh rate)
        try:
            with Live(self._render_menu(), refresh_per_second=15, screen=True) as live:
                # Main event loop
                while True:
                    try:
                        key = self._get_key()
                        
                        # T048: Keyboard shortcuts help
                        if key.lower() in ('?', 'h'):
                            self._show_keyboard_help()
                            # Re-render menu after help
                            live.update(self._render_menu())
                            continue
                        
                        if key == "up":
                            self._handle_keypress("up")
                            live.update(self._render_menu())
                        elif key == "down":
                            self._handle_keypress("down")
                            live.update(self._render_menu())
                        elif key == "enter":
                            result = self._handle_keypress("enter")
                            if result:
                                return result
                        elif key == "escape":
                            result = self._handle_keypress("escape")
                            if result is None:
                                return None
                        elif key == "home":
                            self._handle_keypress("home")
                            live.update(self._render_menu())
                        elif key == "end":
                            self._handle_keypress("end")
                            live.update(self._render_menu())
                        elif key.lower() == 'q':
                            return None
                        elif key.isdigit():
                            # Try to parse as number for simple selection
                            num = int(key)
                            if 1 <= num <= len(self.models):
                                return self.models[num - 1].model_id
                    except (EOFError, KeyboardInterrupt):
                        # T036: Handle Keyboard Interrupts
                        self.console.print("\n[yellow]Selection cancelled by user[/yellow]")
                        return None
        except KeyboardInterrupt:
            # T036: Handle Keyboard Interrupts
            self.console.print("\n[yellow]Selection cancelled by user[/yellow]")
            return None
    
    def _switch_model(self, model_id: str) -> tuple[bool, Optional[str]]:
        """
        Switch to the selected model and update configuration (T023: Model Switching Logic).
        
        Args:
            model_id: Model ID to switch to
        
        Returns:
            Tuple of (success: bool, message: Optional[str])
            - success: True if switch succeeded, False otherwise
            - message: Success or error message
        """
        try:
            # T033: Handle Missing Models Gracefully
            metadata = self.model_registry.get_model_metadata(model_id)
            if not metadata:
                # List available models in error message
                available_models = [m.name for m in self.models[:5]]  # Show first 5
                available_msg = ", ".join(available_models)
                if len(self.models) > 5:
                    available_msg += f" (and {len(self.models) - 5} more)"
                
                return (
                    False,
                    f"Model '{model_id}' not found in registry.\n"
                    f"Available models: {available_msg}\n"
                    "Run 'vertex-spec models list' to see all available models.",
                )
            
            # Get current config
            try:
                config = self.config_manager.load_config()
                project_id = config.project_id
                old_model_id = config.model
            except ConfigurationError:
                # No config exists, create default
                project_id = "default-project"
                old_model_id = None
                config = self.config_manager.create_default_config(project_id=project_id)
            
            # Get model region (use default if not specified)
            region = metadata.default_region or config.region or "us-central1"
            
            # Validate model availability in region
            try:
                self.model_registry.validate_model_availability(model_id, region)
            except ModelNotFoundError as e:
                # T033, T037: Handle Missing Models with helpful message
                error_msg = f"[red]✗ Model not available in region[/red]\n"
                error_msg += f"[yellow]Model:[/yellow] {model_id}\n"
                error_msg += f"[yellow]Requested region:[/yellow] {region}\n"
                
                if e.available_regions:
                    error_msg += f"[yellow]Available regions:[/yellow] {', '.join(e.available_regions)}\n"
                    error_msg += f"\n[yellow]Suggested fix:[/yellow]\n"
                    error_msg += f"  Use one of these regions: {', '.join(e.available_regions)}\n"
                
                error_msg += "\n[yellow]Troubleshooting steps:[/yellow]\n"
                error_msg += "  1. Verify model is available in your GCP project\n"
                error_msg += "  2. Check Vertex AI API is enabled in the region\n"
                error_msg += "  3. Run 'vertex-spec models list --region <region>' to verify\n"
                
                return (False, error_msg)
            
            # Switch model using VertexAIClient (T023)
            try:
                # T034: Handle Authentication Errors - Check gcloud CLI first
                try:
                    import subprocess
                    result = subprocess.run(
                        ["gcloud", "--version"],
                        capture_output=True,
                        timeout=5,
                    )
                    if result.returncode != 0:
                        raise FileNotFoundError("gcloud CLI not found")
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    return (
                        False,
                        "gcloud CLI not installed or not in PATH.\n"
                        "Installation instructions:\n"
                        "  • macOS: brew install google-cloud-sdk\n"
                        "  • Linux: See https://cloud.google.com/sdk/docs/install\n"
                        "  • Windows: See https://cloud.google.com/sdk/docs/install\n"
                        "\nAfter installation, run 'gcloud auth login' to authenticate.",
                    )
                
                # Initialize authentication
                auth_manager = AuthenticationManager()
                credentials = auth_manager.get_credentials(config.auth_method)
                
                # Create or update client
                client = VertexAIClient(
                    project_id=project_id,
                    region=region,
                    model_id=model_id,
                    model_version=metadata.latest_version,
                    credentials=credentials,
                    config=config,
                )
                
                # Update configuration (T024: Configuration Update)
                config.model = model_id
                config.region = region
                if metadata.latest_version:
                    config.model_version = metadata.latest_version
                
                # Save configuration (T025: Selection Persistence)
                try:
                    self.config_manager.save_config(config)
                except ConfigurationError as e:
                    # T037: Add Helpful Error Messages for config errors
                    config_path = self.config_manager.config_path
                    error_msg = f"[red]✗ Failed to save configuration[/red]\n"
                    error_msg += f"[yellow]Error:[/yellow] {e.message}\n"
                    error_msg += f"[yellow]Config file:[/yellow] {config_path}\n"
                    
                    if e.suggested_fix:
                        error_msg += f"\n[yellow]Suggested fix:[/yellow]\n"
                        error_msg += f"  {e.suggested_fix}\n"
                    
                    error_msg += "\n[yellow]Troubleshooting steps:[/yellow]\n"
                    error_msg += "  1. Check file permissions on config directory\n"
                    error_msg += "  2. Verify disk space is available\n"
                    error_msg += "  3. Check if file is locked by another process\n"
                    error_msg += f"  4. Try manually editing: {config_path}\n"
                    
                    return (False, error_msg)
                
                # Update current model ID
                self.current_model_id = model_id
                
                return (
                    True,
                    f"Successfully switched to '{metadata.name}' ({model_id}) in region '{region}'",
                )
            
            except AuthenticationError as e:
                # T034, T037: Handle Authentication Errors with helpful messages
                error_msg = f"[red]✗ Authentication failed[/red]\n"
                error_msg += f"[yellow]Error:[/yellow] {e.message}\n"
                
                if e.suggested_fix:
                    error_msg += f"\n[yellow]Suggested fix:[/yellow]\n"
                    error_msg += f"  {e.suggested_fix}\n"
                
                error_msg += "\n[yellow]Troubleshooting steps:[/yellow]\n"
                error_msg += "  1. Run 'gcloud auth login' to authenticate\n"
                error_msg += "  2. Verify 'gcloud auth print-access-token' works\n"
                error_msg += "  3. Check GOOGLE_APPLICATION_CREDENTIALS if using service account\n"
                error_msg += "  4. Verify your GCP project has Vertex AI API enabled\n"
                
                return (False, error_msg)
            except APIError as e:
                # T037: Add Helpful Error Messages with troubleshooting
                error_msg = f"[red]✗ Failed to switch model[/red]\n"
                error_msg += f"[yellow]Error:[/yellow] {e.message}\n"
                
                if e.suggested_fix:
                    error_msg += f"\n[yellow]Suggested fix:[/yellow]\n"
                    error_msg += f"  {e.suggested_fix}\n"
                
                if e.troubleshooting_steps:
                    error_msg += "\n[yellow]Troubleshooting steps:[/yellow]\n"
                    for i, step in enumerate(e.troubleshooting_steps, 1):
                        error_msg += f"  {i}. {step}\n"
                
                return (False, error_msg)
            except Exception as e:
                return (
                    False,
                    f"Unexpected error during model switch: {str(e)}",
                )
        
        except Exception as e:
            return (
                False,
                f"Error switching model: {str(e)}",
            )
    
    def run_with_switch(self) -> Optional[str]:
        """
        Run interactive menu and switch model if selected.
        
        Returns:
            Selected model ID if switch succeeded, None if cancelled or failed.
        """
        selected_model_id = self.run()
        
        if not selected_model_id:
            return None
        
        # Switch model (T023, T024, T025)
        success, message = self._switch_model(selected_model_id)
        
        # T037: Show feedback with Rich formatting (T026: Success/Error Feedback)
        if success:
            self.console.print(f"\n[bold green]✓ {message}[/bold green]")
            return selected_model_id
        else:
            # Error message already formatted with Rich markup
            self.console.print(f"\n{message}")
            self.console.print(
                "[yellow]⚠ Model switch failed. Current model unchanged.[/yellow]"
            )
            return None

