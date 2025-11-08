"""LangGraph service for advanced RAG workflows"""
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI
from app.services.rag_service import RAGService
from app.config import Config
import operator

class GraphState(TypedDict):
    """State for the LangGraph workflow"""
    messages: Annotated[List[BaseMessage], operator.add]
    question: str
    context: str
    answer: str

class LangGraphService:
    """Service for LangGraph-based RAG workflows"""
    
    def __init__(self, rag_service_instance):
        self.rag_service = rag_service_instance
        # Use LLMService instead of direct ChatOpenAI for compatibility
        self.llm = None  # Will use LLMService.call_llm instead
        self.workflow = self._create_workflow()
    
    def _retrieve_context(self, state: GraphState) -> GraphState:
        """Retrieve relevant context from RAG system"""
        question = state["question"]
        
        if self.rag_service and self.rag_service.is_ready():
            # Search for relevant documents
            results = self.rag_service.search(question, k=4)
            if results:
                context = "\n\n".join([
                    f"Document {i+1}:\n{result['content']}"
                    for i, result in enumerate(results)
                ])
                state["context"] = context
            else:
                state["context"] = "No relevant documents found in knowledge base."
        else:
            state["context"] = "RAG system not initialized. No documents available."
        
        return state
    
    def _generate_answer(self, state: GraphState) -> GraphState:
        """Generate answer using LLM with context"""
        from app.services.llm_service import LLMService
        
        question = state["question"]
        context = state.get("context", "")
        conversation_history = state.get("messages", [])
        
        # Build prompt with context
        if context and context != "No relevant documents found in knowledge base.":
            prompt = f"""Use the following context from the knowledge base to answer the question.
If the context doesn't contain enough information, use your general knowledge to provide a helpful answer.

Context from knowledge base:
{context}

Question: {question}

Provide a comprehensive answer based on the context and your knowledge:"""
        else:
            prompt = question
        
        # Convert to dict format for LLMService
        messages = []
        for msg in conversation_history:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            answer = LLMService.call_llm(messages)
            state["answer"] = answer
            state["messages"].append(AIMessage(content=answer))
        except Exception as e:
            state["answer"] = f"Error generating answer: {str(e)}"
        
        return state
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_context)
        workflow.add_node("generate", self._generate_answer)
        
        # Set entry point
        workflow.set_entry_point("retrieve")
        
        # Add edges
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # Compile workflow
        return workflow.compile()
    
    def process_query(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        """Process a query through the LangGraph workflow"""
        # Convert conversation history to LangChain messages
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content", "")))
        
        # Initial state
        initial_state: GraphState = {
            "messages": messages,
            "question": question,
            "context": "",
            "answer": ""
        }
        
        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            retrieved_docs = []
            if self.rag_service and self.rag_service.is_ready():
                try:
                    retrieved_docs = self.rag_service.search(question, k=4)
                except Exception as e:
                    print(f"Error retrieving docs: {e}")
            
            return {
                "answer": final_state.get("answer", ""),
                "context": final_state.get("context", ""),
                "retrieved_docs": retrieved_docs
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "context": "",
                "retrieved_docs": []
            }

# Initialize services
rag_service = None
langgraph_service = None

def initialize_rag():
    """Initialize RAG and LangGraph services"""
    global rag_service, langgraph_service
    try:
        rag_service = RAGService()
        langgraph_service = LangGraphService(rag_service)
        return True
    except Exception as e:
        print(f"Error initializing RAG: {e}")
        import traceback
        traceback.print_exc()
        return False

