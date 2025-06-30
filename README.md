# OCI GenAI Chatbot

A sample chatbot application demonstrating **Oracle Cloud Infrastructure (OCI) GenAI** integration with **LiteLLM**. This project showcases how to use OCI's powerful generative AI models through LiteLLM's unified interface.

## ✨ Features

- **💬 Interactive Chat Interface**: Both CLI and web-based (Streamlit) interfaces
- **🚀 Real-time Streaming**: Stream responses in real-time for faster perceived response time
- **🔍 Text Embeddings**: Generate embeddings using OCI GenAI embedding models
- **🎯 Multiple Models**: Support for various OCI GenAI models (Cohere, Llama, etc.)
- **⚙️ Configurable Parameters**: Adjust temperature, max tokens, streaming, and system prompts
- **📝 Conversation History**: Maintains context across chat sessions
- **🎨 Rich UI**: Beautiful CLI with Rich library and modern Streamlit web interface
- **🔄 Async Support**: Full async/await support for high-performance applications

## 🏗️ Architecture

This application uses a **forked version of LiteLLM** that includes native OCI GenAI support:

- **LiteLLM Fork**: [https://github.com/djvolz/litellm](https://github.com/djvolz/litellm)
- **OCI Provider**: Native `oci_genai` provider integrated into LiteLLM
- **Authentication**: Uses standard OCI configuration (`~/.oci/config`)

## 📋 Prerequisites

1. **OCI Account**: Access to Oracle Cloud Infrastructure
2. **OCI GenAI Service**: Access to OCI Generative AI service in your region
3. **OCI Configuration**: Properly configured OCI credentials
4. **Python**: Python 3.8 or higher

## 🚀 Installation

### Option 1: Using uv (Recommended)

```bash
# Clone this repository
git clone <repository-url>
cd oci-genai-chatbot

# Install with uv
uv sync
```

### Option 2: Using pip

```bash
# Clone and install
git clone <repository-url>
cd oci-genai-chatbot
pip install -e .
```

## ⚙️ Configuration

### 1. OCI Configuration File

Create `~/.oci/config` with your OCI credentials:

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaa...
fingerprint=12:34:56:78:90:ab:cd:ef...
tenancy=ocid1.tenancy.oc1..aaaaaaaa...
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

### 2. Environment Variables

Set your compartment ID:

```bash
export OCI_COMPARTMENT_ID=ocid1.compartment.oc1..aaaaaaaa...
```

### 3. Verify Setup

Check your configuration:

```bash
chatbot-cli config
```

## 🖥️ Usage

### CLI Interface

Start an interactive chat session:

```bash
# Basic chat
chatbot-cli chat

# With custom model and parameters
chatbot-cli chat --model cohere.command-r-plus --temperature 0.8 --max-tokens 1000

# With system prompt and streaming enabled
chatbot-cli chat --system-prompt "You are a helpful coding assistant" --stream

# Disable streaming for traditional response style
chatbot-cli chat --no-stream
```

Generate embeddings:

```bash
# Generate embedding for text
chatbot-cli embed "Hello, world!"

# With custom embedding model
chatbot-cli embed "Hello, world!" --model cohere.embed-english-light-v3.0
```

List available models:

```bash
chatbot-cli models
```

### Streamlit Web Interface

Launch the web application:

```bash
# Using uv (recommended)
uv run streamlit run src/oci_genai_chatbot/streamlit_app.py

# Or using pip/python directly
streamlit run src/oci_genai_chatbot/streamlit_app.py
```

Then open your browser to `http://localhost:8502` (or the port shown in the terminal)

The web interface provides:

- **💬 Chat Tab**: Interactive chatbot with conversation history and real-time streaming
- **🔍 Embeddings Tab**: Generate and download text embeddings
- **⚙️ Configuration Tab**: View OCI setup status and instructions

## 🤖 Available Models

### Chat Models

- `cohere.command-r-plus` - Advanced command model with enhanced reasoning
- `cohere.command-r` - Balanced command model for general use
- `meta.llama-3.1-405b-instruct` - Large-scale Meta Llama model
- `meta.llama-3.1-70b-instruct` - Mid-scale Meta Llama model

### Embedding Models

- `cohere.embed-multilingual-v3.0` - Multilingual embedding model (1024 dimensions)
- `cohere.embed-english-light-v3.0` - Lightweight English embedding model (384 dimensions)

## 📚 API Usage

### Python API

```python
from oci_genai_chatbot import OCIGenAIChatBot

# Initialize chatbot
bot = OCIGenAIChatBot(
    model="cohere.command-r-plus",
    temperature=0.7,
    max_tokens=500,
    compartment_id="ocid1.compartment.oc1..aaaaaaaa..."
)

# Basic chat
response = bot.chat("Hello! How are you today?")
print(response)

# Streaming chat
for chunk in bot.chat_stream("Tell me a story"):
    print(chunk, end="", flush=True)

# Chat with system prompt
response = bot.chat(
    "Explain quantum computing", 
    system_prompt="You are a physics professor"
)

# Async chat
import asyncio
async def async_chat():
    response = await bot.achat("Hello async world!")
    print(response)
    
    # Async streaming
    async for chunk in await bot.achat_stream("Tell me about AI"):
        print(chunk, end="", flush=True)

asyncio.run(async_chat())

# Generate embeddings
embedding = bot.embedding("Text to embed")
print(f"Embedding dimensions: {len(embedding)}")
```

### Direct LiteLLM Usage

```python
import litellm

# Chat completion
response = litellm.completion(
    model="oci_genai/cohere.command-r-plus",
    messages=[{"role": "user", "content": "Hello!"}],
    compartment_id="ocid1.compartment.oc1..aaaaaaaa...",
    temperature=0.7,
    max_tokens=500
)

# Streaming chat completion
stream = litellm.completion(
    model="oci_genai/cohere.command-r-plus",
    messages=[{"role": "user", "content": "Tell me a story"}],
    compartment_id="ocid1.compartment.oc1..aaaaaaaa...",
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

# Async streaming
async def async_stream():
    stream = await litellm.acompletion(
        model="oci_genai/cohere.command-r-plus",
        messages=[{"role": "user", "content": "Hello async!"}],
        compartment_id="ocid1.compartment.oc1..aaaaaaaa...",
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")

# Embeddings
embedding_response = litellm.embedding(
    model="oci_genai/cohere.embed-multilingual-v3.0",
    input="Text to embed",
    compartment_id="ocid1.compartment.oc1..aaaaaaaa..."
)
```

## 🌟 Features Showcase

### CLI Features

- **Rich Terminal UI**: Beautiful formatted output with colors and panels
- **Real-time streaming**: Watch responses appear character by character
- **Interactive Chat**: Live conversation with real-time streaming or traditional responses
- **History Management**: View and reset conversation history
- **Connection Testing**: Verify OCI GenAI connectivity
- **Model Information**: Browse available models and their capabilities
- **Flexible Modes**: Choose between streaming and non-streaming responses

### Streamlit Features

- **Multi-page Interface**: Separate pages for chat, embeddings, and configuration
- **Real-time Streaming**: Interactive chat with live message streaming
- **Streaming Toggle**: Easy switching between streaming and traditional responses
- **Configuration Management**: Live settings adjustment including streaming preferences
- **Embedding Visualization**: Display embedding vectors and metadata
- **Download Options**: Export embeddings as JSON files

### Advanced Options

- **System Prompts**: Set context and personality for the AI
- **Temperature Control**: Adjust response creativity vs. consistency
- **Token Limits**: Control response length
- **Model Switching**: Easy switching between different OCI GenAI models

## 🔧 OCI GenAI Integration Details

This application demonstrates the **native OCI GenAI integration** added to LiteLLM, featuring:

- **Unified API**: Use OCI GenAI models with the same interface as OpenAI, Anthropic, etc.
- **Authentication**: Seamless OCI config-based authentication
- **Error Handling**: Comprehensive error handling with OCI-specific messages
- **Model Management**: Automatic model discovery and configuration
- **Regional Support**: Multi-region OCI GenAI support

### Supported OCI Features

- **💬 Text Generation**: Chat completion with various models
- **🔍 Embeddings**: Text embedding generation
- **📡 Real-time Streaming**: Live response streaming with chunked delivery
- **🔄 Async Operations**: Full async/await support for high-performance applications
- **🔧 Function Calling**: Tool use capabilities (model-dependent)
- **📋 System Messages**: System prompt support
- **🌡️ Temperature Control**: Response randomness adjustment
- **📏 Token Limits**: Output length control
- **⚡ Performance**: Optimized streaming for faster perceived response times

## 🛠️ Troubleshooting

### Common Issues

1. **OCI Config Not Found**
   ```
   Error: OCI configuration error
   ```
   - Ensure `~/.oci/config` exists with valid credentials
   - Check file permissions (`chmod 600 ~/.oci/config`)

2. **Compartment ID Missing**
   ```
   Error: compartment_id is required
   ```
   - Set `OCI_COMPARTMENT_ID` environment variable
   - Or pass `compartment_id` parameter to the client

3. **Import Error**
   ```
   Error: OCI GenAI support not found in LiteLLM
   ```
   - Ensure you're using the forked version: `pip install git+https://github.com/djvolz/litellm.git`

4. **Permission Denied**
   ```
   Error: User does not have permission to access GenAI
   ```
   - Verify OCI GenAI service access in your tenancy
   - Check IAM policies for GenAI service permissions

### Getting Help

- Check configuration: `chatbot-cli config`
- Test connection: Use the "Test Connection" button in Streamlit
- Verify models: `chatbot-cli models`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🙏 Acknowledgments

- **LiteLLM**: Original unified LLM interface
- **Oracle Cloud Infrastructure**: GenAI service and platform
- **Streamlit**: Beautiful web interface framework
- **Rich**: Enhanced CLI experience