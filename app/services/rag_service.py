"""RAG (Retrieval-Augmented Generation) Service using LangChain and LangGraph"""
import os
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.config import Config

# Global RAG service instance
rag_service = None

class RAGService:
    """RAG Service for document processing and retrieval"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.retriever = None
        self.qa_chain = None
        self._initialize_embeddings()
        self._load_vectorstore()
    
    def _initialize_embeddings(self):
        """Initialize embeddings model (using free HuggingFace models)"""
        try:
            # Use free sentence-transformers model
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
            self.embeddings = None
    
    def _load_vectorstore(self):
        """Load existing vectorstore or create new one"""
        vectorstore_path = "data/vectorstore"
        try:
            if os.path.exists(vectorstore_path) and os.path.exists(f"{vectorstore_path}/index.faiss"):
                self.vectorstore = FAISS.load_local(
                    vectorstore_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
                print("✅ Loaded existing vectorstore")
            else:
                # Create empty vectorstore
                self.vectorstore = None
                self.retriever = None
                print("📝 No existing vectorstore found. Will create new one when documents are added.")
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
            self.vectorstore = None
            self.retriever = None
    
    def _save_vectorstore(self):
        """Save vectorstore to disk"""
        if self.vectorstore:
            vectorstore_path = "data/vectorstore"
            os.makedirs(vectorstore_path, exist_ok=True)
            try:
                self.vectorstore.save_local(vectorstore_path)
                print("✅ Vectorstore saved")
            except Exception as e:
                print(f"Error saving vectorstore: {e}")
    
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Add documents to the vectorstore"""
        if not self.embeddings:
            return False
        
        try:
            # Create documents
            documents = []
            for i, text in enumerate(texts):
                doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
                documents.append(Document(page_content=text, metadata=doc_metadata))
            
            # Split documents
            split_docs = self.text_splitter.split_documents(documents)
            
            # Create or update vectorstore
            if self.vectorstore:
                # Add to existing vectorstore
                self.vectorstore.add_documents(split_docs)
            else:
                # Create new vectorstore
                self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
            
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
            self._save_vectorstore()
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def add_text_file(self, file_path: str) -> bool:
        """Add a text file to the vectorstore"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.add_documents([content], [{"source": file_path, "type": "text_file"}])
        except Exception as e:
            print(f"Error adding text file: {e}")
            return False
    
    def search(self, query: str, k: int = 4) -> List[Dict]:
        """Search for relevant documents"""
        if not self.retriever:
            return []
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
                    "score": 1.0  # FAISS doesn't return scores by default
                })
            return results[:k]
        except Exception as e:
            print(f"Error searching: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_retriever(self):
        """Get the retriever for use in chains"""
        return self.retriever
    
    def is_ready(self) -> bool:
        """Check if RAG system is ready"""
        return self.retriever is not None and self.embeddings is not None
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vectorstore"""
        if self.vectorstore is None:
            return 0
        try:
            # FAISS vectorstore has a method to get document count
            # We can use the index size or search with a dummy query
            # The most reliable way is to check the index directly
            if hasattr(self.vectorstore, 'index'):
                return self.vectorstore.index.ntotal
            # Fallback: try to get from retriever
            if self.retriever:
                # Search with empty query to get all (not ideal but works)
                try:
                    docs = self.retriever.get_relevant_documents("")
                    return len(docs) if docs else 0
                except:
                    return 0
            return 0
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0

