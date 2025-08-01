import click
import re
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from rich import box
from typing import Optional
from ..llm.client import LLMManager
from ..core.config import settings
from ..rag import VectorStore, CodeAnalyzer

console = Console()

def show_welcome():
    """Display welcome screen with ASCII art and info."""
    console.clear()
    
    # ASCII Art
    ascii_art = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ▄████▄   ▒█████  ▓█████▄ ▓█████ ██▓ ███▄    █   ██████    ║
    ║  ▒██▀ ▀█  ▒██▒  ██▒▒██▀ ██▌▓█   ▀▓██▒ ██ ▀█   █ ▒██    ▒    ║
    ║  ▒▓█    ▄ ▒██░  ██▒░██   █▌▒███  ▒██▒▓██  ▀█ ██▒░ ▓██▄      ║
    ║  ▒▓▓▄ ▄██▒▒██   ██░░▓█▄   ▌▒▓█  ▄░██░▓██▒  ▐▌██▒  ▒   ██▒   ║
    ║  ▒ ▓███▀ ░░ ████▓▒░░▒████▓ ░▒████░██░▒██░   ▓██░▒██████▒▒   ║
    ║  ░ ░▒ ▒  ░░ ▒░▒░▒░  ▒▒▓  ▒ ░░ ▒░ ░▓  ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░   ║
    ║    ░  ▒     ░ ▒ ▒░  ░ ▒  ▒  ░ ░  ░▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    
    console.print(Panel(
        Text(ascii_art, style="bold cyan", justify="center"),
        title="[bold yellow]Welcome to CodeInsight[/bold yellow]",
        subtitle="[dim]AI-Powered Code Analysis Assistant[/dim]",
        border_style="bright_blue",
        box=box.DOUBLE_EDGE
    ))
    
    # Display version and info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Key", style="cyan", width=20)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("[bold]Version[/bold]", "0.1.0")
    info_table.add_row("[bold]Status[/bold]", "Ready")
    info_table.add_row("[bold]Mode[/bold]", "Interactive")
    
    console.print(Panel(info_table, title="System Info", border_style="dim"))

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """CodeInsight - AI-Powered Code Analysis Assistant"""
    if ctx.invoked_subcommand is None:
        interactive_mode()

@main.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Analyze recursively')
def analyze(path: str, recursive: bool):
    """Analyze code in a file or directory."""
    console.print(f"[cyan]Analyzing {path}...[/cyan]")
    analyzer = CodeAnalyzer()
    store = VectorStore()
    
    if os.path.isdir(path):
        snippets = analyzer.analyze_directory(Path(path), recursive)
    else:
        snippets = analyzer.analyze_file(Path(path))
    
    for snippet in snippets:
        store.add_code_snippet(
            code=snippet.content,
            metadata={
                'file_path': snippet.file_path,
                'language': snippet.language,
                'snippet_type': snippet.snippet_type,
                'name': snippet.name,
                'docstring': snippet.docstring
            }
        )
    
    console.print(f"[green]Analysis complete! {len(snippets)} snippets added to vector store.[/green]")

@main.command()
@click.argument('query', nargs=-1, required=True)
def ask(query):
    """Ask a question about your codebase."""
    question = ' '.join(query)
    console.print(f"[cyan]Processing query: {question}[/cyan]")
    
    llm_manager = LLMManager()
    store = VectorStore()
    snippets = store.search(question, n_results=3)
    
    if snippets['results']:
        context = '\n'.join([res['document'] for res in snippets['results']])
        answer = llm_manager.generate_with_context(query=question, context=context)
        console.print(Panel(
            answer,
            title="[bold green]Answer[/bold green]",
            border_style="green"
        ))
    else:
        console.print("[red]No relevant code snippets found in the knowledge base.[/red]")

@main.command()
@click.argument('path', type=click.Path())
def add(path: str):
    """Add a file or folder to the knowledge base."""
    console.print(f"[cyan]Adding {path} to knowledge base...[/cyan]")
    analyzer = CodeAnalyzer()
    store = VectorStore()
    
    if os.path.isdir(path):
        snippets = analyzer.analyze_directory(Path(path), recursive=False)
    else:
        snippets = analyzer.analyze_file(Path(path))
    
    for snippet in snippets:
        store.add_code_snippet(
            code=snippet.content,
            metadata={
                'file_path': snippet.file_path,
                'language': snippet.language,
                'snippet_type': snippet.snippet_type,
                'name': snippet.name,
                'docstring': snippet.docstring
            }
        )
    
    console.print("[green]Successfully added snippets to knowledge base![green]")

