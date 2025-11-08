"""Web search service using DuckDuckGo (free)"""
from typing import List, Dict
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    print("Warning: duckduckgo-search not available. Install with: pip install duckduckgo-search")

class WebSearchService:
    """Service for web search using DuckDuckGo (free, no API key needed)"""
    
    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with 'title', 'url', and 'body'
        """
        if not DDGS_AVAILABLE:
            return []
        
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', '')[:300]  # Limit snippet length
                    })
                return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []
