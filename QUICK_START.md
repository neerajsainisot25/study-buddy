# Quick Start Guide - RAG Chatbot

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the App
```bash
python main.py
```

### 3. Access the App
Open your browser: `http://localhost:5001`

## 📚 Building Your Knowledge Base

### Option 1: Upload a Document
Use the API endpoint:
```bash
curl -X POST http://localhost:5001/api/rag/upload \
  -F "file=@your_document.pdf"
```

Or use a tool like Postman/Insomnia to upload files.

### Option 2: Add Text Directly
```bash
curl -X POST http://localhost:5001/api/rag/add-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document content here...",
    "title": "My Document"
  }'
```

## 💬 Using the Chatbot

### All Modes are RAG-Enhanced!

1. **Normal Chat**: Automatically uses knowledge base when available
2. **Thinking Mode**: Reasoning enhanced with your documents
3. **Research Mode**: Combines web search + knowledge base
4. **Full RAG Mode**: Pure knowledge base-powered answers

### Example Workflow

1. Upload a document about "Machine Learning"
2. Ask: "What is supervised learning?"
3. System automatically:
   - Searches your document
   - Enhances answer with document content
   - Shows source document

## ✅ Status Indicator

Look for "📚 KB Ready" indicator in the chat UI - this shows your knowledge base is active!

## 🎯 Best Practices

- Upload documents related to topics you'll ask about
- Use "Full RAG Mode" for document-specific questions
- Use "Normal Chat" for general questions (auto-enhanced)
- Check status indicator to verify knowledge base is ready

Your RAG chatbot is ready to use! 🎉

