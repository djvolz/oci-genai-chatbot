"""
Command-line interface for OCI GenAI Chatbot.
"""

import click
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.markdown import Markdown

from .litellm_client import OCIGenAIChatBot, AVAILABLE_CHAT_MODELS, AVAILABLE_EMBEDDING_MODELS

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """OCI GenAI Chatbot - Powered by LiteLLM"""
    pass


@main.command()
@click.option("--model", "-m", default="cohere.command-r-plus", 
              help="OCI GenAI model to use", 
              type=click.Choice(AVAILABLE_CHAT_MODELS))
@click.option("--temperature", "-t", default=0.7, type=float,
              help="Response temperature (0.0-1.0)")
@click.option("--max-tokens", default=500, type=int,
              help="Maximum tokens to generate")
@click.option("--system-prompt", "-s", 
              help="System prompt to set context")
@click.option("--compartment-id", "-c",
              help="OCI compartment ID (defaults to OCI_COMPARTMENT_ID env var)")
def chat(model, temperature, max_tokens, system_prompt, compartment_id):
    """Start an interactive chat session with OCI GenAI."""
    
    console.print(Panel.fit(
        "[bold blue]OCI GenAI Chatbot[/bold blue]\n"
        f"Model: {model}\n"
        f"Temperature: {temperature}\n"
        f"Max Tokens: {max_tokens}",
        title="🤖 Chatbot Configuration"
    ))
    
    try:
        # Initialize chatbot
        bot = OCIGenAIChatBot(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            compartment_id=compartment_id
        )
        
        console.print("[green]✓[/green] Successfully connected to OCI GenAI")
        
        if system_prompt:
            console.print(f"[yellow]System:[/yellow] {system_prompt}")
        
        console.print("\n[dim]Type 'quit', 'exit', or 'bye' to end the conversation[/dim]")
        console.print("[dim]Type 'reset' to clear conversation history[/dim]")
        console.print("[dim]Type 'history' to view conversation history[/dim]\n")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("[bold green]You[/bold green]")
                
                if user_input.lower() in ["quit", "exit", "bye"]:
                    console.print("\n[yellow]Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == "reset":
                    bot.reset_conversation()
                    console.print("[yellow]Conversation history cleared.[/yellow]\n")
                    continue
                
                if user_input.lower() == "history":
                    _show_history(bot)
                    continue
                
                if not user_input.strip():
                    continue
                
                # Get bot response
                with console.status("[bold blue]Thinking...", spinner="dots"):
                    response = bot.chat(user_input, system_prompt if system_prompt else None)
                
                # Display response
                console.print(f"[bold blue]Bot:[/bold blue] {response}\n")
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Goodbye! 👋[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}\n")
                
    except Exception as e:
        console.print(f"[red]Failed to initialize chatbot:[/red] {e}")
        console.print("\n[yellow]Please check your OCI configuration:[/yellow]")
        console.print("1. Ensure ~/.oci/config exists with valid credentials")
        console.print("2. Set OCI_COMPARTMENT_ID environment variable")
        console.print("3. Verify OCI GenAI service access in your region")


def _show_history(bot: OCIGenAIChatBot):
    """Display conversation history."""
    history = bot.get_conversation_history()
    
    if not history:
        console.print("[yellow]No conversation history yet.[/yellow]\n")
        return
    
    console.print("\n[bold]Conversation History:[/bold]")
    
    for i, msg in enumerate(history):
        role = "You" if msg["role"] == "user" else "Bot"
        color = "green" if msg["role"] == "user" else "blue"
        console.print(f"[bold {color}]{role}:[/bold {color}] {msg['content']}")
    
    console.print()


@main.command()
@click.argument("text")
@click.option("--model", "-m", default="cohere.embed-multilingual-v3.0",
              help="OCI GenAI embedding model to use",
              type=click.Choice(AVAILABLE_EMBEDDING_MODELS))
@click.option("--compartment-id", "-c",
              help="OCI compartment ID (defaults to OCI_COMPARTMENT_ID env var)")
def embed(text, model, compartment_id):
    """Generate embeddings for text using OCI GenAI."""
    
    console.print(Panel.fit(
        f"[bold blue]Text Embedding[/bold blue]\n"
        f"Model: {model}\n"
        f"Text: {text[:100]}{'...' if len(text) > 100 else ''}",
        title="🔢 Embedding Configuration"
    ))
    
    try:
        # Initialize chatbot (for embedding functionality)
        bot = OCIGenAIChatBot(compartment_id=compartment_id)
        
        with console.status("[bold blue]Generating embedding...", spinner="dots"):
            embedding = bot.embedding(text, model)
        
        console.print(f"[green]✓[/green] Generated {len(embedding)}-dimensional embedding")
        
        # Show first and last few values
        console.print("\n[bold]Embedding Vector (preview):[/bold]")
        console.print(f"First 5 values: {embedding[:5]}")
        console.print(f"Last 5 values: {embedding[-5:]}")
        
        # Calculate magnitude
        magnitude = sum(x**2 for x in embedding) ** 0.5
        console.print(f"Magnitude: {magnitude:.6f}")
        
    except Exception as e:
        console.print(f"[red]Failed to generate embedding:[/red] {e}")


@main.command()
def models():
    """List available OCI GenAI models."""
    
    # Chat models table
    chat_table = Table(title="💬 Available Chat Models")
    chat_table.add_column("Model", style="cyan")
    chat_table.add_column("Description", style="white")
    
    model_descriptions = {
        "cohere.command-r-plus": "Advanced command model with enhanced reasoning",
        "cohere.command-r": "Balanced command model for general use",
        "meta.llama-3.1-405b-instruct": "Large-scale Meta Llama model",
        "meta.llama-3.1-70b-instruct": "Mid-scale Meta Llama model",
    }
    
    for model in AVAILABLE_CHAT_MODELS:
        chat_table.add_row(model, model_descriptions.get(model, "Chat completion model"))
    
    console.print(chat_table)
    
    # Embedding models table
    embed_table = Table(title="🔢 Available Embedding Models")
    embed_table.add_column("Model", style="cyan")
    embed_table.add_column("Description", style="white")
    embed_table.add_column("Dimensions", style="yellow")
    
    embedding_info = {
        "cohere.embed-multilingual-v3.0": ("Multilingual embedding model", "1024"),
        "cohere.embed-english-light-v3.0": ("Lightweight English embedding model", "384"),
    }
    
    for model in AVAILABLE_EMBEDDING_MODELS:
        desc, dims = embedding_info.get(model, ("Embedding model", "Unknown"))
        embed_table.add_row(model, desc, dims)
    
    console.print(embed_table)


@main.command()
def config():
    """Show OCI configuration status."""
    
    console.print(Panel.fit("[bold blue]OCI Configuration Status[/bold blue]", title="⚙️ Configuration"))
    
    # Check OCI config file
    config_file = os.path.expanduser("~/.oci/config")
    if os.path.exists(config_file):
        console.print("[green]✓[/green] OCI config file found at ~/.oci/config")
    else:
        console.print("[red]✗[/red] OCI config file not found at ~/.oci/config")
    
    # Check compartment ID
    compartment_id = os.getenv("OCI_COMPARTMENT_ID")
    if compartment_id:
        console.print(f"[green]✓[/green] OCI_COMPARTMENT_ID: {compartment_id}")
    else:
        console.print("[red]✗[/red] OCI_COMPARTMENT_ID environment variable not set")
    
    # Try to load OCI config
    try:
        import oci
        config = oci.config.from_file()
        
        console.print("\n[bold]OCI Config Details:[/bold]")
        for key in ["user", "tenancy", "region"]:
            value = config.get(key, "Not set")
            if key == "user" and value != "Not set":
                # Truncate user OCID for display
                value = value[:20] + "..." if len(value) > 20 else value
            console.print(f"  {key}: {value}")
            
    except Exception as e:
        console.print(f"[red]Error loading OCI config:[/red] {e}")


if __name__ == "__main__":
    main()