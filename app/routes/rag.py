"""RAG routes for document management"""
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from app.services.langgraph_service import rag_service
if rag_service is None:
    from app.services.rag_service import RAGService
    rag_service = RAGService()

rag_bp = Blueprint('rag', __name__)

UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@rag_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Process file based on type
            success = False
            if filename.endswith('.txt') or filename.endswith('.md'):
                success = rag_service.add_text_file(filepath)
            elif filename.endswith('.pdf'):
                from langchain_community.document_loaders import PyPDFLoader
                loader = PyPDFLoader(filepath)
                documents = loader.load()
                texts = [doc.page_content for doc in documents]
                metadata = [{"source": filename, "type": "pdf"} for _ in texts]
                success = rag_service.add_documents(texts, metadata)
            elif filename.endswith('.docx'):
                from langchain_community.document_loaders import Docx2txtLoader
                loader = Docx2txtLoader(filepath)
                documents = loader.load()
                texts = [doc.page_content for doc in documents]
                metadata = [{"source": filename, "type": "docx"} for _ in texts]
                success = rag_service.add_documents(texts, metadata)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": f"Document '{filename}' added to knowledge base",
                    "filename": filename
                })
            else:
                return jsonify({"error": "Failed to process document"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@rag_bp.route('/add-text', methods=['POST'])
def add_text():
    """Add text directly to knowledge base"""
    data = request.json or {}
    text = data.get('text', '').strip()
    title = data.get('title', 'Manual Entry')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        success = rag_service.add_documents(
            [text],
            [{"source": title, "type": "manual_entry"}]
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Text added to knowledge base"
            })
        else:
            return jsonify({"error": "Failed to add text"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rag_bp.route('/search', methods=['POST'])
def search_documents():
    """Search documents in knowledge base"""
    data = request.json or {}
    query = data.get('query', '').strip()
    k = int(data.get('k', 4))
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        results = rag_service.search(query, k=k)
        return jsonify({
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rag_bp.route('/status', methods=['GET'])
def get_status():
    """Get RAG system status"""
    return jsonify({
        "ready": rag_service.is_ready() if rag_service else False,
        "has_documents": rag_service.vectorstore is not None if rag_service else False
    })

