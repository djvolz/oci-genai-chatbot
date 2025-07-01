"""
Codex-inspired CLI interface for OCI GenAI Chatbot.
A clean, developer-focused interface similar to OpenAI Codex.
"""

import os
import sys
import click
import readline
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
import time

from oci_genai_chatbot.litellm_client import OCIGenAIChatBot, AVAILABLE_CHAT_MODELS

console = Console()

class CodexInterface:
    """Codex-inspired interface for OCI GenAI."""
    
    def __init__(self, model: str = "cohere.command-r-plus", 
                 temperature: float = 0.7, max_tokens: int = 1000,
                 compartment_id: Optional[str] = None,
                 mode: str = "suggest", demo: bool = False):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.compartment_id = compartment_id
        self.mode = mode
        self.demo = demo
        self.bot: Optional[OCIGenAIChatBot] = None
        self.session_history: List[Dict[str, Any]] = []
        
        # Codex-style system prompts
        self.system_prompts = {
            "suggest": "You are an AI coding assistant. Provide helpful suggestions and explanations for code. Always ask for confirmation before making changes.",
            "code": "You are an expert programmer. Write clean, efficient code with clear explanations. Format code properly with syntax highlighting.",
            "explain": "You are a technical documentation expert. Explain code, algorithms, and concepts clearly and concisely.",
            "debug": "You are a debugging expert. Help identify and fix issues in code. Provide step-by-step debugging guidance.",
            "review": "You are a code reviewer. Analyze code for best practices, potential issues, and improvement suggestions."
        }
    
    def initialize(self) -> bool:
        """Initialize the OCI GenAI connection."""
        if self.demo:
            console.print("[yellow]Running in demo mode - no actual AI responses[/yellow]")
            return True
            
        try:
            self.bot = OCIGenAIChatBot(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                compartment_id=self.compartment_id
            )
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to connect: {str(e)}")
            console.print(f"[dim]Use --demo flag to try the interface without OCI setup[/dim]")
            return False
    
    def show_startup_banner(self):
        """Display startup banner in Codex style."""
        console.print()
        console.print("[bold cyan]oci-genai[/bold cyan] [dim]v0.1.0[/dim]")
        console.print(f"[dim]Model: {self.model}[/dim]")
        console.print(f"[dim]Mode: {self.mode}[/dim]")
        console.print()
        console.print("[dim]Type your request in natural language.[/dim]")
        console.print("[dim]Commands: /help, /mode, /reset, /exit[/dim]")
        console.print()
    
    def get_system_prompt(self) -> str:
        """Get system prompt based on current mode."""
        return self.system_prompts.get(self.mode, self.system_prompts["suggest"])
    
    def process_command(self, input_text: str) -> bool:
        """Process special commands. Returns True if command was handled."""
        if not input_text.startswith('/'):
            return False
        
        command = input_text[1:].strip().lower()
        
        if command == "help":
            self.show_help()
            return True
        elif command == "exit" or command == "quit":
            console.print("[dim]Goodbye![/dim]")
            return "exit"
        elif command == "reset":
            self.bot.reset_conversation()
            self.session_history.clear()
            console.print("[dim]Session reset.[/dim]")
            return True
        elif command.startswith("mode"):
            parts = command.split()
            if len(parts) > 1:
                new_mode = parts[1]
                if new_mode in self.system_prompts:
                    self.mode = new_mode
                    console.print(f"[dim]Mode changed to: {new_mode}[/dim]")
                else:
                    console.print(f"[red]Unknown mode: {new_mode}[/red]")
                    console.print(f"[dim]Available modes: {', '.join(self.system_prompts.keys())}[/dim]")
            else:
                console.print(f"[dim]Current mode: {self.mode}[/dim]")
                console.print(f"[dim]Available modes: {', '.join(self.system_prompts.keys())}[/dim]")
            return True
        elif command == "history":
            self.show_history()
            return True
        else:
            console.print(f"[red]Unknown command: /{command}[/red]")
            console.print("[dim]Type /help for available commands[/dim]")
            return True
    
    def show_help(self):
        """Show help information."""
        help_text = """[bold]Commands:[/bold]
  /help     Show this help
  /mode     Change interaction mode (suggest, code, explain, debug, review)
  /reset    Clear conversation history  
  /history  Show conversation history
  /exit     Exit the session

[bold]Modes:[/bold]
  suggest   AI provides suggestions (default)
  code      Focus on code generation
  explain   Explain code and concepts
  debug     Debug and troubleshoot issues
  review    Code review and best practices

[bold]Examples:[/bold]
  Write a Python function to sort a list
  Explain this regex pattern: ^[a-zA-Z0-9]+$
  Debug why my loop isn't working
  Review this code for performance issues
"""
        console.print(Panel(help_text, title="[bold cyan]oci-genai help[/bold cyan]", border_style="dim"))
    
    def show_history(self):
        """Show conversation history."""
        if not self.session_history:
            console.print("[dim]No conversation history.[/dim]")
            return
        
        console.print("\n[bold]Session History:[/bold]")
        for i, entry in enumerate(self.session_history[-5:], 1):  # Show last 5
            prompt_preview = entry['prompt'][:60] + "..." if len(entry['prompt']) > 60 else entry['prompt']
            response_preview = entry['response'][:60] + "..." if len(entry['response']) > 60 else entry['response']
            console.print(f"[dim]{i}.[/dim] [cyan]>[/cyan] {prompt_preview}")
            console.print(f"   [green]<[/green] {response_preview}")
        console.print()
    
    def format_response(self, response: str) -> None:
        """Format and display response with syntax highlighting."""
        # Check if response contains code blocks
        if "```" in response:
            # Split by code blocks and render appropriately
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    if part.strip():
                        console.print(Markdown(part))
                else:
                    # Code block
                    lines = part.strip().split('\n')
                    if lines:
                        # Try to detect language from first line
                        first_line = lines[0]
                        language = "text"
                        code_content = part
                        
                        # Common language indicators
                        if first_line in ["python", "py", "javascript", "js", "bash", "shell", "sql", "json", "yaml", "dockerfile"]:
                            language = first_line
                            code_content = '\n'.join(lines[1:])
                        elif "def " in code_content or "import " in code_content:
                            language = "python"
                        elif "function " in code_content or "const " in code_content:
                            language = "javascript"
                        elif "SELECT " in code_content.upper() or "FROM " in code_content.upper():
                            language = "sql"
                        
                        try:
                            syntax = Syntax(code_content, language, theme="monokai", line_numbers=True)
                            console.print(syntax)
                        except:
                            console.print(f"[dim]```{language}[/dim]")
                            console.print(code_content)
                            console.print("[dim]```[/dim]")
        else:
            # Regular markdown rendering
            console.print(Markdown(response))
    
    def stream_response(self, prompt: str) -> str:
        """Stream response with Codex-style formatting."""
        console.print("[green]<[/green] ", end="")
        
        if self.demo:
            # Demo mode - provide sample responses
            demo_responses = {
                "code": """```python
def hello_world():
    \"\"\"A simple hello world function.\"\"\"
    print("Hello, World!")
    return "Hello, World!"

# Usage
if __name__ == "__main__":
    greeting = hello_world()
```

This function prints and returns a greeting message. It's a classic example for demonstrating basic Python syntax.""",
                
                "explain": """This appears to be a request for code explanation. In demo mode, I would analyze your code and provide:

• **Purpose**: What the code does
• **Structure**: How it's organized  
• **Key concepts**: Important programming principles
• **Best practices**: Recommendations for improvement

For a real analysis, please run without the --demo flag with proper OCI configuration.""",
                
                "debug": """**Debugging Approach:**

1. **Identify the issue**: Reproduce the problem consistently
2. **Check inputs**: Verify data types and values
3. **Add logging**: Use print statements or debugger
4. **Test incrementally**: Test small parts in isolation
5. **Review logic**: Check conditional statements and loops

In demo mode, I can't analyze your specific code, but this is the general debugging methodology I would apply.""",
                
                "review": """**Code Review Checklist:**

✅ **Readability**: Clear variable names and comments
✅ **Performance**: Efficient algorithms and data structures  
✅ **Security**: Input validation and error handling
✅ **Maintainability**: Modular design and documentation
✅ **Standards**: Following language conventions

For a detailed review of your specific code, please run without --demo flag.""",
                
                "suggest": """I'd be happy to help with that! In demo mode, I can show you the interface but can't provide actual AI responses.

Some things I can help with when properly connected:
• Code generation and optimization
• Debugging and troubleshooting
• Architecture and design patterns
• Documentation and explanations
• Code reviews and best practices

Run without --demo to get real AI assistance!"""
            }
            
            response = demo_responses.get(self.mode, demo_responses["suggest"])
            
            # Simulate streaming by printing character by character
            for char in response:
                console.print(char, end="")
                time.sleep(0.01)  # Small delay to simulate streaming
            
            console.print("\n")
            return response
        
        system_prompt = self.get_system_prompt()
        
        try:
            full_response = ""
            response_generator = self.bot.chat(prompt, system_prompt, stream=True)
            
            for chunk in response_generator:
                if chunk.startswith("Error:"):
                    console.print(f"[red]{chunk}[/red]")
                    return chunk
                else:
                    full_response += chunk
                    console.print(chunk, end="")
            
            console.print("\n")
            return full_response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    def run_repl(self):
        """Run the main REPL loop."""
        if not self.initialize():
            return
        
        self.show_startup_banner()
        
        while True:
            try:
                # Codex-style prompt
                console.print("[cyan]>[/cyan] ", end="")
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                result = self.process_command(user_input)
                if result == "exit":
                    break
                elif result:
                    continue
                
                # Process regular input
                response = self.stream_response(user_input)
                
                # Store in history
                self.session_history.append({
                    "prompt": user_input,
                    "response": response,
                    "mode": self.mode,
                    "timestamp": time.time()
                })
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[dim]Use /exit to quit[/dim]")
                continue
            except EOFError:
                console.print("\n[dim]Goodbye![/dim]")
                break
            except Exception as e:
                console.print(f"[red]Unexpected error: {str(e)}[/red]")
                continue


