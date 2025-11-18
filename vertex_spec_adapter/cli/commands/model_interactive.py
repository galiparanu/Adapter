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
        
        # Load available models
        models_dict = self.model_registry.get_available_models(
            project_id=project_id,
            region=None,
            use_cache=True,
        )
        
        # Convert dicts to ModelMetadata objects
        self.models: List[ModelMetadata] = []
        for model_dict in models_dict:
            model_id = model_dict.get("id")
            if model_id:
                metadata = self.model_registry.get_model_metadata(model_id)
                if metadata:
                    self.models.append(metadata)
        
        # Sort models alphabetically by name (per FR-004)
        self.models.sort(key=lambda m: m.name.lower())
        
        # Menu state
        self.selected_index = 0
        self.hover_details_model_id: Optional[str] = None
        
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
        
        Returns:
            Rich Layout object ready for display
        """
        # Create layout
        layout = Layout()
        
        # Top panel: Current model indicator
        current_model_text = self._format_current_model()
        layout.split_column(
            Layout(Panel(current_model_text, border_style="cyan"), size=3, name="header"),
            Layout(name="body"),
        )
        
        # Body: Split into left (model list) and right (hover details)
        layout["body"].split_row(
            Layout(name="model_list", ratio=1),
            Layout(name="hover_details", ratio=1),
        )
        
        # Model list panel
        model_list_text = self._format_model_list()
        layout["model_list"].update(Panel(model_list_text, title="Available Models", border_style="blue"))
        
        # Hover details panel
        hover_details_text = self._format_hover_details()
        layout["hover_details"].update(Panel(hover_details_text, title="Model Information", border_style="green"))
        
        return layout
    
    def _format_current_model(self) -> Text:
        """
        Format current model display for top panel.
        
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
                text.append("Current Model: ", style="bold")
                text.append(f"{current_model.name} ", style="bold cyan")
                text.append(f"({current_model.model_id})", style="dim")
            else:
                text.append("Current Model: ", style="bold")
                text.append(f"{self.current_model_id} ", style="yellow")
                text.append("(not in available models)", style="dim red")
        else:
            text.append("Current Model: ", style="bold")
            text.append("None", style="dim")
        
        return text
    
    def _format_model_list(self) -> Text:
        """
        Format model list for left panel.
        
        Returns:
            Rich Text object with model list
        """
        text = Text()
        
        if not self.models:
            text.append("No models available", style="red")
            return text
        
        for i, model in enumerate(self.models):
            # Selection indicator
            if i == self.selected_index:
                text.append("▶ ", style="bold green")  # Selection indicator
            else:
                text.append("  ")
            
            # Current model indicator
            if model.model_id.lower() == (self.current_model_id or "").lower():
                text.append("✓ ", style="bold yellow")
            else:
                text.append("  ")
            
            # Model name
            if i == self.selected_index:
                text.append(model.name, style="bold white on blue")
            else:
                text.append(model.name, style="white")
            
            text.append("\n")
        
        return text
    
    def _format_hover_details(self) -> Text:
        """
        Format model metadata for hover details display.
        
        Returns:
            Rich Text object with formatted model information
        """
        text = Text()
        
        if not self.hover_details_model_id:
            text.append("Select a model to see details", style="dim")
            return text
        
        # Find model
        model = None
        for m in self.models:
            if m.model_id == self.hover_details_model_id:
                model = m
                break
        
        if not model:
            text.append("Model not found", style="red")
            return text
        
        # Model Name & ID
        text.append("Model: ", style="bold")
        text.append(f"{model.name}\n", style="cyan")
        text.append(f"ID: {model.model_id}\n\n", style="dim")
        
        # Context Window
        if model.context_window:
            text.append("Context Window: ", style="bold")
            text.append(f"{model.context_window}\n", style="white")
        else:
            text.append("Context Window: ", style="bold")
            text.append("N/A\n", style="dim")
        
        # Pricing
        if model.pricing:
            text.append("\nPricing:\n", style="bold")
            if "input" in model.pricing:
                text.append(f"  Input:  ${model.pricing['input']:.4f}/1K tokens\n", style="white")
            if "output" in model.pricing:
                text.append(f"  Output: ${model.pricing['output']:.4f}/1K tokens\n", style="white")
        else:
            text.append("\nPricing: ", style="bold")
            text.append("N/A\n", style="dim")
        
        # Capabilities
        if model.capabilities:
            text.append("\nCapabilities:\n", style="bold")
            for cap in model.capabilities:
                text.append(f"  • {cap}\n", style="white")
        else:
            text.append("\nCapabilities: ", style="bold")
            text.append("N/A\n", style="dim")
        
        # Status
        text.append("\nStatus: ", style="bold")
        if model.model_id.lower() == (self.current_model_id or "").lower():
            text.append("✓ Active\n", style="bold green")
        else:
            text.append("Available\n", style="green")
        
        # Description
        if model.description:
            text.append("\nDescription:\n", style="bold")
            # Wrap description if too long (max 40 chars per line per FR-002)
            desc_lines = self._wrap_text(model.description, width=40)
            for line in desc_lines:
                text.append(f"  {line}\n", style="white")
        else:
            text.append("\nDescription: ", style="bold")
            text.append("N/A\n", style="dim")
        
        return text
    
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
        Check if terminal supports required features.
        
        Returns:
            True if terminal supports alternate screen, False otherwise
        """
        return self.console.is_terminal
    
    def _simple_text_menu(self) -> Optional[str]:
        """
        Simple text-based menu fallback for unsupported terminals.
        
        Returns:
            Selected model ID or None
        """
        if not self.models:
            self.console.print("[red]No models available[/red]")
            return None
        
        self.console.print("\n[bold]Available Models:[/bold]\n")
        for i, model in enumerate(self.models):
            current_marker = " (current)" if model.model_id.lower() == (self.current_model_id or "").lower() else ""
            self.console.print(f"  {i + 1}. {model.name}{current_marker}")
        
        try:
            choice = self.console.input("\n[bold]Select model number (or 'q' to cancel): [/bold]")
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(self.models):
                return self.models[index].model_id
            else:
                self.console.print("[red]Invalid selection[/red]")
                return None
        except (ValueError, KeyboardInterrupt):
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
        
        # Check if we have models
        if not self.models:
            self.console.print("[red]No models available. Check ModelRegistry connection.[/red]")
            return None
        
        # Use Rich Live for real-time updates
        try:
            with Live(self._render_menu(), refresh_per_second=10, screen=True) as live:
                # Main event loop
                while True:
                    try:
                        key = self._get_key()
                        
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
                        return None
        except KeyboardInterrupt:
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
            # Validate model exists
            metadata = self.model_registry.get_model_metadata(model_id)
            if not metadata:
                return (
                    False,
                    f"Model '{model_id}' not found in registry. Please check available models.",
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
                return (
                    False,
                    f"Model '{model_id}' not available in region '{region}'. "
                    f"Available regions: {', '.join(metadata.available_regions)}",
                )
            
            # Switch model using VertexAIClient (T023)
            try:
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
                    return (
                        False,
                        f"Failed to save configuration: {str(e)}. "
                        "Please check file permissions and try again.",
                    )
                
                # Update current model ID
                self.current_model_id = model_id
                
                return (
                    True,
                    f"Successfully switched to '{metadata.name}' ({model_id}) in region '{region}'",
                )
            
            except AuthenticationError as e:
                return (
                    False,
                    f"Authentication failed: {str(e)}. "
                    "Please check your credentials and try again.",
                )
            except APIError as e:
                return (
                    False,
                    f"Failed to switch model: {str(e)}. "
                    "Please check your configuration and try again.",
                )
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
        
        # Show feedback (T026: Success/Error Feedback)
        if success:
            self.console.print(f"\n[bold green]✓ {message}[/bold green]")
            return selected_model_id
        else:
            self.console.print(f"\n[bold red]✗ {message}[/bold red]")
            self.console.print(
                "[yellow]Model switch failed. Current model unchanged.[/yellow]"
            )
            return None

