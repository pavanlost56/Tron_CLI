from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
from pathlib import Path

from ..llm.client import LLMManager
from ..rag import VectorStore, CodeAnalyzer
from ..mcp import WebBrowser
from .config import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeInsight API",
    description="AI-powered code analysis and assistance API",
    version="0.1.0"
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    context_limit: Optional[int] = 5

class AnalyzeRequest(BaseModel):
    path: str
    recursive: bool = True

class FixRequest(BaseModel):
    file_path: str
    issue_description: str

class WebSearchRequest(BaseModel):
    query: str
    site: Optional[str] = None

# Initialize services
llm_manager = LLMManager()
vector_store = VectorStore()
code_analyzer = CodeAnalyzer()
web_browser = WebBrowser()

@app.get("/")
async def read_root():
    return {
        "service": "CodeInsight API",
        "version": "0.1.0",
        "status": "ready",
        "endpoints": [
            "/analyze",
            "/query",
            "/fix",
            "/add",
            "/search",
            "/stats"
        ]
    }

@app.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    """Analyze code in a file or directory."""
    try:
        path = Path(request.path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if path.is_dir():
            snippets = code_analyzer.analyze_directory(path, request.recursive)
        else:
            snippets = code_analyzer.analyze_file(path)
        
        # Add to vector store
        for snippet in snippets:
            vector_store.add_code_snippet(
                code=snippet.content,
                metadata={
                    'file_path': snippet.file_path,
                    'language': snippet.language,
                    'snippet_type': snippet.snippet_type,
                    'name': snippet.name,
                    'docstring': snippet.docstring
                }
            )
        
        return {
            "status": "success",
            "snippets_analyzed": len(snippets),
            "path": str(path)
        }
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_codebase(request: QueryRequest):
    """Query the codebase with a question."""
    try:
        # Search for relevant snippets
        results = vector_store.search(request.query, n_results=request.context_limit)
        
        if results['results']:
            # Generate context from results
            context = '\n\n'.join([res['document'] for res in results['results']])
            
            # Get answer from LLM
            answer = llm_manager.generate_with_context(
                query=request.query,
                context=context
            )
            
            return {
                "query": request.query,
                "answer": answer,
                "sources": [
                    {
                        "file": res['metadata']['file_path'],
                        "type": res['metadata']['snippet_type'],
                        "name": res['metadata'].get('name', 'N/A')
                    }
                    for res in results['results']
                ]
            }
        else:
            return {
                "query": request.query,
                "answer": "No relevant code snippets found in the knowledge base.",
                "sources": []
            }
    except Exception as e:
        logger.error(f"Error querying codebase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fix")
async def fix_code(request: FixRequest):
    """Fix code issues in a specific file."""
    try:
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read file content
        original_code = file_path.read_text(encoding='utf-8')
        
        # Create fix prompt
        fix_prompt = f"""You are an expert programmer. Fix the following issue in the code:

Issue: {request.issue_description}

Original Code:
```
{original_code}
```

Provide the fixed code with explanations of what was changed and why."""
        
        # Get fix from LLM
        fixed_response = llm_manager.generate(fix_prompt)
        
        return {
            "status": "success",
            "file_path": str(file_path),
            "issue": request.issue_description,
            "fix": fixed_response
        }
    except Exception as e:
        logger.error(f"Error fixing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_files(files: List[UploadFile] = File(...)):
    """Add uploaded files to the knowledge base."""
    try:
        results = []
        for file in files:
            content = await file.read()
            text_content = content.decode('utf-8', errors='ignore')
            
            # Detect language from filename
            file_path = Path(file.filename)
            language = code_analyzer._detect_language(file_path) or 'unknown'
            
            # Parse content
            if language in code_analyzer.parsers:
                snippets = code_analyzer.parsers[language](
                    text_content,
                    file.filename,
                    language
                )
            else:
                snippets = code_analyzer._parse_generic(
                    text_content,
                    file.filename,
                    language
                )
            
            # Add to vector store
            for snippet in snippets:
                vector_store.add_code_snippet(
                    code=snippet.content,
                    metadata={
                        'file_path': snippet.file_path,
                        'language': snippet.language,
                        'snippet_type': snippet.snippet_type,
                        'name': snippet.name,
                        'docstring': snippet.docstring
                    }
                )
            
            results.append({
                "file": file.filename,
                "snippets": len(snippets)
            })
        
        return {
            "status": "success",
            "files_processed": len(files),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error adding files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_web(request: WebSearchRequest):
    """Search for documentation or information online."""
    try:
        results = web_browser.search_documentation(request.query, request.site)
        return results
    except Exception as e:
        logger.error(f"Error searching web: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get statistics about the knowledge base."""
    try:
        stats = vector_store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
