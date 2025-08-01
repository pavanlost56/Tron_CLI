"""Code analyzer for parsing and extracting information from source files."""
import ast
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    """Represents a code snippet with metadata."""
    content: str
    file_path: str
    language: str
    start_line: int
    end_line: int
    snippet_type: str  # function, class, module, etc.
    name: Optional[str] = None
    docstring: Optional[str] = None


class CodeAnalyzer:
    """Analyze source code files and extract meaningful snippets."""
    
    # Language extensions mapping
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.go': 'go',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.cs': 'csharp',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.jl': 'julia',
        '.lua': 'lua',
        '.dart': 'dart',
        '.ex': 'elixir',
        '.ml': 'ocaml',
        '.hs': 'haskell',
        '.pl': 'perl',
        '.sh': 'bash',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.xml': 'xml',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.rst': 'restructuredtext',
        '.tex': 'latex',
    }
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.parsers = {
            'python': self._parse_python,
            'javascript': self._parse_javascript,
            'go': self._parse_go,
            # Add more parsers as needed
        }
    
    def analyze_file(self, file_path: Path) -> List[CodeSnippet]:
        """Analyze a single file and extract code snippets."""
        try:
            # Detect language
            language = self._detect_language(file_path)
            if not language:
                logger.warning(f"Unknown file type: {file_path}")
                return []
            
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Parse based on language
            if language in self.parsers:
                return self.parsers[language](content, str(file_path), language)
            else:
                # Default parsing for unsupported languages
                return self._parse_generic(content, str(file_path), language)
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return []
    
    def analyze_directory(self, directory: Path, recursive: bool = True) -> List[CodeSnippet]:
        """Analyze all files in a directory."""
        snippets = []
        
        pattern = '**/*' if recursive else '*'
        for file_path in directory.glob(pattern):
            if file_path.is_file() and not self._should_ignore(file_path):
                snippets.extend(self.analyze_file(file_path))
        
        return snippets
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        return self.LANGUAGE_MAP.get(suffix)
    
    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored."""
        ignore_patterns = [
            '__pycache__',
            '.git',
            '.venv',
            'venv',
            'node_modules',
            '.idea',
            '.vscode',
            'dist',
            'build',
            '.egg-info',
            '.pytest_cache',
            '.mypy_cache',
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in ignore_patterns)
    
    def _parse_python(self, content: str, file_path: str, language: str) -> List[CodeSnippet]:
        """Parse Python code and extract functions, classes, and docstrings."""
        snippets = []
        
        try:
            tree = ast.parse(content)
            
            # Extract module-level docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                snippets.append(CodeSnippet(
                    content=module_docstring,
                    file_path=file_path,
                    language=language,
                    start_line=1,
                    end_line=len(module_docstring.split('\n')),
                    snippet_type='module_docstring',
                    name='module'
                ))
            
            # Walk through AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    snippet = self._extract_python_function(node, content, file_path, language)
                    if snippet:
                        snippets.append(snippet)
                elif isinstance(node, ast.ClassDef):
                    snippet = self._extract_python_class(node, content, file_path, language)
                    if snippet:
                        snippets.append(snippet)
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            # Fall back to generic parsing
            snippets = self._parse_generic(content, file_path, language)
        
        return snippets
    
    def _extract_python_function(self, node: ast.FunctionDef, content: str, file_path: str, language: str) -> Optional[CodeSnippet]:
        """Extract a Python function."""
        try:
            # Get function source
            lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
            
            # Find actual end by looking for dedentation
            if end_line >= len(lines):
                end_line = len(lines) - 1
            
            function_lines = lines[start_line:end_line]
            function_content = '\n'.join(function_lines)
            
            # Get docstring
            docstring = ast.get_docstring(node)
            
            return CodeSnippet(
                content=function_content,
                file_path=file_path,
                language=language,
                start_line=node.lineno,
                end_line=end_line + 1,
                snippet_type='function',
                name=node.name,
                docstring=docstring
            )
        except Exception as e:
            logger.error(f"Error extracting function {node.name}: {e}")
            return None
    
    def _extract_python_class(self, node: ast.ClassDef, content: str, file_path: str, language: str) -> Optional[CodeSnippet]:
        """Extract a Python class."""
        try:
            # Get class source
            lines = content.split('\n')
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
            
            if end_line >= len(lines):
                end_line = len(lines) - 1
            
            class_lines = lines[start_line:end_line]
            class_content = '\n'.join(class_lines)
            
            # Get docstring
            docstring = ast.get_docstring(node)
            
            return CodeSnippet(
                content=class_content,
                file_path=file_path,
                language=language,
                start_line=node.lineno,
                end_line=end_line + 1,
                snippet_type='class',
                name=node.name,
                docstring=docstring
            )
        except Exception as e:
            logger.error(f"Error extracting class {node.name}: {e}")
            return None
    
    def _parse_javascript(self, content: str, file_path: str, language: str) -> List[CodeSnippet]:
        """Parse JavaScript code using regex patterns."""
        snippets = []
        
        # Function patterns
        function_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)\s*{',  # function declaration
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',  # arrow function
            r'const\s+(\w+)\s*=\s*function\s*\([^)]*\)\s*{',  # function expression
        ]
        
        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                start = match.start()
                
                # Find the end of the function (rough estimate)
                brace_count = 1
                end = match.end()
                while brace_count > 0 and end < len(content):
                    if content[end] == '{':
                        brace_count += 1
                    elif content[end] == '}':
                        brace_count -= 1
                    end += 1
                
                function_content = content[start:end]
                start_line = content[:start].count('\n') + 1
                end_line = content[:end].count('\n') + 1
                
                snippets.append(CodeSnippet(
                    content=function_content,
                    file_path=file_path,
                    language=language,
                    start_line=start_line,
                    end_line=end_line,
                    snippet_type='function',
                    name=name
                ))
        
        # Class patterns
        class_pattern = r'class\s+(\w+)\s*(?:extends\s+\w+\s*)?{'
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            start = match.start()
            
            # Find the end of the class
            brace_count = 1
            end = match.end()
            while brace_count > 0 and end < len(content):
                if content[end] == '{':
                    brace_count += 1
                elif content[end] == '}':
                    brace_count -= 1
                end += 1
            
            class_content = content[start:end]
            start_line = content[:start].count('\n') + 1
            end_line = content[:end].count('\n') + 1
            
            snippets.append(CodeSnippet(
                content=class_content,
                file_path=file_path,
                language=language,
                start_line=start_line,
                end_line=end_line,
                snippet_type='class',
                name=name
            ))
        
        return snippets
    
    def _parse_go(self, content: str, file_path: str, language: str) -> List[CodeSnippet]:
        """Parse Go code using regex patterns."""
        snippets = []
        
        # Function patterns
        function_pattern = r'func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\([^)]*\)\s*(?:\([^)]*\)\s*)?(?:{|$)'
        for match in re.finditer(function_pattern, content, re.MULTILINE):
            name = match.group(1)
            start = match.start()
            
            # Find the end of the function
            if content[match.end()-1] == '{':
                brace_count = 1
                end = match.end()
                while brace_count > 0 and end < len(content):
                    if content[end] == '{':
                        brace_count += 1
                    elif content[end] == '}':
                        brace_count -= 1
                    end += 1
            else:
                # Interface method or similar
                end = content.find('\n', match.end()) + 1
            
            function_content = content[start:end]
            start_line = content[:start].count('\n') + 1
            end_line = content[:end].count('\n') + 1
            
            snippets.append(CodeSnippet(
                content=function_content,
                file_path=file_path,
                language=language,
                start_line=start_line,
                end_line=end_line,
                snippet_type='function',
                name=name
            ))
        
        # Struct patterns
        struct_pattern = r'type\s+(\w+)\s+struct\s*{'
        for match in re.finditer(struct_pattern, content):
            name = match.group(1)
            start = content.rfind('\n', 0, match.start()) + 1  # Include type declaration
            
            # Find the end of the struct
            brace_count = 1
            end = match.end()
            while brace_count > 0 and end < len(content):
                if content[end] == '{':
                    brace_count += 1
                elif content[end] == '}':
                    brace_count -= 1
                end += 1
            
            struct_content = content[start:end]
            start_line = content[:start].count('\n') + 1
            end_line = content[:end].count('\n') + 1
            
            snippets.append(CodeSnippet(
                content=struct_content,
                file_path=file_path,
                language=language,
                start_line=start_line,
                end_line=end_line,
                snippet_type='struct',
                name=name
            ))
        
        return snippets
    
    def _parse_generic(self, content: str, file_path: str, language: str) -> List[CodeSnippet]:
        """Generic parsing for unsupported languages - split into chunks."""
        snippets = []
        lines = content.split('\n')
        
        # Create chunks of reasonable size
        chunk_size = 50  # lines per chunk
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            
            if chunk_content.strip():  # Skip empty chunks
                snippets.append(CodeSnippet(
                    content=chunk_content,
                    file_path=file_path,
                    language=language,
                    start_line=i + 1,
                    end_line=min(i + chunk_size, len(lines)),
                    snippet_type='chunk',
                    name=f'chunk_{i // chunk_size + 1}'
                ))
        
        return snippets
