#!/usr/bin/env python3
"""Script untuk register Vertex Adapter Tool ke Gemini CLI."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vertex_spec_adapter.tools.vertex_adapter_tool import VertexAdapterTool
from vertex_spec_adapter.tools.gemini_cli_integration import register_tool_to_gemini_cli


def main():
    """Main entry point."""
    print("Registering Vertex Adapter Tool to Gemini CLI...")
    print()
    
    # Check config
    config_path = Path(".specify/config.yaml")
    if not config_path.exists():
        print("⚠ Warning: .specify/config.yaml not found")
        print("  Tool will use default configuration")
        print("  Run 'vertex-spec init' to create config")
        print()
    
    # Create tool
    try:
        tool = VertexAdapterTool()
        print(f"✓ Tool created: {tool.name}")
        print(f"  Description: {tool.description}")
    except Exception as e:
        print(f"✗ Failed to create tool: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure .specify/config.yaml exists")
        print("  2. Run 'vertex-spec test' to verify configuration")
        return 1
    
    # Register tool
    try:
        result = register_tool_to_gemini_cli(tool)
        
        if result["success"]:
            print(f"✓ {result['message']}")
            print(f"  Config saved to: {result['config_path']}")
            print()
            print("🎉 Vertex Adapter Tool is now available in Gemini CLI!")
            print()
            print("Usage examples:")
            print("  gemini 'Use vertex_adapter to list available models'")
            print("  gemini 'Generate code using vertex_adapter with gemini-2-5-pro'")
            print("  gemini 'Switch to claude-4-5-sonnet using vertex_adapter'")
            return 0
        else:
            print(f"✗ Registration failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"✗ Registration failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure Gemini CLI is installed")
        print("  2. Check write permissions for ~/.gemini/ directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())

