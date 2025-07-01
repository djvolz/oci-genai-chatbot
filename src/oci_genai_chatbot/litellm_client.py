"""
LiteLLM client wrapper for OCI GenAI integration.
"""

import os
import sys
from typing import List, Dict, Any, Optional, Iterator, Union, AsyncIterator

# Import LiteLLM with OCI GenAI support
# This uses the forked version from https://github.com/djvolz/litellm
try:
    import litellm
    
    # Try to verify OCI GenAI support is available, but don't exit if not found
    # This allows the module to be imported for testing purposes
    OCI_GENAI_AVAILABLE = False
    try:
        from litellm.types.utils import LlmProviders
        if hasattr(LlmProviders, 'OCI_GENAI'):
            OCI_GENAI_AVAILABLE = True
    except (ImportError, AttributeError):
        # OCI GenAI support not available, but continue loading the module
        pass
        
except ImportError as e:
    print(f"Error importing litellm: {e}")
    print("\nTo install LiteLLM with OCI GenAI support:")
    print("1. pip install git+https://github.com/djvolz/litellm.git")
    print("2. OR clone the repository and install locally:")
    print("   git clone https://github.com/djvolz/litellm.git")
    print("   cd litellm && pip install -e .")
    # Don't exit here - allow the module to be imported
    litellm = None
    OCI_GENAI_AVAILABLE = False


