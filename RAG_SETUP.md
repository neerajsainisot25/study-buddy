# RAG System Setup Guide

## Overview

The app now includes a full RAG (Retrieval-Augmented Generation) system powered by:
- **LangChain**: Document processing and vector store management
- **LangGraph**: Workflow orchestration for RAG pipeline
- **FAISS**: Free, local vector database for embeddings
- **HuggingFace Embeddings**: Free sentence transformers for embeddings

## Features

### 1. Document Upload
- Support for multiple file formats: `.txt`, `.pdf`, `.docx`, `.md`
- Automatic text extraction and chunking
- Vector embedding generation
- Persistent storage in FAISS

### 2. RAG Chat Mode
- Retrieves relevant documents from knowledge base
- Uses LangGraph workflow for orchestration
- Generates context-aware answers
- Shows retrieved documents in UI

### 3. Knowledge Base Management
- Add documents via API
- Add text directly
- Search documents
- Check system status

## API Endpoints

### Document Management

**Upload Document**
```bash
POST /api/rag/upload
Content-Type: multipart/form-data
Body: file (txt, pdf, docx, md)
```

**Add Text Directly**
```bash
POST /api/rag/add-text
Content-Type: application/json
Body: {
  "text": "Your text content here",
  "title": "Document Title"
}
```

**Search Documents**
```bash
POST /api/rag/search
Content-Type: application/json
Body: {
  "query": "search query",
  "k": 4
}
```

**Get Status**
```bash
GET /api/rag/status
```

### Chat with RAG

**RAG Mode Chat**
```bash
POST /api/chat
Content-Type: application/json
Body: {
  "question": "Your question",
  "session_id": "session_123",
  "mode": "rag"
}
```

## How It Works

### LangGraph Workflow

1. **Retrieve Node**: Searches knowledge base for relevant documents
2. **Generate Node**: Uses retrieved context + LLM to generate answer

### Document Processing Pipeline

1. **Load**: Extract text from uploaded file
2. **Split**: Chunk text into manageable pieces (1000 chars, 200 overlap)
3. **Embed**: Generate embeddings using HuggingFace model
4. **Store**: Save to FAISS vector database
5. **Retrieve**: Semantic search for relevant chunks

## Usage Examples

### Adding Documents

**Via File Upload:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/rag/upload', {
    method: 'POST',
    body: formData
});
```

**Via Text:**
```javascript
fetch('/api/rag/add-text', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: "Your document content here",
        title: "My Document"
    })
});
```

### Using RAG Mode

1. Select "📚 RAG Mode (Knowledge Base)" from chat mode dropdown
2. Ask questions about your uploaded documents
3. The system will:
   - Search your knowledge base
   - Retrieve relevant context
   - Generate answer using that context
   - Show retrieved documents in the response

## Storage

- **Vector Store**: `data/vectorstore/` (FAISS files)
- **Uploads**: `data/uploads/` (original files)
- All data is stored locally, no external services required

## Free & Open Source

- ✅ FAISS: Free vector database
- ✅ HuggingFace Embeddings: Free sentence transformers
- ✅ LangChain: Open source framework
- ✅ LangGraph: Open source workflow engine
- ✅ No API keys needed for embeddings
- ✅ All processing happens locally

## Next Steps

1. Upload documents to build your knowledge base
2. Use RAG mode in chat to query your documents
3. Documents persist across sessions
4. Add more documents anytime to expand knowledge base

