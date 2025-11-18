#!/usr/bin/env python3
"""Quick test script untuk integrasi Gemini."""

from vertex_spec_adapter.core.client import VertexAIClient
from vertex_spec_adapter.core.config import ConfigurationManager

def test_gemini():
    """Test Gemini integration."""
    try:
        # Load config
        config_manager = ConfigurationManager()
        config = config_manager.load_config()
        
        print("✓ Configuration loaded")
        
        # Initialize Gemini client
        client = VertexAIClient(
            project_id=config.project_id,
            region=config.region,
            model_id="gemini-2-5-pro",
            config=config,
        )
        
        print("✓ Gemini client initialized")
        
        # Test generation
        messages = [
            {"role": "user", "content": "Hello! Can you introduce yourself?"}
        ]
        
        print("Generating response...")
        response = client.generate(messages, temperature=0.7)
        
        print(f"\n✓ Response received:")
        print(response)
        print(f"\nToken usage: {client.token_usage}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        if hasattr(e, 'troubleshooting_steps'):
            print("\nTroubleshooting steps:")
            for step in e.troubleshooting_steps:
                print(f"  - {step}")

if __name__ == "__main__":
    test_gemini()