@click.command()
@click.option("--model", "-m", default="cohere.command-r-plus",
              type=click.Choice(AVAILABLE_CHAT_MODELS),
              help="OCI GenAI model to use")
@click.option("--temperature", "-t", default=0.7, type=float,
              help="Response temperature (0.0-1.0)")
@click.option("--max-tokens", default=1000, type=int,
              help="Maximum tokens to generate")
@click.option("--mode", default="suggest",
              type=click.Choice(["suggest", "code", "explain", "debug", "review"]),
              help="Interaction mode")
@click.option("--compartment-id", "-c",
              help="OCI compartment ID")
@click.option("--one-shot", "-o",
              help="Execute a single command and exit")
@click.option("--demo", is_flag=True,
              help="Run in demo mode (no OCI connection required)")
def codex(model, temperature, max_tokens, mode, compartment_id, one_shot, demo):
    """
    oci-genai - Codex-inspired AI coding assistant
    
    A clean, developer-focused interface for OCI GenAI models.
    """
    
    interface = CodexInterface(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        compartment_id=compartment_id,
        mode=mode,
        demo=demo
    )
    
    if one_shot:
        # Single command mode
        if not interface.initialize():
            sys.exit(1)
        
        response = interface.stream_response(one_shot)
        if not response.startswith("Error:"):
            interface.format_response(response)
    else:
        # Interactive REPL mode
        interface.run_repl()


if __name__ == "__main__":
    codex()