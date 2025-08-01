#!/usr/bin/env python3
"""Test script to verify CodeInsight functionality."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from codeinsight.llm.client import LLMManager
from codeinsight.rag import VectorStore, CodeAnalyzer
from codeinsight.mcp import WebBrowser
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)


def test_llm_connection():
    """Test connection to Ollama."""
    print("\n🔍 Testing LLM Connection...")
    try:
        llm = LLMManager()
        response = llm.generate("Hello, CodeInsight!")
        print(f"✅ LLM Response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return False


def test_vector_store():
    """Test vector store functionality."""
    print("\n🔍 Testing Vector Store...")
    try:
        store = VectorStore()
        
        # Add a test snippet
        snippet_id = store.add_code_snippet(
            code="def hello_world():\n    print('Hello, World!')",
            metadata={
                'file_path': 'test.py',
                'language': 'python',
                'snippet_type': 'function',
                'name': 'hello_world'
            }
        )
        print(f"✅ Added snippet: {snippet_id}")
        
        # Search for it
        results = store.search("hello world function", n_results=1)
        print(f"✅ Search results: {results['count']} found")
        
        return True
    except Exception as e:
        print(f"❌ Vector Store Error: {e}")
        return False


def test_code_analyzer():
    """Test code analyzer functionality."""
    print("\n🔍 Testing Code Analyzer...")
    try:
        analyzer = CodeAnalyzer()
        
        # Create a test file
        test_file = Path("test_sample.py")
        test_file.write_text("""
def sample_function(x, y):
    '''Add two numbers.'''
    return x + y

class SampleClass:
    '''A sample class.'''
    def __init__(self):
        self.value = 42
""")
        
        # Analyze it
        snippets = analyzer.analyze_file(test_file)
        print(f"✅ Found {len(snippets)} code snippets")
        
        # Clean up
        test_file.unlink()
        
        return True
    except Exception as e:
        print(f"❌ Code Analyzer Error: {e}")
        return False


def test_web_browser():
    """Test web browser functionality."""
    print("\n🔍 Testing Web Browser...")
    try:
        browser = WebBrowser()
        
        # Test URL fetching
        content = browser.fetch_url("https://httpbin.org/html")
        if content:
            print("✅ Successfully fetched web content")
            
            # Test text extraction
            text = browser.extract_text(content)
            print(f"✅ Extracted {len(text)} characters of text")
            
            return True
        else:
            print("❌ Failed to fetch web content")
            return False
    except Exception as e:
        print(f"❌ Web Browser Error: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting CodeInsight Tests...\n")
    
    tests = [
        ("LLM Connection", test_llm_connection),
        ("Vector Store", test_vector_store),
        ("Code Analyzer", test_code_analyzer),
        ("Web Browser", test_web_browser),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 40)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:<20} {status}")
    
    print("=" * 40)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! CodeInsight is ready to use.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
