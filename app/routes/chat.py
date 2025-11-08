"""Chat routes blueprint"""
from flask import Blueprint, request, jsonify
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

@chat_bp.route('', methods=['POST'])
def handle_chat():
    """Handle chat queries with different modes: normal, thinking, research, rag"""
    ensure_rag_initialized()
    
    data = request.json or {}
    query = data.get('question', '').strip()
    session_id = data.get('session_id', 'default')
    mode = data.get('mode', 'normal')  # 'normal', 'thinking', 'research', 'rag'

    if not query:
        return jsonify({"error": "No question provided"}), 400

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
        
        # Handle different modes
        if mode == 'rag':
            # RAG mode: Use LangGraph workflow with document retrieval
            if langgraph_service and rag_available:
                result = langgraph_service.process_query(query, conversation[:-1])
                answer = result.get("answer", "")
                retrieved_docs = result.get("retrieved_docs", [])
            else:
                answer = "RAG system not available. Please add documents to the knowledge base first using the document upload feature."
        
        elif mode == 'research':
            # Research mode: Search web + optionally knowledge base, then synthesize
            search_results = WebSearchService.search(query, max_results=5)
            
            # Also check knowledge base if available
            kb_docs = []
            if rag_available:
                kb_docs = rag_service.search(query, k=3)
            
            # Build context with search results and knowledge base
            context = f"User question: {query}\n\n"
            
            # Add knowledge base context if available
            if kb_docs:
                context += "Relevant information from knowledge base:\n"
                for i, doc in enumerate(kb_docs, 1):
                    source = doc.get('metadata', {}).get('source', 'Knowledge Base')
                    context += f"{i}. [KB] {source}: {doc['content'][:300]}...\n\n"
                retrieved_docs = kb_docs
            
            # Add web search results
            if search_results:
                context += "Relevant web search results:\n"
                for i, result in enumerate(search_results, 1):
                    context += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n\n"
            
            if not search_results and not kb_docs:
                context += "No specific search results found. Answer based on your knowledge.\n"
            else:
                context += "Based on the above information (from knowledge base and web search), provide a comprehensive answer. Cite sources when relevant.\n"
            
            # Create research conversation
            research_conversation = conversation[:-1] + [{"role": "user", "content": context}]
            answer = LLMService.call_llm(research_conversation)
            
        elif mode == 'thinking':
            # Thinking mode: Multi-layer deep reasoning (with optional RAG enhancement)
            if rag_available:
                # Enhance thinking with RAG context
                rag_docs = rag_service.search(query, k=3)
                if rag_docs:
                    context = "\n\n".join([f"Reference: {doc['content'][:300]}" for doc in rag_docs])
                    enhanced_query = f"{query}\n\nRelevant context from knowledge base:\n{context}"
                    reasoning_result = ReasoningService.deep_reasoning(enhanced_query, conversation[:-1])
                else:
                    reasoning_result = ReasoningService.deep_reasoning(query, conversation[:-1])
            else:
                reasoning_result = ReasoningService.deep_reasoning(query, conversation[:-1])
            
            answer = reasoning_result['final_answer']
            thinking_layers = reasoning_result['layers']
            
            # Include RAG docs if available
            if rag_available:
                retrieved_docs = rag_service.search(query, k=3)
        
        else:
            # Normal mode: Standard chat (with optional RAG enhancement)
            if rag_available:
                # Try to enhance with RAG context
                rag_docs = rag_service.search(query, k=3)
                if rag_docs:
                    context = "\n\n".join([
                        f"From knowledge base: {doc['content'][:400]}"
                        for doc in rag_docs
                    ])
                    enhanced_conversation = conversation[:-1] + [{
                        "role": "user",
                        "content": f"{query}\n\nRelevant context:\n{context}"
                    }]
                    answer = LLMService.call_llm(enhanced_conversation)
                    retrieved_docs = rag_docs
                else:
                    answer = LLMService.call_llm(conversation)
            else:
                answer = LLMService.call_llm(conversation)
        
        # Add assistant response
        storage.add_message(session_id, "assistant", answer)

        return jsonify({
            "answer": answer,
            "thinking_layers": thinking_layers if mode == 'thinking' else None,
            "search_results": search_results if mode == 'research' else None,
            "retrieved_docs": retrieved_docs if (retrieved_docs and rag_available) else None,
            "mode": mode,
            "rag_enhanced": rag_available and len(retrieved_docs) > 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/clear', methods=['POST'])
def clear_chat_history():
    """Clear conversation history for a session"""
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    storage.clear_conversation(session_id)
    return jsonify({"status": "cleared"})