@main.command()
def chat():
    """Start an interactive chat session."""
    console.print("[bold cyan]Starting interactive chat session...[/bold cyan]")
    console.print("[dim]Type 'exit' or 'quit' to end the session[/dim]\n")
    
    llm_manager = LLMManager()
    store = VectorStore()
    
    while True:
        user_input = Prompt.ask("[cyan]You[/cyan]")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            console.print("[yellow]Ending chat session. Goodbye![/yellow]")
            break
        
        # Search for relevant context
        results = store.search(user_input, n_results=3)
        
        if results['results']:
            context = '\n\n'.join([res['document'] for res in results['results']])
            response = llm_manager.generate_with_context(query=user_input, context=context)
        else:
            response = llm_manager.generate(user_input)
        
        console.print(f"[green]CodeInsight[/green]: {response}")

@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.argument('issue', nargs=-1, required=True)
@click.option('--output', '-o', help='Output file for fixed code')
def fix(file: str, issue, output: Optional[str]):
    """Fix code issues in a specific file based on the described issue."""
    issue_description = ' '.join(issue)
    console.print(f"[cyan]Analyzing {file} for: {issue_description}[/cyan]")
    
    try:
        # Read the file content
        with open(file, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        # Initialize LLM
        llm_manager = LLMManager()
        
        # Create a prompt for fixing the code
        fix_prompt = f"""You are an expert programmer. Fix the following issue in the code:

Issue: {issue_description}

Original Code:
```
{original_code}
```

Provide the fixed code with explanations of what was changed and why."""
        
        # Get the fix from LLM
        fixed_response = llm_manager.generate(fix_prompt)
        
        # Display the fix
        console.print(Panel(
            fixed_response,
            title="[bold green]Code Fix[/bold green]",
            border_style="green"
        ))
        
        # Save to output file if specified
        if output:
            # Extract code from response (basic implementation)
            import re
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', fixed_response, re.DOTALL)
            if code_blocks:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(code_blocks[0])
                console.print(f"[green]Fixed code saved to: {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error fixing code: {e}[/red]")

@main.command()
@click.argument('location', type=click.Path(exists=True))
@click.argument('query', nargs=-1, required=True)
@click.option('--depth', '-d', default=2, help='Search depth for directories')
def query_location(location: str, query, depth: int):
    """Query code in a specific location (file or directory)."""
    query_text = ' '.join(query)
    console.print(f"[cyan]Querying '{query_text}' in: {location}[/cyan]")
    
    analyzer = CodeAnalyzer()
    store = VectorStore()
    llm_manager = LLMManager()
    
    # Analyze the location
    if os.path.isdir(location):
        snippets = analyzer.analyze_directory(Path(location), recursive=True)
    else:
        snippets = analyzer.analyze_file(Path(location))
    
    # Create temporary in-memory store for this query
    temp_store = VectorStore()
    for snippet in snippets:
        temp_store.add_code_snippet(
            code=snippet.content,
            metadata={
                'file_path': snippet.file_path,
                'language': snippet.language,
                'snippet_type': snippet.snippet_type,
                'name': snippet.name,
                'docstring': snippet.docstring
            }
        )
    
    # Search for relevant snippets
    results = temp_store.search(query_text, n_results=5)
    
    if results['results']:
        console.print(f"\n[bold]Found {results['count']} relevant code snippets:[/bold]\n")
        
        for i, result in enumerate(results['results'], 1):
            console.print(Panel(
                f"File: {result['metadata']['file_path']}\n"
                f"Type: {result['metadata']['snippet_type']}\n"
                f"Name: {result['metadata'].get('name', 'N/A')}\n\n"
                f"Code:\n{result['document'][:200]}...",
                title=f"[cyan]Result {i}[/cyan]",
                border_style="dim"
            ))
        
        # Generate analysis
        context = '\n\n'.join([res['document'] for res in results['results']])
        analysis = llm_manager.generate_with_context(
            query=f"Analyze the following code snippets related to: {query_text}",
            context=context
        )
        
        console.print(Panel(
            analysis,
            title="[bold green]Analysis[/bold green]",
            border_style="green"
        ))
    else:
        console.print("[yellow]No relevant code found for your query.[/yellow]")

def interactive_mode():
    """Run the interactive menu mode."""
    show_welcome()
    
    options = {
        "1": ("Analyze Code", analyze_interactive),
        "2": ("Ask a Question", ask_interactive),
        "3": ("Chat Mode", chat),
        "4": ("Fix Code Issues", fix_interactive),
        "5": ("Query Location", query_location_interactive),
        "6": ("Add Files/Folders", add_interactive),
        "7": ("Settings", show_settings),
        "8": ("Exit", exit_app)
    }
    
    while True:
        console.print("\n[bold cyan]Main Menu[/bold cyan]")
        
        menu_table = Table(show_header=False, box=box.ROUNDED)
        menu_table.add_column("Option", style="yellow", width=10)
        menu_table.add_column("Action", style="white")
        
        for key, (label, _) in options.items():
            menu_table.add_row(f"[{key}]", label)
        
        console.print(menu_table)
        
        choice = Prompt.ask("\n[bold]Select an option[/bold]", choices=list(options.keys()))
        
        _, action = options[choice]
        if callable(action):
            action()
        else:
            action.main(standalone_mode=False)

def analyze_interactive():
    """Interactive code analysis."""
    path = Prompt.ask("[cyan]Enter file or directory path[/cyan]")
    if os.path.exists(path):
        recursive = Confirm.ask("[cyan]Analyze recursively?[/cyan]", default=True)
        analyze.main([path, '--recursive'] if recursive else [path], standalone_mode=False)
    else:
        console.print("[red]Path does not exist![/red]")

def ask_interactive():
    """Interactive question asking."""
    query = Prompt.ask("[cyan]What would you like to know?[/cyan]")
    ask.main([query], standalone_mode=False)

def add_interactive():
    """Interactive file/folder addition."""
    path = Prompt.ask("[cyan]Enter file or directory path to add[/cyan]")
    if os.path.exists(path):
        add.main([path], standalone_mode=False)
    else:
        console.print("[red]Path does not exist![/red]")

def fix_interactive():
    """Interactive code fixing."""
    file_path = Prompt.ask("[cyan]Enter file path to fix[/cyan]")
    if os.path.exists(file_path) and os.path.isfile(file_path):
        issue = Prompt.ask("[cyan]Describe the issue to fix[/cyan]")
        save_output = Confirm.ask("[cyan]Save fixed code to a new file?[/cyan]", default=False)
        
        if save_output:
            output_path = Prompt.ask("[cyan]Enter output file path[/cyan]", default=file_path + ".fixed")
            fix.main([file_path, issue, '--output', output_path], standalone_mode=False)
        else:
            fix.main([file_path, issue], standalone_mode=False)
    else:
        console.print("[red]File does not exist![/red]")

def query_location_interactive():
    """Interactive location querying."""
    location = Prompt.ask("[cyan]Enter file or directory path to query[/cyan]")
    if os.path.exists(location):
        query = Prompt.ask("[cyan]What would you like to know about this location?[/cyan]")
        query_location.main([location, query], standalone_mode=False)
    else:
        console.print("[red]Location does not exist![/red]")

def show_settings():
    """Display current settings."""
    console.print("\n[bold cyan]Current Settings[/bold cyan]")
    
    settings_table = Table()
    settings_table.add_column("Setting", style="cyan")
    settings_table.add_column("Value", style="yellow")
    
    settings_table.add_row("LLM Model", "mistral (default)")
    settings_table.add_row("Ollama Host", "http://localhost:11434")
    settings_table.add_row("Server Port", "8000")
    settings_table.add_row("Vector DB Path", "./chroma_db")
    
    console.print(settings_table)
    
    if Confirm.ask("\n[cyan]Would you like to modify settings?[/cyan]"):
        console.print("[yellow]Settings modification not yet implemented[/yellow]")

def exit_app():
    """Exit the application."""
    if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
        console.print("[cyan]Thank you for using CodeInsight! Goodbye! 👋[/cyan]")
        sys.exit(0)

if __name__ == '__main__':
    main()
