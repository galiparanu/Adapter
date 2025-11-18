"""Entry point for Gemini CLI /model command execution."""

import sys
from pathlib import Path
from typing import List, Optional

from vertex_spec_adapter.cli.commands.model_interactive import ModelInteractiveMenu


def parse_args(args: Optional[List[str]]) -> dict:
    """
    Parse command arguments from Gemini CLI.
    
    Args:
        args: Command arguments from Gemini CLI
    
    Returns:
        Dictionary with parsed arguments
    
    Current Behavior:
    - If no args: Show interactive menu
    - If args provided: Can be used for future non-interactive mode
    """
    if not args:
        return {"interactive": True}
    
    # Parse arguments (future: support --list, --switch, --info)
    parsed = {"interactive": True}
    
    # For now, any arguments trigger interactive mode
    # Future: Parse --list, --switch MODEL_ID, --info MODEL_ID
    if args:
        # Check for flags
        if "--list" in args:
            parsed["list"] = True
            parsed["interactive"] = False
        elif "--switch" in args:
            idx = args.index("--switch")
            if idx + 1 < len(args):
                parsed["switch"] = args[idx + 1]
                parsed["interactive"] = False
        elif "--info" in args:
            idx = args.index("--info")
            if idx + 1 < len(args):
                parsed["info"] = args[idx + 1]
                parsed["interactive"] = False
    
    return parsed


def main(args: Optional[List[str]] = None) -> None:
    """
    Entry point for Gemini CLI command execution.
    
    Args:
        args: Command arguments from Gemini CLI
    """
    try:
        # Parse arguments
        parsed_args = parse_args(args)
        
        # Create menu
        menu = ModelInteractiveMenu()
        
        # Execute based on arguments
        if parsed_args.get("interactive", True):
            # Interactive mode: show menu and switch
            result = menu.run_with_switch()
            if result:
                sys.exit(0)
            else:
                sys.exit(1)
        elif parsed_args.get("list"):
            # Future: List models (non-interactive)
            # For now, fall back to interactive
            result = menu.run_with_switch()
            sys.exit(0 if result else 1)
        elif parsed_args.get("switch"):
            # Future: Switch model (non-interactive)
            model_id = parsed_args["switch"]
            success, message = menu._switch_model(model_id)
            if success:
                print(message)
                sys.exit(0)
            else:
                print(f"Error: {message}", file=sys.stderr)
                sys.exit(1)
        elif parsed_args.get("info"):
            # Future: Show model info (non-interactive)
            model_id = parsed_args["info"]
            metadata = menu.model_registry.get_model_metadata(model_id)
            if metadata:
                print(f"Model: {metadata.name} ({metadata.model_id})")
                if metadata.description:
                    print(f"Description: {metadata.description}")
                sys.exit(0)
            else:
                print(f"Error: Model '{model_id}' not found", file=sys.stderr)
                sys.exit(1)
        else:
            # Default: interactive mode
            result = menu.run_with_switch()
            sys.exit(0 if result else 1)
    
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:] if len(sys.argv) > 1 else None)

