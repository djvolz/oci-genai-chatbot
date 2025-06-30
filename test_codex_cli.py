#!/usr/bin/env python3
"""
Test script for the Codex-style CLI interface.
"""

import sys
import subprocess

def test_codex_cli_help():
    """Test the Codex CLI help command."""
    print("Testing Codex CLI help...")
    result = subprocess.run([
        sys.executable, "-m", "oci_genai_chatbot.codex_cli", "--help"
    ], capture_output=True, text=True, cwd="src")
    
    assert result.returncode == 0
    assert "oci-genai - Codex-inspired AI coding assistant" in result.stdout
    assert "--mode" in result.stdout
    assert "--demo" in result.stdout
    print("✓ Codex CLI help works")

def test_codex_cli_one_shot_demo():
    """Test one-shot demo mode."""
    print("Testing Codex CLI one-shot demo mode...")
    result = subprocess.run([
        sys.executable, "-m", "oci_genai_chatbot.codex_cli", 
        "--demo", "--one-shot", "test command", "--mode", "code"
    ], capture_output=True, text=True, cwd="src")
    
    assert result.returncode == 0
    assert "Running in demo mode" in result.stdout
    assert "```python" in result.stdout
    print("✓ Codex CLI one-shot demo works")

def test_script_entry_points():
    """Test that the script entry points are properly configured."""
    print("Testing script entry points...")
    
    # Test oci-genai command
    result = subprocess.run(["uv", "run", "oci-genai", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "oci-genai - Codex-inspired AI coding assistant" in result.stdout
    
    # Test chatbot-cli command  
    result = subprocess.run(["uv", "run", "chatbot-cli", "--help"],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "OCI GenAI Chatbot - Powered by LiteLLM" in result.stdout
    
    print("✓ Both CLI entry points work")

def test_codex_interface_import():
    """Test importing the CodexInterface class."""
    print("Testing CodexInterface import...")
    
    # Add src to path
    import os
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
    
    from oci_genai_chatbot.codex_cli import CodexInterface
    
    # Test creating interface
    interface = CodexInterface(demo=True)
    assert interface.demo == True
    assert interface.mode == "suggest"
    assert "suggest" in interface.system_prompts
    
    print("✓ CodexInterface import and initialization works")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Codex-Style CLI Implementation")
    print("=" * 60)
    
    tests = [
        test_codex_interface_import,
        test_codex_cli_help,
        test_codex_cli_one_shot_demo,
        test_script_entry_points,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Codex CLI tests passed!")
        print("\n✨ Codex-style interface features verified:")
        print("  • CLI entry points working")
        print("  • Demo mode functioning")
        print("  • Help system operational")
        print("  • Class imports successful")
        print("  • One-shot command execution")
    else:
        print(f"⚠️  {total - passed} tests failed.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)