#!/usr/bin/env python3
"""
Test script to verify the chatbot package is working correctly.
"""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test our modules
        from oci_genai_chatbot import OCIGenAIChatBot
        from oci_genai_chatbot.cli import main as cli_main
        print("✅ Package imports successful")
        
        # Test LiteLLM with OCI GenAI
        import litellm
        from litellm.types.utils import LlmProviders
        
        if hasattr(LlmProviders, 'OCI_GENAI'):
            print("✅ LiteLLM with OCI GenAI support detected")
        else:
            print("❌ OCI GenAI support not found in LiteLLM")
            return False
        
        # Test OCI SDK
        import oci
        print("✅ OCI SDK import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_oci_config():
    """Test OCI configuration."""
    print("\n🔧 Testing OCI configuration...")
    
    try:
        import oci
        
        # Check config file
        config_file = os.path.expanduser("~/.oci/config")
        if os.path.exists(config_file):
            print("✅ OCI config file found")
        else:
            print("⚠️ OCI config file not found at ~/.oci/config")
        
        # Try to load config
        try:
            config = oci.config.from_file()
            required_keys = ["user", "tenancy", "fingerprint", "key_file", "region"]
            missing_keys = [key for key in required_keys if not config.get(key)]
            
            if missing_keys:
                print(f"⚠️ Missing config keys: {missing_keys}")
            else:
                print("✅ OCI config appears valid")
                
        except Exception as e:
            print(f"⚠️ Error loading OCI config: {e}")
        
        # Check compartment ID
        compartment_id = os.getenv("OCI_COMPARTMENT_ID")
        if compartment_id:
            print("✅ OCI_COMPARTMENT_ID environment variable set")
        else:
            print("⚠️ OCI_COMPARTMENT_ID environment variable not set")
        
        return True
        
    except Exception as e:
        print(f"❌ OCI configuration error: {e}")
        return False

def test_chatbot_init():
    """Test chatbot initialization (without making API calls)."""
    print("\n🤖 Testing chatbot initialization...")
    
    compartment_id = os.getenv("OCI_COMPARTMENT_ID")
    if not compartment_id:
        print("⚠️ Skipping chatbot test - OCI_COMPARTMENT_ID not set")
        return True
    
    try:
        from oci_genai_chatbot import OCIGenAIChatBot
        
        # This should validate config but not make API calls
        bot = OCIGenAIChatBot(
            model="cohere.command-r-plus",
            temperature=0.7,
            max_tokens=100,
            compartment_id=compartment_id
        )
        
        print("✅ Chatbot initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {e}")
        return False

def test_cli_import():
    """Test CLI module import."""
    print("\n💻 Testing CLI import...")
    
    try:
        from oci_genai_chatbot.cli import main
        print("✅ CLI import successful")
        
        # Test that we can import click
        import click
        print("✅ Click import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False

def test_streamlit_import():
    """Test Streamlit app import."""
    print("\n🌐 Testing Streamlit app import...")
    
    try:
        from oci_genai_chatbot.streamlit_app import main
        print("✅ Streamlit app import successful")
        
        # Test that we can import streamlit
        import streamlit
        print("✅ Streamlit import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 OCI GenAI Chatbot Setup Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("OCI Configuration", test_oci_config),
        ("CLI Import", test_cli_import),
        ("Streamlit Import", test_streamlit_import),
        ("Chatbot Initialization", test_chatbot_init),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set OCI_COMPARTMENT_ID if not already set")
        print("2. Try: python demo.py")
        print("3. Try: python -m oci_genai_chatbot.cli config")
        print("4. Try: python run_streamlit.py")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the issues above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())