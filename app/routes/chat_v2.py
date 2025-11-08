"""New Chat routes with Supabase persistence and SSE streaming"""
from flask import Blueprint, request, jsonify, Response, stream_with_context, render_template_string
from app.services.supabase_service import supabase_service
from app.services.llm_service import LLMService
from app.services.langgraph_service import rag_service
from app.services.web_search import WebSearchService
from app.services.reasoning_service import ReasoningService
import uuid
import re
from datetime import datetime

chat_v2_bp = Blueprint('chat_v2', __name__)

def get_user_id():
    """Get user ID from X-User-Id header"""
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        # For development, allow a default user
        # In production, this should return 401
        user_id = '00000000-0000-0000-0000-000000000000'
    return user_id

@chat_v2_bp.route('/start', methods=['POST'])
def start_chat():
    """Create a new chat conversation"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.json or {}
        else:
            data = request.form.to_dict() or {}
        
        title = data.get('title', 'New Conversation')
        
        conversation = supabase_service.create_conversation(user_id, title)
        
        # Check if request wants HTML (HTMX)
        if request.headers.get('HX-Request'):
            # Return HTML fragment for sidebar
            date_str = ''
            if conversation.get('created_at'):
                try:
                    date = datetime.fromisoformat(conversation['created_at'].replace('Z', '+00:00'))
                    date_str = date.strftime('%m/%d/%Y')
                except:
                    date_str = ''
            html = f'''
            <div class="sidebar-item" data-chat-id="{conversation['id']}" onclick="loadChat('{conversation['id']}')">
                <div class="font-medium truncate">{conversation.get('title', 'New Conversation')}</div>
                <div class="text-xs text-gray-500 mt-1">{date_str}</div>
            </div>
            '''
            return html, 201
        
        return jsonify({
            "id": conversation.get('id'),
            "title": conversation.get('title'),
            "created_at": conversation.get('created_at')
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_v2_bp.route('', methods=['GET'])
def list_chats():
    """List all conversations for the user"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        conversations = supabase_service.get_conversations(user_id)
        
        # Check if request wants HTML (HTMX)
        if request.headers.get('HX-Request'):
            # Return HTML fragment for HTMX
            html = ''
            for chat in conversations:
                date_str = ''
                if chat.get('created_at'):
                    try:
                        date = datetime.fromisoformat(chat['created_at'].replace('Z', '+00:00'))
                        date_str = date.strftime('%m/%d/%Y')
                    except:
                        date_str = ''
                html += f'''
                <div class="sidebar-item" data-chat-id="{chat['id']}" onclick="loadChat('{chat['id']}')">
                    <div class="font-medium truncate">{chat.get('title', 'New Conversation')}</div>
                    <div class="text-xs text-gray-500 mt-1">{date_str}</div>
                </div>
                '''
            return html, 200
        
        return jsonify({
            "conversations": conversations,
            "count": len(conversations)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_v2_bp.route('/<conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """Get all messages for a conversation"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        messages = supabase_service.get_conversation_messages(conversation_id, user_id)
        
        # Check if request wants HTML (HTMX)
        if request.headers.get('HX-Request'):
            # Return HTML fragment for HTMX
            html = ''
            for msg in messages:
                role_class = 'message-user' if msg['role'] == 'user' else 'message-assistant'
                content = msg['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html += f'<div class="{role_class}">{content}</div>'
            return html, 200
        
        return jsonify({
            "messages": messages,
            "count": len(messages)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_v2_bp.route('/<conversation_id>/message', methods=['POST'])
def send_message(conversation_id):
    """Send a message and stream assistant response"""
    user_id = get_user_id()
    
    if not supabase_service.is_available():
        return jsonify({"error": "Supabase not configured"}), 503
    
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get capability flags
        use_rag = data.get('use_rag', True)
        use_web_search = data.get('use_web_search', False)
        use_research = data.get('use_research', False)
        use_thinking = data.get('use_thinking', False)
        
        # Save user message
        supabase_service.save_message(user_id, conversation_id, 'user', user_message)
        
        # Auto-generate title from first message if conversation has no title
        try:
            from app.extensions import supabase
            if supabase.is_available() and supabase.client:
                # Check if conversation exists and has no title
                conv_response = supabase.client.table('conversations').select('title').eq('id', conversation_id).eq('user_id', user_id).limit(1).execute()
                if conv_response.data and (not conv_response.data[0].get('title') or conv_response.data[0].get('title') == 'New Conversation'):
                    # Generate title from first message (first 50 chars)
                    title = user_message[:50] + ('...' if len(user_message) > 50 else '')
                    supabase.client.table('conversations').update({'title': title}).eq('id', conversation_id).eq('user_id', user_id).execute()
        except Exception as e:
            # Title generation is optional, don't fail if it errors
            pass
        
        # Get conversation history
        history = supabase_service.get_conversation_messages(conversation_id, user_id)
        conversation = [
            {"role": msg['role'], "content": msg['content']}
            for msg in history
        ]
        
        # Build context from capabilities
        context_parts = []
        retrieved_docs = []
        search_results = []
        
        # RAG: Retrieve from knowledge base
        if use_rag and rag_service and rag_service.is_ready():
            rag_docs = rag_service.search(user_message, k=4)
            if rag_docs:
                retrieved_docs = rag_docs
                kb_context = "Relevant information from knowledge base:\n"
                for i, doc in enumerate(rag_docs, 1):
                    source = doc.get('metadata', {}).get('source', 'Knowledge Base')
                    kb_context += f"{i}. [KB] {source}: {doc['content'][:400]}...\n\n"
                context_parts.append(kb_context)
        
        # Research: Iterative web search
        if use_research:
            search_results = WebSearchService.iterative_research(user_message, max_iterations=3, results_per_search=5)
            if search_results:
                research_context = "Relevant web search results:\n"
                for i, result in enumerate(search_results, 1):
                    research_context += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n\n"
                context_parts.append(research_context)
        elif use_web_search:
            search_results = WebSearchService.search(user_message, max_results=5)
            if search_results:
                web_context = "Relevant web search results:\n"
                for i, result in enumerate(search_results, 1):
                    web_context += f"{i}. {result['title']}\n   URL: {result['url']}\n   {result['snippet']}\n\n"
                context_parts.append(web_context)
        
        # Build full context
        if context_parts:
            full_context = f"User question: {user_message}\n\n"
            full_context += "\n".join(context_parts)
            full_context += "\nBased on the above information, provide a comprehensive answer. Cite sources when relevant."
        else:
            full_context = user_message
        
        # Prepare messages for LLM
        if context_parts:
            enhanced_conversation = conversation[:-1] + [{"role": "user", "content": full_context}]
        else:
            enhanced_conversation = conversation
        
        # Stream assistant response
        def generate():
            assistant_response = ""
            import json as json_lib
            
            # For thinking mode, use reasoning service
            if use_thinking:
                reasoning_result = ReasoningService.cot_reasoning(
                    full_context if context_parts else user_message,
                    conversation[:-1],
                    use_system_message=True
                )
                assistant_response = reasoning_result['answer']
                # Stream the response character by character for consistency
                for char in assistant_response:
                    yield f"data: {json_lib.dumps({'delta': char})}\n\n"
            else:
                # Stream from LLM
                for chunk in LLMService.stream_llm(enhanced_conversation):
                    assistant_response += chunk
                    yield f"data: {json_lib.dumps({'delta': chunk})}\n\n"
            
            # Save assistant message after streaming completes
            try:
                supabase_service.save_message(user_id, conversation_id, 'assistant', assistant_response)
            except Exception as e:
                # Log error but don't fail the stream
                print(f"Error saving assistant message: {e}")
            
            # Send completion signal
            yield "data: [DONE]\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

