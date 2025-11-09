"""Chat routes blueprint"""
from flask import Blueprint, request, jsonify, session as flask_session
import re
import uuid
from app.services.llm_service import LLMService
from app.services.storage import storage
from app.services.web_search import WebSearchService
from app.services.reasoning_service import ReasoningService
from app.services.langgraph_service import initialize_rag, langgraph_service, rag_service

chat_bp = Blueprint('chat', __name__)

# Initialize RAG system on module load
_rag_initialized = False
def ensure_rag_initialized():
    global _rag_initialized
    if not _rag_initialized:
        _rag_initialized = initialize_rag()

def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in flask_session:
        flask_session['session_id'] = str(uuid.uuid4())
    return flask_session['session_id']

@chat_bp.route('', methods=['POST'])
def handle_chat():
    """Handle chat queries with multiple simultaneous capabilities"""
    ensure_rag_initialized()
    
    data = request.json or {}
    query = data.get('question', '').strip()
    session_id = get_session_id()
    
    # Get capability flags (default to RAG only if none specified)
    use_rag = data.get('use_rag', True)
    use_web_search = data.get('use_web_search', False)
    use_research = data.get('use_research', False)
    use_thinking = data.get('use_thinking', False)

    if not query:
        return jsonify({"error": "No question provided"}), 400

    # Ensure at least one capability is enabled
    if not (use_rag or use_web_search or use_research or use_thinking):
        use_rag = True  # Default fallback

    try:
        # Get conversation history
        conversation = storage.get_conversation(session_id)
        
        # Add user message
        conversation.append({"role": "user", "content": query})
        storage.add_message(session_id, "user", query)

        answer = ""
        thinking_layers = []
        search_results = []
        retrieved_docs = []

        # Check if RAG is available and has documents
        rag_available = rag_service and rag_service.is_ready()
        
        # Collect context from all enabled capabilities
        context_parts = []
        
        # 1. RAG: Retrieve from knowledge base
        if use_rag and rag_available:
            rag_docs = rag_service.search(query, k=4)
            if rag_docs:
                retrieved_docs = rag_docs
                kb_context = "Relevant information from knowledge base:\n"
                for i, doc in enumerate(rag_docs, 1):
                    source = doc.get('metadata', {}).get('source', 'Knowledge Base')
                    kb_context += f"{i}. [KB] {source}: {doc['content'][:400]}...\n\n"
                context_parts.append(kb_context)
        
        # 2. Research: Iterative web search (includes web search functionality)
        if use_research:
            search_results = WebSearchService.iterative_research(query, max_iterations=3, results_per_search=5)
            if search_results:
                research_context = "Relevant web search results (from iterative research):\n"
                for i, result in enumerate(search_results, 1):
                    research_context += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n\n"
                context_parts.append(research_context)
        
        # 3. Web Search: Single web search (only if research is not enabled)
        elif use_web_search:
            search_results = WebSearchService.search(query, max_results=5)
            if search_results:
                web_context = "Relevant web search results:\n"
                for i, result in enumerate(search_results, 1):
                    web_context += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n\n"
                context_parts.append(web_context)
        
        # Build comprehensive context
        if context_parts:
            full_context = f"User question: {query}\n\n"
            full_context += "\n".join(context_parts)
            full_context += "\nBased on the above information, provide a comprehensive answer. Cite sources when relevant."
        else:
            full_context = query
        
        # 4. Thinking: Apply Chain of Thought reasoning
        if use_thinking:
            # Use context if available, otherwise use original query
            reasoning_query = full_context if context_parts else query
            # Use CoT reasoning with system message
            reasoning_result = ReasoningService.cot_reasoning(reasoning_query, conversation[:-1], use_system_message=True)
            answer = reasoning_result['answer']
            thinking = reasoning_result['thinking']
            
            # Convert thinking to layers format for frontend compatibility
            # Parse the three-phase structure if present
            if thinking:
                # Check if it follows the three-phase structure
                phase_patterns = {
                    'Phase 1': r'Phase\s*1[:\s]*🧐?\s*ANALYSIS[:\s]*(.*?)(?=Phase\s*2|$)',
                    'Phase 2': r'Phase\s*2[:\s]*🗺️?\s*PLANNING[:\s]*(.*?)(?=Phase\s*3|$)',
                    'Phase 3': r'Phase\s*3[:\s]*✅?\s*EXECUTION[:\s]*(.*?)$'
                }
                
                # Map phase numbers to descriptive names
                phase_names = {
                    'Phase 1': '🧐 Analysis',
                    'Phase 2': '🗺️ Planning',
                    'Phase 3': '✅ Execution & Verification'
                }
                
                phases_found = []
                for phase_key, pattern in phase_patterns.items():
                    match = re.search(pattern, thinking, re.IGNORECASE | re.DOTALL)
                    if match:
                        phases_found.append({
                            'number': len(phases_found) + 1,
                            'name': phase_names.get(phase_key, phase_key.replace('Phase ', '')),
                            'reasoning': match.group(1).strip()
                        })
                
                if len(phases_found) == 3:
                    # Three-phase structure found - use it
                    thinking_layers = phases_found
                else:
                    # Fallback: split by paragraphs or sections
                    thinking_parts = [part.strip() for part in thinking.split('\n\n') if part.strip()]
                    if len(thinking_parts) > 1:
                        # Multiple steps - create layers
                        thinking_layers = [
                            {'number': i+1, 'name': f'Reasoning Step {i+1}', 'reasoning': part}
                            for i, part in enumerate(thinking_parts)
                        ]
                    else:
                        # Single thinking block
                        thinking_layers = [
                            {'number': 1, 'name': 'Chain of Thought Reasoning', 'reasoning': thinking}
                        ]
            else:
                thinking_layers = []
        else:
            # Standard LLM call with context
            if context_parts:
                enhanced_conversation = conversation[:-1] + [{"role": "user", "content": full_context}]
                answer = LLMService.call_llm(enhanced_conversation)
            else:
                answer = LLMService.call_llm(conversation)
        
        # Add assistant response
        storage.add_message(session_id, "assistant", answer)

        return jsonify({
            "answer": answer,
            "thinking_layers": thinking_layers if use_thinking else None,
            "search_results": search_results if (use_web_search or use_research) and search_results else None,
            "retrieved_docs": retrieved_docs if (use_rag and retrieved_docs) else None,
            "capabilities": {
                "rag": use_rag and rag_available,
                "web_search": use_web_search,
                "research": use_research,
                "thinking": use_thinking
            },
            "rag_enhanced": use_rag and rag_available and len(retrieved_docs) > 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_chat_history():
    """Clear conversation history for a session"""
    session_id = get_session_id()
    storage.clear_conversation(session_id)
    return jsonify({"status": "cleared"})

@chat_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get chat analytics and statistics"""
    try:
        from datetime import datetime, timedelta
        import time
        
        # Get all conversations
        all_conversations = storage._memory_storage.get('conversations', {})
        
        # Count total queries
        total_queries = 0
        today_queries = 0
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        
        for session_id, messages in all_conversations.items():
            user_messages = [m for m in messages if m.get('role') == 'user']
            total_queries += len(user_messages)
            
            # Count today's queries (approximate - using message count)
            if len(user_messages) > 0:
                today_queries += len(user_messages)  # Simplified - would need timestamps
        
        return jsonify({
            "total_queries": total_queries,
            "today_queries": today_queries,
            "active_sessions": len(all_conversations),
            "last_activity": time.time()  # Current timestamp
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get chat history organized by session"""
    try:
        all_conversations = storage._memory_storage.get('conversations', {})
        
        sessions = []
        for session_id, messages in all_conversations.items():
            if messages:
                sessions.append({
                    "session_id": session_id,
                    "message_count": len(messages),
                    "last_message": messages[-1].get('content', '')[:100] if messages else '',
                    "created": session_id.split('_')[1] if '_' in session_id else 'unknown'
                })
        
        # Sort by creation time (newest first)
        sessions.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            "sessions": sessions,
            "count": len(sessions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

