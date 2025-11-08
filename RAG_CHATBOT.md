# Complete RAG Chatbot System

## Overview

The chatbot is now a **complete RAG (Retrieval-Augmented Generation) system** powered by LangChain and LangGraph. All chat modes are enhanced with knowledge base capabilities when documents are available.

## RAG-Enhanced Chat Modes

### 1. 💬 Normal Chat (RAG-Enhanced)
- **Default behavior**: Standard conversation
- **RAG Enhancement**: Automatically uses knowledge base when available
- **How it works**: 
  - Searches knowledge base for relevant context
  - Enhances LLM prompt with retrieved documents
  - Shows retrieved documents in response
- **Best for**: General questions with optional knowledge base support

### 2. 🧠 Thinking Mode (RAG-Enhanced)
- **Default behavior**: Multi-layer deep reasoning (4 layers)
- **RAG Enhancement**: Reasoning layers include knowledge base context
- **How it works**:
  - Retrieves relevant documents from knowledge base
  - Enhances each reasoning layer with document context
  - Shows both reasoning process and source documents
- **Best for**: Complex questions requiring deep analysis

### 3. 🔍 Research Mode
- **Default behavior**: Web search + AI synthesis
- **RAG Enhancement**: Can combine web search with knowledge base
- **How it works**:
  - Searches web using DuckDuckGo
  - Optionally searches knowledge base
  - Synthesizes both sources
- **Best for**: Questions requiring current information

### 4. 📚 Full RAG Mode
- **Default behavior**: Pure RAG-powered answers
- **How it works**:
  - Uses LangGraph workflow
  - Retrieves relevant documents
  - Generates answer based primarily on knowledge base
  - Falls back to general knowledge if needed
- **Best for**: Questions about your uploaded documents

## How RAG Enhancement Works

### Automatic Enhancement
When documents are in the knowledge base:
1. **Query Analysis**: System analyzes your question
2. **Document Retrieval**: Searches knowledge base for relevant chunks
3. **Context Injection**: Adds retrieved context to LLM prompt
4. **Enhanced Answer**: LLM generates answer using both general knowledge and your documents
5. **Source Display**: Shows which documents were used

### LangGraph Workflow (Full RAG Mode)

```
User Question
    ↓
[Retrieve Node] → Search knowledge base
    ↓
[Generate Node] → LLM with context
    ↓
Final Answer + Retrieved Docs
```

## Setting Up Your Knowledge Base

### Method 1: Upload Documents
```bash
POST /api/rag/upload
Content-Type: multipart/form-data
Body: file (PDF, TXT, DOCX, MD)
```

### Method 2: Add Text Directly
```bash
POST /api/rag/add-text
Content-Type: application/json
Body: {
  "text": "Your document content",
  "title": "Document Title"
}
```

### Supported Formats
- **PDF**: `.pdf` files
- **Text**: `.txt`, `.md` files
- **Word**: `.docx` files

## Technical Architecture

### Components

1. **RAG Service** (`app/services/rag_service.py`)
   - FAISS vector store
   - HuggingFace embeddings
   - Document processing
   - Semantic search

2. **LangGraph Service** (`app/services/langgraph_service.py`)
   - Workflow orchestration
   - State management
   - Retrieve → Generate pipeline

3. **Chat Routes** (`app/routes/chat.py`)
   - RAG-aware chat handling
   - Automatic enhancement
   - Mode-specific processing

### Data Flow

```
User Question
    ↓
Check RAG Availability
    ↓
[If Available] → Search Knowledge Base
    ↓
Retrieve Relevant Chunks
    ↓
Enhance LLM Prompt
    ↓
Generate Answer
    ↓
Return Answer + Sources
```

## Features

✅ **Automatic RAG Enhancement**: All modes use knowledge base when available  
✅ **Smart Fallback**: Works without documents (standard chat)  
✅ **Source Attribution**: Shows which documents were used  
✅ **Persistent Storage**: Documents saved in FAISS vector store  
✅ **Free & Local**: No external services for embeddings  
✅ **LangGraph Workflow**: Advanced orchestration for RAG pipeline  

## Usage Examples

### Example 1: Normal Chat with RAG
1. Upload a document about "Python programming"
2. Select "Normal Chat" mode
3. Ask: "What is a decorator in Python?"
4. System automatically:
   - Searches your document
   - Enhances answer with document content
   - Shows source document

### Example 2: Thinking Mode with RAG
1. Upload technical documentation
2. Select "Thinking Mode"
3. Ask: "How does this system work?"
4. System shows:
   - 4-layer reasoning process
   - Each layer enhanced with document context
   - Source documents

### Example 3: Full RAG Mode
1. Upload multiple documents
2. Select "Full RAG Mode"
3. Ask questions about your documents
4. System:
   - Uses LangGraph workflow
   - Retrieves relevant chunks
   - Generates answer from your documents
   - Shows all sources

## Status Indicator

The UI shows "📚 KB Ready" when:
- RAG system is initialized
- Documents are in knowledge base
- System is ready for RAG-enhanced answers

## Best Practices

1. **Upload Relevant Documents**: Add documents related to topics you'll ask about
2. **Use Appropriate Mode**: 
   - Normal: General questions
   - Thinking: Complex analysis
   - Research: Current events
   - RAG: Document-specific questions
3. **Check Status**: Verify knowledge base is ready before asking document-specific questions
4. **Combine Sources**: Research mode can combine web + knowledge base

## Free & Open Source

- ✅ FAISS: Free vector database
- ✅ HuggingFace: Free embeddings
- ✅ LangChain: Open source
- ✅ LangGraph: Open source
- ✅ No API keys needed for embeddings
- ✅ All processing local

Your chatbot is now a complete RAG system! 🚀

