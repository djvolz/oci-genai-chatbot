#!/usr/bin/env python3
"""
Demo script showing OCI GenAI integration with LiteLLM.
"""

import os
import sys

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from oci_genai_chatbot.litellm_client import OCIGenAIChatBot

def demo_chat():
    """Demonstrate chat functionality."""
    print("🤖 OCI GenAI Chat Demo")
    print("=" * 40)
    
    # Check if we have OCI config
    compartment_id = os.getenv("OCI_COMPARTMENT_ID")
    if not compartment_id:
        print("❌ Error: OCI_COMPARTMENT_ID environment variable not set")
        print("Please set it to your OCI compartment OCID")
        return
    
    try:
        # Initialize chatbot
        print("Initializing chatbot...")
        bot = OCIGenAIChatBot(
            model="cohere.command-r-plus",
            temperature=0.7,
            max_tokens=200,
            compartment_id=compartment_id
        )
        print("✅ Chatbot initialized successfully!")
        
        # Test messages
        test_messages = [
            "Hello! Please introduce yourself briefly.",
            "What can you help me with?",
            "Tell me a fun fact about Oracle Cloud."
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n👤 User {i}: {message}")
            
            try:
                response = bot.chat(message)
                print(f"🤖 Bot {i}: {response}")
            except Exception as e:
                print(f"❌ Error in chat {i}: {e}")
        
        print("\n✅ Chat demo completed!")
        
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        print("\nPlease check:")
        print("1. OCI config file exists at ~/.oci/config")
        print("2. OCI_COMPARTMENT_ID environment variable is set")
        print("3. You have access to OCI GenAI service")

def demo_embedding():
    """Demonstrate embedding functionality."""
    print("\n🔢 OCI GenAI Embedding Demo")
    print("=" * 40)
    
    compartment_id = os.getenv("OCI_COMPARTMENT_ID")
    if not compartment_id:
        print("❌ Error: OCI_COMPARTMENT_ID environment variable not set")
        return
    
    try:
        # Initialize chatbot for embedding
        print("Initializing embedding client...")
        bot = OCIGenAIChatBot(compartment_id=compartment_id)
        print("✅ Embedding client initialized!")
        
        # Test texts
        test_texts = [
            "Hello, world!",
            "Oracle Cloud Infrastructure is awesome!",
            "LiteLLM makes AI integration easy."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 Text {i}: {text}")
            
            try:
                embedding = bot.embedding(text)
                print(f"✅ Generated {len(embedding)}-dimensional embedding")
                print(f"First 5 values: {embedding[:5]}")
                
                # Calculate magnitude
                magnitude = sum(x**2 for x in embedding) ** 0.5
                print(f"Magnitude: {magnitude:.6f}")
                
            except Exception as e:
                print(f"❌ Error generating embedding {i}: {e}")
        
        print("\n✅ Embedding demo completed!")
        
    except Exception as e:
        print(f"❌ Error in embedding demo: {e}")

def main():
    """Run all demos."""
    print("🚀 OCI GenAI + LiteLLM Integration Demo")
    print("=" * 50)
    
    # Check if we're using the fork
    try:
        import litellm
        from litellm.types.utils import LlmProviders
        
        if hasattr(LlmProviders, 'OCI_GENAI'):
            print("✅ LiteLLM with OCI GenAI support detected!")
        else:
            print("❌ OCI GenAI support not found in LiteLLM")
            print("Please install: pip install git+https://github.com/djvolz/litellm.git")
            return
            
    except ImportError as e:
        print(f"❌ Error importing LiteLLM: {e}")
        return
    
    # Run demos
    try:
        demo_chat()
        demo_embedding()
        
        print("\n🎉 All demos completed!")
        print("\nNext steps:")
        print("1. Try the CLI: chatbot-cli chat")
        print("2. Launch web app: python run_streamlit.py")
        print("3. Explore the API in your own scripts")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()