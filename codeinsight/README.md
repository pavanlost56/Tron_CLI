# CodeInsight: AI-Powered Codebase Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-brightgreen)](https://ollama.ai/)

CodeInsight is an open-source, AI-powered command-line interface (CLI) tool that revolutionizes how developers interact with codebases. By combining local LLMs via Ollama with advanced RAG (Retrieval-Augmented Generation) capabilities, CodeInsight provides intelligent code analysis, natural language querying, and automated code fixing.

## 🚀 Key Features

### 🧠 Local LLM Integration
- Powered by Ollama with CodeLlama 13B model
- Privacy-first approach - your code never leaves your machine
- Support for multiple models (CodeLlama, DeepSeek Coder, Llama 3.1)

### 🔍 Advanced RAG Capabilities
- ChromaDB-powered vector storage for code embeddings
- Semantic search across your entire codebase
- Multi-language support (Python, JavaScript, Go, and more)

### 💡 Intelligent Features
- **Analyze**: Deep code analysis with AI-generated insights
- **Query**: Natural language questions about your codebase
- **Fix**: Automated code issue detection and fixing
- **Chat**: Interactive conversations with code context
- **Search**: Find relevant code snippets by location

### 🌐 Web Documentation Integration
- MCP browser support for real-time documentation
- Extract and analyze web content alongside code

### 🚀 Flexible Deployment
- CLI interface for terminal usage
- FastAPI server for REST API access
- Interactive menu system

## 🎯 Problem We Solve

Ever followed AI-generated installation commands only to find they're outdated? CodeInsight solves this by combining local LLM reasoning with real-time web data, ensuring you always get current, accurate solutions for:

- Framework installation commands
- Breaking changes and migration guides
- Dependency compatibility checks
- Latest syntax and best practices

## 📦 Installation

### Prerequisites
- Python 3.8+
- Ollama installed and running
- 8GB+ RAM (16GB recommended for larger models)
- GPU optional but beneficial

### Quick Start

#### 1. Install Ollama (Windows/Mac/Linux)
```bash
# Windows (PowerShell as Administrator)
# Download from: https://ollama.ai/download/windows

# Mac/Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. Pull the CodeLlama model
```bash
# Recommended for code analysis (13B parameters)
ollama pull codellama:13b

# Alternative smaller model (7B parameters)
ollama pull codellama:7b
```

#### 3. Clone and Install CodeInsight
```bash
# Clone the repository
git clone https://github.com/yourusername/codeinsight.git
cd codeinsight

# Create virtual environment (recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install CodeInsight
pip install -e .
```

#### 4. Set Environment Variables (Optional)
```bash
# Windows (PowerShell)
$env:OLLAMA_HOST="http://localhost:11434"
$env:OLLAMA_MODELS="D:\ollama-models"  # Custom model storage

# Mac/Linux
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODELS="/path/to/ollama-models"
```

## 💻 Usage Examples

### Get Current Installation Commands
```bash
# TailwindCSS with Next.js 14
codeinsight install "TailwindCSS with Next.js 14"

# Returns current commands for TailwindCSS 4.1+
```

### Check Breaking Changes
```bash
# Upgrade guidance
codeinsight upgrade "Next.js 13 to 14"

# Returns migration guide with solutions
```

### Analyze Your Codebase
```bash
# Index your project
codeinsight index /path/to/project

# Ask questions about your code
codeinsight ask "What does the authentication flow do?"
```

### Interactive Mode
```bash
# Start conversational interface
codeinsight interactive
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User CLI      │────│   CodeInsight   │────│   Docker        │
│   Interface     │    │   Core Engine   │    │   Container     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    │                   │
           ┌─────────────────┐ ┌─────────────────┐
           │   Local LLM     │ │   MCP Client    │
           │   (Reasoning)   │ │   (Live Docs)   │
           └─────────────────┘ └─────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Architecture Overview](docs/architecture.md)

## 🗺️ Roadmap

- [x] Core RAG pipeline
- [x] Local LLM integration
- [x] MCP browsing capabilities
- [ ] Plugin system
- [ ] VS Code extension
- [ ] Web UI interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mallareddy College of Engineering & Technology
- LangChain community
- Ollama team
- All our contributors

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/codeinsight/issues)
- Discussions: [Join the community](https://github.com/yourusername/codeinsight/discussions)
- Email: support@codeinsight.dev

---
Made with ❤️ by the CodeInsight team
