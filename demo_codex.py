#!/usr/bin/env python3
"""
Demo script to showcase the Codex-style CLI interface.
"""

import os
import sys

# Add src to path so we can import our modules
sys.path.insert(0, 'src')

from oci_genai_chatbot.codex_cli import CodexInterface

def main():
    """Run a demo of the Codex interface."""
    print("=== OCI GenAI Codex-style CLI Demo ===\n")
    
    # Create interface in demo mode
    interface = CodexInterface(demo=True, mode="code")
    
    if not interface.initialize():
        return
    
    interface.show_startup_banner()
    
    # Simulate some interactions
    test_commands = [
        "/help",
        "Write a Python function to calculate fibonacci numbers",
        "/mode explain",
        "How does recursion work?",
        "/mode debug",
        "My code has an infinite loop",
        "/history",
        "/exit"
    ]
    
    print("Demo commands that will be processed:")
    for cmd in test_commands:
        print(f"  > {cmd}")
    print("\nStarting demo...\n")
    
    for command in test_commands:
        print(f"[cyan]>[/cyan] {command}")
        
        # Process command
        if interface.process_command(command) == "exit":
            break
        elif interface.process_command(command):
            continue
        else:
            # Regular input - get response
            response = interface.stream_response(command)
            interface.session_history.append({
                "prompt": command,
                "response": response,
                "mode": interface.mode,
                "timestamp": 0
            })
        
        print()

if __name__ == "__main__":
    main()