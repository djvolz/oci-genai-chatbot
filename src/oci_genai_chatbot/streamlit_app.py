"""
Streamlit web application for OCI GenAI Chatbot.
"""

import streamlit as st
import os
import time
from typing import Dict, Any

from .litellm_client import OCIGenAIChatBot, AVAILABLE_CHAT_MODELS, AVAILABLE_EMBEDDING_MODELS


def init_session_state():
    """Initialize Streamlit session state."""
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "config" not in st.session_state:
        st.session_state.config = {
            "model": "cohere.command-r-plus",
            "temperature": 0.7,
            "max_tokens": 500,
            "system_prompt": "",
            "compartment_id": os.getenv("OCI_COMPARTMENT_ID", "")
        }


def sidebar_config():
    """Render sidebar configuration."""
    st.sidebar.title("🤖 Chatbot Settings")
    
    # Model selection
    model = st.sidebar.selectbox(
        "Select Model",
        AVAILABLE_CHAT_MODELS,
        index=AVAILABLE_CHAT_MODELS.index(st.session_state.config["model"])
    )
    
    # Temperature slider
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.config["temperature"],
        step=0.1,
        help="Controls randomness in responses. Lower = more focused, Higher = more creative"
    )
    
    # Max tokens
    max_tokens = st.sidebar.number_input(
        "Max Tokens",
        min_value=50,
        max_value=2000,
        value=st.session_state.config["max_tokens"],
        step=50,
        help="Maximum number of tokens to generate"
    )
    
    # System prompt
    system_prompt = st.sidebar.text_area(
        "System Prompt (optional)",
        value=st.session_state.config["system_prompt"],
        height=100,
        help="Set context or instructions for the AI assistant"
    )
    
    # Compartment ID
    compartment_id = st.sidebar.text_input(
        "OCI Compartment ID",
        value=st.session_state.config["compartment_id"],
        type="password",
        help="Your OCI compartment OCID"
    )
    
    # Update config if changed
    new_config = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt,
        "compartment_id": compartment_id
    }
    
    config_changed = new_config != st.session_state.config
    st.session_state.config = new_config
    
    # Initialize/reinitialize chatbot if config changed
    if config_changed or st.session_state.chatbot is None:
        if compartment_id:
            try:
                with st.spinner("Initializing chatbot..."):
                    st.session_state.chatbot = OCIGenAIChatBot(
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        compartment_id=compartment_id
                    )
                st.sidebar.success("✅ Chatbot initialized!")
            except Exception as e:
                st.sidebar.error(f"❌ Failed to initialize: {str(e)}")
                st.session_state.chatbot = None
        else:
            st.sidebar.warning("⚠️ Please enter your OCI Compartment ID")
            st.session_state.chatbot = None
    
    # Control buttons
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.chatbot:
            st.session_state.chatbot.reset_conversation()
        st.rerun()
    
    if st.sidebar.button("🧪 Test Connection", use_container_width=True):
        test_connection()


def test_connection():
    """Test OCI GenAI connection."""
    try:
        if not st.session_state.chatbot:
            st.sidebar.error("❌ Chatbot not initialized")
            return
        
        with st.sidebar.container():
            with st.spinner("Testing connection..."):
                response = st.session_state.chatbot.chat("Hello! Please respond with just 'Hi'.")
            
            if "error" in response.lower():
                st.sidebar.error(f"❌ Connection failed: {response}")
            else:
                st.sidebar.success("✅ Connection successful!")
                
    except Exception as e:
        st.sidebar.error(f"❌ Connection test failed: {str(e)}")


def main_chat_interface():
    """Render main chat interface."""
    st.title("🤖 OCI GenAI Chatbot")
    st.markdown("*Powered by LiteLLM + Oracle Cloud Infrastructure GenAI*")
    
    # Display current model info
    if st.session_state.chatbot:
        st.info(f"💬 Using model: **{st.session_state.config['model']}** | "
                f"🌡️ Temperature: **{st.session_state.config['temperature']}** | "
                f"🎯 Max tokens: **{st.session_state.config['max_tokens']}**")
    else:
        st.warning("⚠️ Please configure your settings in the sidebar to start chatting.")
        return
    
    # Chat messages container
    chat_container = st.container()
    
    with chat_container:
        # Display conversation history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here...", disabled=not st.session_state.chatbot):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        system_prompt = st.session_state.config["system_prompt"] if st.session_state.config["system_prompt"] else None
                        response = st.session_state.chatbot.chat(prompt, system_prompt)
                        
                        if response.startswith("Error:"):
                            st.error(response)
                        else:
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def embedding_page():
    """Render embedding generation page."""
    st.title("🔢 Text Embeddings")
    st.markdown("*Generate embeddings using OCI GenAI*")
    
    # Embedding model selection
    embedding_model = st.selectbox(
        "Select Embedding Model",
        AVAILABLE_EMBEDDING_MODELS,
        help="Choose the embedding model to use"
    )
    
    # Text input
    text_input = st.text_area(
        "Text to Embed",
        height=150,
        placeholder="Enter the text you want to generate embeddings for..."
    )
    
    # Compartment ID
    compartment_id = st.text_input(
        "OCI Compartment ID",
        value=os.getenv("OCI_COMPARTMENT_ID", ""),
        type="password",
        help="Your OCI compartment OCID"
    )
    
    if st.button("Generate Embedding", type="primary", disabled=not text_input or not compartment_id):
        try:
            with st.spinner("Generating embedding..."):
                # Initialize chatbot for embedding
                bot = OCIGenAIChatBot(compartment_id=compartment_id)
                embedding = bot.embedding(text_input, embedding_model)
            
            st.success(f"✅ Generated {len(embedding)}-dimensional embedding")
            
            # Display embedding information
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Dimensions", len(embedding))
                st.metric("Magnitude", f"{sum(x**2 for x in embedding) ** 0.5:.6f}")
            
            with col2:
                st.write("**First 10 values:**")
                st.json(embedding[:10])
                
                st.write("**Last 10 values:**")
                st.json(embedding[-10:])
            
            # Download option
            import json
            embedding_data = {
                "text": text_input,
                "model": embedding_model,
                "embedding": embedding,
                "metadata": {
                    "dimensions": len(embedding),
                    "magnitude": sum(x**2 for x in embedding) ** 0.5
                }
            }
            
            st.download_button(
                "📥 Download Embedding",
                data=json.dumps(embedding_data, indent=2),
                file_name=f"embedding_{int(time.time())}.json",
                mime="application/json"
            )
            
        except Exception as e:
            st.error(f"❌ Failed to generate embedding: {str(e)}")


