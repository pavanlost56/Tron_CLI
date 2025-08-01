"""MCP Browser module for web content extraction."""
import logging
from typing import Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup
from ..core.config import settings

logger = logging.getLogger(__name__)


class WebBrowser:
    """Handle web browsing and content extraction."""
    
    def __init__(self):
        """Initialize the web browser."""
        self.client = httpx.Client(
            timeout=settings.mcp_timeout,
            follow_redirects=True,
            headers={
                'User-Agent': 'CodeInsight/1.0 (AI-powered code assistant)'
            }
        )
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from a URL."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract clean text from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_code_blocks(self, html: str) -> list:
        """Extract code blocks from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            code_blocks = []
            
            # Find <pre> and <code> tags
            for tag in soup.find_all(['pre', 'code']):
                code = tag.get_text().strip()
                if code:
                    code_blocks.append({
                        'code': code,
                        'language': tag.get('class', [''])[0] if tag.get('class') else 'unknown'
                    })
            
            return code_blocks
        except Exception as e:
            logger.error(f"Error extracting code blocks: {e}")
            return []
    
    def search_documentation(self, query: str, site: Optional[str] = None) -> Dict[str, Any]:
        """Search for documentation online."""
        search_url = f"https://www.google.com/search?q={query}"
        if site:
            search_url += f"+site:{site}"
        
        # Note: This is a placeholder. In production, you'd want to use
        # a proper search API or implement more sophisticated scraping
        return {
            'query': query,
            'site': site,
            'results': [],
            'status': 'not_implemented'
        }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'client'):
            self.client.close()



class MCPBrowser:
    """Browser client for fetching real-time documentation."""
    
    def __init__(self):
        self.timeout = settings.mcp_timeout
        self.max_retries = settings.max_retries
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch content from a URL."""
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.text
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                        return None
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def extract_text(self, html: str) -> str:
        """Extract text content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def fetch_documentation(self, framework: str, topic: str) -> Optional[str]:
        """Fetch documentation for a specific framework and topic."""
        # Map frameworks to their documentation URLs
        doc_urls = {
            "tailwindcss": f"https://tailwindcss.com/docs/{topic.lower().replace(' ', '-')}",
            "nextjs": f"https://nextjs.org/docs/{topic.lower().replace(' ', '-')}",
            "react": f"https://react.dev/reference/{topic.lower().replace(' ', '-')}",
            "vue": f"https://vuejs.org/guide/{topic.lower().replace(' ', '-')}.html",
            "typescript": f"https://www.typescriptlang.org/docs/handbook/{topic.lower().replace(' ', '-')}.html"
        }
        
        base_url = doc_urls.get(framework.lower())
        if not base_url:
            logger.warning(f"No documentation URL found for framework: {framework}")
            return None
        
        html = await self.fetch_url(base_url)
        if html:
            return self.extract_text(html)
        return None
    
    async def search_stackoverflow(self, query: str, limit: int = 3) -> List[Dict[str, str]]:
        """Search Stack Overflow for relevant answers."""
        search_url = f"https://api.stackexchange.com/2.3/search/advanced"
        params = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "site": "stackoverflow",
            "pagesize": limit
        }
        
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", []):
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "score": item.get("score", 0),
                        "is_answered": item.get("is_answered", False)
                    })
                
                return results
            except Exception as e:
                logger.error(f"Error searching Stack Overflow: {e}")
                return []
    
    async def get_npm_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get information about an npm package."""
        url = f"https://registry.npmjs.org/{package_name}/latest"
        
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "name": data.get("name"),
                    "version": data.get("version"),
                    "description": data.get("description"),
                    "homepage": data.get("homepage"),
                    "repository": data.get("repository", {}).get("url"),
                    "dependencies": list(data.get("dependencies", {}).keys()),
                    "peerDependencies": list(data.get("peerDependencies", {}).keys())
                }
            except Exception as e:
                logger.error(f"Error fetching npm package info: {e}")
                return None


class DocumentationFetcher:
    """High-level interface for fetching documentation."""
    
    def __init__(self):
        self.browser = MCPBrowser()
    
    async def get_current_docs(self, framework: str, topic: str) -> str:
        """Get current documentation for a framework topic."""
        docs = await self.browser.fetch_documentation(framework, topic)
        if docs:
            return f"Current documentation for {framework} - {topic}:\n\n{docs[:2000]}..."
        return f"Could not fetch documentation for {framework} - {topic}"
    
    async def search_solutions(self, problem: str) -> str:
        """Search for solutions to a problem."""
        results = await self.browser.search_stackoverflow(problem)
        if results:
            output = f"Found {len(results)} relevant solutions:\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. {result['title']}\n"
                output += f"   Link: {result['link']}\n"
                output += f"   Score: {result['score']} | Answered: {result['is_answered']}\n\n"
            return output
        return "No solutions found for the given problem."
    
    async def check_package_version(self, package_name: str) -> str:
        """Check the latest version of a package."""
        info = await self.browser.get_npm_package_info(package_name)
        if info:
            output = f"Package: {info['name']} v{info['version']}\n"
            output += f"Description: {info['description']}\n"
            if info.get('homepage'):
                output += f"Homepage: {info['homepage']}\n"
            if info.get('dependencies'):
                output += f"Dependencies: {', '.join(info['dependencies'][:5])}"
                if len(info['dependencies']) > 5:
                    output += f" and {len(info['dependencies']) - 5} more"
            return output
        return f"Could not find package information for {package_name}"
