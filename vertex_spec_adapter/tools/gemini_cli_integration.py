"""Integration helper untuk Gemini CLI."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool


def register_tool_to_gemini_cli(
    tool: VertexAdapterTool,
    gemini_config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Register Vertex Adapter Tool ke Gemini CLI configuration.
    
    Args:
        tool: VertexAdapterTool instance
        gemini_config_path: Path to Gemini CLI config file
    
    Returns:
        Registration result
    """
    # Default Gemini CLI config locations
    if not gemini_config_path:
        home = Path.home()
        gemini_config_path = home / ".gemini" / "config.json"
    
    config_path = Path(gemini_config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {"tools": []}
    
    # Add tool if not already registered
    tool_config = {
        "name": tool.name,
        "type": "function",
        "schema": tool.schema,
        "handler": "vertex_spec_adapter.tools.vertex_adapter_tool:VertexAdapterTool.execute",
    }
    
    # Check if already registered
    existing_tools = [t for t in config.get("tools", []) if t.get("name") == tool.name]
    if existing_tools:
        return {
            "success": True,
            "message": f"Tool '{tool.name}' already registered",
            "config_path": str(config_path),
        }
    
    # Add tool
    if "tools" not in config:
        config["tools"] = []
    config["tools"].append(tool_config)
    
    # Save config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    return {
        "success": True,
        "message": f"Tool '{tool.name}' registered successfully",
        "config_path": str(config_path),
        "tool": tool_config,
    }


def create_gemini_cli_wrapper_script(output_path: str = "gemini-vertex-wrapper.py") -> str:
    """
    Create wrapper script untuk Gemini CLI yang menggunakan Vertex Adapter.
    
    Args:
        output_path: Path untuk save wrapper script
    
    Returns:
        Path to created script
    """
    script_content = '''#!/usr/bin/env python3
"""
Wrapper script untuk menggunakan Vertex Adapter dengan Gemini CLI.
Usage: python gemini-vertex-wrapper.py <gemini-cli-command>
"""

import sys
import subprocess
from pathlib import Path

from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool
from vertex_spec_adapter.tools.gemini_cli_integration import register_tool_to_gemini_cli


def main():
    """Main entry point."""
    # Create and register tool
    tool = VertexAdapterTool()
    
    # Register to Gemini CLI
    result = register_tool_to_gemini_cli(tool)
    print(f"✓ {result['message']}")
    print(f"  Config: {result['config_path']}")
    
    # Execute Gemini CLI command if provided
    if len(sys.argv) > 1:
        gemini_cmd = sys.argv[1:]
        subprocess.run(["gemini"] + gemini_cmd)
    else:
        print("\\nUsage: python gemini-vertex-wrapper.py <gemini-command>")
        print("Example: python gemini-vertex-wrapper.py 'List available models'")


if __name__ == "__main__":
    main()
'''
    
    script_path = Path(output_path)
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    
    return str(script_path)

