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
    
    @staticmethod
    def iterative_research(query: str, max_iterations: int = 3, results_per_search: int = 5) -> List[Dict[str, str]]:
        """
        Perform iterative research by searching, analyzing gaps, and refining queries
        
        Args:
            query: Initial search query
            max_iterations: Maximum number of search iterations
            results_per_search: Number of results per search
            
        Returns:
            Combined list of unique search results from all iterations
        """
        if not DDGS_AVAILABLE:
            return []
        
        all_results = []
        seen_urls = set()
        current_query = query
        
        try:
            from app.services.llm_service import LLMService
            
            for iteration in range(max_iterations):
                # Perform search with current query
                search_results = WebSearchService.search(current_query, max_results=results_per_search)
                
                # Add unique results
                for result in search_results:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)
                
                # If this is the last iteration, stop
                if iteration == max_iterations - 1:
                    break
                
                # Analyze results and generate refined query
                if all_results:
                    # Build context from current results
                    results_summary = "\n".join([
                        f"- {r.get('title', '')}: {r.get('snippet', '')[:200]}"
                        for r in all_results[-results_per_search:]
                    ])
                    
                    # Use LLM to generate refined search query
                    refinement_prompt = f"""Based on the initial query "{query}" and the following search results, identify what information might be missing or what aspects need deeper investigation.

Initial Query: {query}

Current Results Summary:
{results_summary}

Generate a refined search query that would help find additional relevant information. Focus on:
1. Different angles or perspectives on the topic
2. More specific aspects that weren't covered
3. Related concepts or recent developments

Respond with ONLY the refined search query (no explanation, just the query):"""
                    
                    try:
                        refined_query = LLMService.call_llm([{"role": "user", "content": refinement_prompt}])
                        refined_query = refined_query.strip()
                        
                        # If the refined query is too similar or empty, stop iterating
                        if not refined_query or refined_query.lower() == query.lower():
                            break
                        
                        current_query = refined_query
                    except Exception as e:
                        print(f"Error generating refined query: {e}")
                        break
                else:
                    # No results found, stop iterating
                    break
            
            return all_results
            
        except Exception as e:
            print(f"Iterative research error: {e}")
            # Fallback to single search
            return WebSearchService.search(query, max_results=results_per_search * max_iterations)