class OCIGenAIChatBot:
    """
    A simple chatbot client using LiteLLM with OCI GenAI.
    """
    
    def __init__(
        self, 
        model: str = "cohere.command-r-plus",
        temperature: float = 0.7,
        max_tokens: int = 500,
        compartment_id: Optional[str] = None
    ):
        """
        Initialize the OCI GenAI chatbot.
        
        Args:
            model: OCI GenAI model name (without oci_genai/ prefix)
            temperature: Response randomness (0.0-1.0)
            max_tokens: Maximum tokens to generate
            compartment_id: OCI compartment ID (defaults to env var OCI_COMPARTMENT_ID)
        """
        self.model = f"oci_genai/{model}"
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.compartment_id = compartment_id or os.getenv("OCI_COMPARTMENT_ID")
        self.conversation_history: List[Dict[str, str]] = []
        
        # Validate OCI setup
        self._validate_oci_setup()
    
    def _validate_oci_setup(self) -> None:
        """Validate that OCI configuration is available."""
        # Check if LiteLLM is available
        if litellm is None:
            raise ValueError("LiteLLM is not available. Please install it with: pip install git+https://github.com/djvolz/litellm.git")
        
        # Check if OCI GenAI support is available (optional - show warning if not)
        if not OCI_GENAI_AVAILABLE:
            print("Warning: OCI GenAI support not detected in LiteLLM. Make sure you're using the forked version.")
            
        try:
            import oci
            config = oci.config.from_file()
            required_keys = ["user", "tenancy", "fingerprint", "key_file", "region"]
            missing_keys = [key for key in required_keys if not config.get(key)]
            
            if missing_keys:
                raise ValueError(f"Missing OCI config keys: {missing_keys}")
                
            if not self.compartment_id:
                raise ValueError("compartment_id is required. Set OCI_COMPARTMENT_ID environment variable or pass it to constructor")
                
        except Exception as e:
            raise ValueError(f"OCI configuration error: {e}")
    
    def chat(self, message: str, system_prompt: Optional[str] = None, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Send a message to the chatbot and get a response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt to set context
            stream: Whether to stream the response (default: False)
            
        Returns:
            Bot response (string if stream=False, Iterator[str] if stream=True)
        """
        # Build messages list
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        try:
            # Make LiteLLM call to OCI GenAI
            response = litellm.completion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                compartment_id=self.compartment_id,
                stream=stream,
            )
            
            if stream:
                # Return streaming generator
                return self._process_streaming_response(response, message)
            else:
                # Extract response content
                bot_response = response.choices[0].message.content
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history reasonable length (last 10 exchanges)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return bot_response
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            if stream:
                # Return error as a single chunk for streaming
                def error_generator():
                    yield error_message
                return error_generator()
            else:
                return error_message
    
    def _process_streaming_response(self, response_stream, user_message: str) -> Iterator[str]:
        """
        Process streaming response from LiteLLM.
        
        Args:
            response_stream: Streaming response from LiteLLM
            user_message: Original user message for history tracking
            
        Yields:
            Response chunks as they arrive
        """
        collected_response = ""
        
        try:
            for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        collected_response += content
                        yield content
                    
                    # Check if streaming is finished
                    if chunk.choices[0].finish_reason:
                        break
            
            # Update conversation history after streaming is complete
            if collected_response:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": collected_response})
                
                # Keep conversation history reasonable length (last 10 exchanges)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                    
        except Exception as e:
            yield f"\n\nError during streaming: {str(e)}"
    
    def chat_stream(self, message: str, system_prompt: Optional[str] = None) -> Iterator[str]:
        """
        Send a message to the chatbot and get a streaming response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt to set context
            
        Yields:
            Response chunks as they arrive
        """
        return self.chat(message, system_prompt, stream=True)
    
    async def achat(self, message: str, system_prompt: Optional[str] = None, stream: bool = False) -> Union[str, AsyncIterator[str]]:
        """
        Send a message to the chatbot and get an async response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt to set context
            stream: Whether to stream the response (default: False)
            
        Returns:
            Bot response (string if stream=False, AsyncIterator[str] if stream=True)
        """
        # Build messages list
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        try:
            # Make async LiteLLM call to OCI GenAI
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                compartment_id=self.compartment_id,
                stream=stream,
            )
            
            if stream:
                # Return async streaming generator
                return self._process_async_streaming_response(response, message)
            else:
                # Extract response content
                bot_response = response.choices[0].message.content
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history reasonable length (last 10 exchanges)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return bot_response
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            if stream:
                # Return error as a single chunk for async streaming
                async def async_error_generator():
                    yield error_message
                return async_error_generator()
            else:
                return error_message
    
    async def _process_async_streaming_response(self, response_stream, user_message: str) -> AsyncIterator[str]:
        """
        Process async streaming response from LiteLLM.
        
        Args:
            response_stream: Async streaming response from LiteLLM
            user_message: Original user message for history tracking
            
        Yields:
            Response chunks as they arrive
        """
        collected_response = ""
        
        try:
            async for chunk in response_stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        collected_response += content
                        yield content
                    
                    # Check if streaming is finished
                    if chunk.choices[0].finish_reason:
                        break
            
            # Update conversation history after streaming is complete
            if collected_response:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": collected_response})
                
                # Keep conversation history reasonable length (last 10 exchanges)
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                    
        except Exception as e:
            yield f"\n\nError during async streaming: {str(e)}"
    
    async def achat_stream(self, message: str, system_prompt: Optional[str] = None) -> AsyncIterator[str]:
        """
        Send a message to the chatbot and get an async streaming response.
        
        Args:
            message: User message
            system_prompt: Optional system prompt to set context
            
        Yields:
            Response chunks as they arrive
        """
        return await self.achat(message, system_prompt, stream=True)
    
    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def embedding(self, text: str, model: str = "cohere.embed-multilingual-v3.0") -> List[float]:
        """
        Generate embeddings for text using OCI GenAI.
        
        Args:
            text: Text to embed
            model: Embedding model name (without oci_genai/ prefix)
            
        Returns:
            Embedding vector
        """
        try:
            response = litellm.embedding(
                model=f"oci_genai/{model}",
                input=text,
                compartment_id=self.compartment_id,
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            raise Exception(f"Embedding error: {str(e)}")


# Available OCI GenAI models
AVAILABLE_CHAT_MODELS = [
    "cohere.command-r-plus",
    "cohere.command-r", 
    "meta.llama-3.1-405b-instruct",
    "meta.llama-3.1-70b-instruct",
]

AVAILABLE_EMBEDDING_MODELS = [
    "cohere.embed-multilingual-v3.0",
    "cohere.embed-english-light-v3.0",
]