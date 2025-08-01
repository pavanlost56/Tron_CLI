# CodeInsight Installation & Setup Guide

This guide documents the complete process of setting up CodeInsight as a globally accessible CLI tool on Windows.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Making CodeInsight Global](#making-codeinsight-global)
5. [Dependencies Used](#dependencies-used)
6. [Troubleshooting](#troubleshooting)

## Project Overview

CodeInsight is an AI-powered CLI tool for code analysis, built with:
- **Frontend (CLI)**: Python with Rich library for beautiful terminal UI
- **Backend**: FastAPI for server components
- **AI/LLM**: Ollama for local LLM, LangChain for orchestration
- **Vector Database**: ChromaDB for semantic search
- **Embeddings**: Sentence Transformers

## Prerequisites

1. **Python 3.12** (verified with `python --version`)
2. **Visual Studio Community** or **Microsoft C++ Build Tools** (for compiling some dependencies)
3. **Git** (for version control)
4. **PowerShell 7.x** (for terminal commands)

## Step-by-Step Installation

### 1. Clone/Navigate to Project
```bash
cd D:\Tron_CLI\codeinsight
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Core Dependencies

#### Install from requirements.txt (if exists)
```bash
pip install -r requirements.txt
```

#### Or install individual packages
```bash
# Core CLI libraries
pip install click==8.2.1
pip install typer==0.16.0
pip install rich==14.0.0

# FastAPI and server
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0

# AI/LLM libraries
pip install langchain==0.1.0
pip install ollama==0.1.6
pip install chromadb==1.0.15  # Latest version
pip install sentence-transformers==2.2.2

# Additional utilities
pip install python-dotenv==1.0.0
pip install httpx==0.25.2
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install aiohttp==3.9.1
```

### 5. Handle ChromaDB Installation Issues

If you encounter compilation errors with ChromaDB:
```bash
# Install the latest pre-built version
pip install chromadb --upgrade
```

### 6. Install PyTorch (for Sentence Transformers)
```bash
pip install torch torchvision
```

## Making CodeInsight Global

### Method 1: Using pip install --user (Recommended)

1. **Exit virtual environment**
```bash
deactivate
```

2. **Install pipx globally** (for isolated global installations)
```bash
pip install --user pipx
python -m pipx ensurepath
```

3. **Install CodeInsight globally**
```bash
# From the project directory
pip install --user -e .
```

4. **Add Python Scripts to PATH**

The installation will place the executable in:
```
C:\Users\[YourUsername]\AppData\Roaming\Python\Python312\Scripts\
```

To ensure it's in PATH:
```powershell
python -m pipx ensurepath --force
```

5. **Refresh PATH in current session**
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Method 2: Using pipx (Alternative)

```bash
# Install pipx if not already installed
pip install --user pipx

# Use pipx to install globally
pipx install .
```

### Method 3: Direct Installation

```bash
# Install directly to global Python
pip install .
```

## Project Structure

```
codeinsight/
├── src/
│   └── codeinsight/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py          # Main CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── config.py
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py        # LLM client implementation
│       ├── mcp/
│       │   ├── __init__.py
│       │   └── browser.py
│       ├── rag/
│       │   └── __init__.py
│       └── utils/
│           └── __init__.py
├── tests/
├── pyproject.toml               # Package configuration
├── requirements.txt             # Dependencies
├── .env                        # Environment variables
└── README.md

```

## pyproject.toml Configuration

The `pyproject.toml` file defines how the CLI is installed:

```toml
[project]
name = "codeinsight"
version = "0.1"
dependencies = [
    "click",
    "typer",
]

[project.scripts]
codeinsight = "codeinsight.cli.main:main"
```

This creates the `codeinsight` command that runs the `main` function from `src/codeinsight/cli/main.py`.

## Dependencies Used

### CLI Interface
- **click**: Basic command-line interface framework
- **typer**: Modern CLI framework built on Click
- **rich**: Beautiful terminal formatting, tables, panels, and colors

### AI/LLM Stack
- **langchain**: LLM orchestration framework
- **ollama**: Local LLM runtime
- **chromadb**: Vector database for semantic search
- **sentence-transformers**: Generate embeddings for text

### Web Framework
- **fastapi**: Modern web API framework
- **uvicorn**: ASGI server for FastAPI

### Utilities
- **python-dotenv**: Load environment variables from .env
- **httpx**: HTTP client library
- **beautifulsoup4**: Web scraping
- **aiohttp**: Async HTTP client/server

## Commands Summary

### Virtual Environment Commands
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Deactivate
deactivate
```

### Installation Commands
```bash
# Install in development mode (editable)
pip install -e .

# Install globally for current user
pip install --user -e .

# Force reinstall
pip install --user -e . --force-reinstall

# Install without dependencies
pip install --user -e . --no-deps
```

### Running CodeInsight
```bash
# After global installation
codeinsight

# With commands
codeinsight analyze /path/to/code
codeinsight ask "your question"
codeinsight chat
codeinsight add /path/to/folder

# If not in PATH
C:\Users\[YourUsername]\AppData\Roaming\Python\Python312\Scripts\codeinsight.exe
```

## Troubleshooting

### "Module not found" errors
- Ensure all dependencies are installed in the active environment
- Check if virtual environment is activated

### "codeinsight not recognized" error
1. Close and reopen terminal
2. Check if Scripts directory is in PATH:
   ```powershell
   echo $env:Path
   ```
3. Manually add to PATH if needed

### ChromaDB compilation errors
- Ensure Visual Studio C++ Build Tools are installed
- Use pre-built wheels: `pip install chromadb --upgrade`

### HTTPx version conflicts
- If Ollama requires different HTTPx version:
  ```bash
  pip install httpx==0.25.2
  ```

## Next Steps

1. **Install Ollama**: Download from https://ollama.ai
2. **Pull a model**: `ollama pull mistral`
3. **Configure settings**: Edit `.env` file
4. **Start using**: Run `codeinsight` to access the interactive menu

## Version Information

- CodeInsight: v0.1.0
- Python: 3.12
- LangChain: 0.1.0
- ChromaDB: 1.0.15
- Ollama: 0.1.6

---

*Document created: January 2025*
*Last updated: January 9, 2025*