def config_page():
    """Render configuration page."""
    st.title("⚙️ Configuration")
    st.markdown("*OCI GenAI setup and status*")
    
    # OCI Configuration Status
    st.subheader("📋 OCI Configuration Status")
    
    # Check OCI config file
    config_file = os.path.expanduser("~/.oci/config")
    if os.path.exists(config_file):
        st.success("✅ OCI config file found at ~/.oci/config")
    else:
        st.error("❌ OCI config file not found at ~/.oci/config")
        st.info("Please create an OCI config file with your credentials")
    
    # Check compartment ID
    compartment_id = os.getenv("OCI_COMPARTMENT_ID")
    if compartment_id:
        st.success(f"✅ OCI_COMPARTMENT_ID environment variable set")
        st.code(f"OCI_COMPARTMENT_ID={compartment_id}")
    else:
        st.warning("⚠️ OCI_COMPARTMENT_ID environment variable not set")
    
    # Try to load OCI config
    try:
        import oci
        config = oci.config.from_file()
        
        st.subheader("🔧 OCI Config Details")
        
        config_display = {}
        for key in ["user", "tenancy", "region", "fingerprint"]:
            value = config.get(key, "Not set")
            if key in ["user", "tenancy"] and value != "Not set":
                # Truncate long OCIDs for display
                value = value[:20] + "..." if len(value) > 20 else value
            config_display[key] = value
        
        st.json(config_display)
        
        # Key file check
        key_file = config.get("key_file")
        if key_file and os.path.exists(os.path.expanduser(key_file)):
            st.success(f"✅ Private key file found: {key_file}")
        else:
            st.error(f"❌ Private key file not found: {key_file}")
            
    except Exception as e:
        st.error(f"❌ Error loading OCI config: {str(e)}")
    
    # Setup instructions
    st.subheader("📚 Setup Instructions")
    
    with st.expander("How to set up OCI GenAI"):
        st.markdown("""
        ### 1. Create OCI Config File
        
        Create a file at `~/.oci/config` with your OCI credentials:
        
        ```ini
        [DEFAULT]
        user=ocid1.user.oc1..aaaaaaaa...
        fingerprint=12:34:56:78:90:ab:cd:ef...
        tenancy=ocid1.tenancy.oc1..aaaaaaaa...
        region=us-ashburn-1
        key_file=~/.oci/oci_api_key.pem
        ```
        
        ### 2. Set Environment Variable
        
        Set your compartment ID:
        
        ```bash
        export OCI_COMPARTMENT_ID=ocid1.compartment.oc1..aaaaaaaa...
        ```
        
        ### 3. Verify Access
        
        Ensure you have access to OCI GenAI service in your region.
        """)
    
    # Available models
    st.subheader("🤖 Available Models")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Chat Models:**")
        for model in AVAILABLE_CHAT_MODELS:
            st.write(f"• {model}")
    
    with col2:
        st.write("**Embedding Models:**")
        for model in AVAILABLE_EMBEDDING_MODELS:
            st.write(f"• {model}")


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="OCI GenAI Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Page navigation
    page = st.sidebar.radio(
        "Navigation",
        ["💬 Chat", "🔢 Embeddings", "⚙️ Configuration"],
        index=0
    )
    
    # Render sidebar configuration for chat page
    if page == "💬 Chat":
        sidebar_config()
    
    # Render selected page
    if page == "💬 Chat":
        main_chat_interface()
    elif page == "🔢 Embeddings":
        embedding_page()
    elif page == "⚙️ Configuration":
        config_page()


if __name__ == "__main__":
    main()