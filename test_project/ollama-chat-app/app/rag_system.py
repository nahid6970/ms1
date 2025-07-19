# filename: rag_system.py
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import hashlib
import logging
from pathlib import Path

class NomicRAGSystem:
    def __init__(self, 
                 persist_directory: str = "./chroma_db",
                 collection_name: str = "documents",
                 model_name: str = "nomic-ai/nomic-embed-text-v1"):
        """
        Initialize RAG system with Nomic embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.model_name = model_name
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize embedding model
        self.logger.info(f"Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name, trust_remote_code=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            self.logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info(f"Created new collection: {collection_name}")
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def add_document(self, 
                    content: str, 
                    metadata: Dict[str, Any] = None,
                    chunk_size: int = 512) -> List[str]:
        """
        Add document to the vector store
        """
        if metadata is None:
            metadata = {}
        
        # Generate document ID
        doc_id = hashlib.md5(content.encode()).hexdigest()
        
        # Chunk the document
        chunks = self.chunk_text(content, chunk_size)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare data for ChromaDB
        chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        chunk_metadata = []
        
        for i, chunk in enumerate(chunks):
            chunk_meta = metadata.copy()
            chunk_meta.update({
                'doc_id': doc_id,
                'chunk_index': i,
                'chunk_count': len(chunks)
            })
            chunk_metadata.append(chunk_meta)
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata,
            ids=chunk_ids
        )
        
        self.logger.info(f"Added document with {len(chunks)} chunks")
        return chunk_ids
    
    def add_file(self, file_path: str, metadata: Dict[str, Any] = None) -> List[str]:
        """
        Add file content to vector store
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'filename': file_path.name,
            'filepath': str(file_path),
            'file_extension': file_path.suffix
        })
        
        return self.add_document(content, metadata)
    
    def add_directory(self, 
                     directory_path: str, 
                     file_extensions: List[str] = None,
                     recursive: bool = True) -> Dict[str, List[str]]:
        """
        Add all files from directory to vector store
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']
        
        directory_path = Path(directory_path)
        added_files = {}
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    chunk_ids = self.add_file(str(file_path))
                    added_files[str(file_path)] = chunk_ids
                    self.logger.info(f"Added file: {file_path}")
                except Exception as e:
                    self.logger.error(f"Error adding file {file_path}: {e}")
        
        return added_files
    
    def search(self, 
              query: str, 
              n_results: int = 5,
              filter_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'id': results['ids'][0][i]
            })
        
        return formatted_results
    
    def get_context(self, 
                   query: str, 
                   n_results: int = 3,
                   max_context_length: int = 2000) -> str:
        """
        Get relevant context for RAG
        """
        results = self.search(query, n_results)
        
        context_parts = []
        total_length = 0
        
        for result in results:
            content = result['content']
            if total_length + len(content) <= max_context_length:
                context_parts.append(content)
                total_length += len(content)
            else:
                # Add partial content if it fits
                remaining = max_context_length - total_length
                if remaining > 100:  # Only add if meaningful amount remains
                    context_parts.append(content[:remaining] + "...")
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def delete_document(self, doc_id: str):
        """
        Delete document by ID
        """
        # Find all chunks for this document
        results = self.collection.get(where={"doc_id": doc_id})
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            self.logger.info(f"Deleted document: {doc_id}")
        else:
            self.logger.warning(f"Document not found: {doc_id}")
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the collection
        """
        results = self.collection.get()
        
        # Group by document ID
        docs = {}
        for i, metadata in enumerate(results['metadatas']):
            doc_id = metadata.get('doc_id')
            if doc_id not in docs:
                docs[doc_id] = {
                    'doc_id': doc_id,
                    'filename': metadata.get('filename', 'Unknown'),
                    'chunk_count': metadata.get('chunk_count', 0),
                    'metadata': metadata
                }
        
        return list(docs.values())
    
    def clear_collection(self):
        """
        Clear all documents from collection
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.logger.info("Cleared collection")

# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG system
    rag = NomicRAGSystem()
    
    # Add some sample documents
    sample_docs = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "metadata": {"topic": "programming", "language": "python"}
        },
        {
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from and make predictions on data. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.",
            "metadata": {"topic": "machine_learning", "category": "AI"}
        },
        {
            "content": "Web development involves creating websites and web applications. Frontend technologies include HTML, CSS, and JavaScript, while backend technologies include Python, Node.js, and databases.",
            "metadata": {"topic": "web_development", "category": "programming"}
        }
    ]
    
    # Add documents
    for doc in sample_docs:
        rag.add_document(doc["content"], doc["metadata"])
    
    # Test search
    query = "What is Python programming?"
    results = rag.search(query, n_results=2)
    
    print(f"Query: {query}")
    print("Results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Content: {result['content'][:100]}...")
        print(f"   Distance: {result['distance']:.4f}")
        print(f"   Metadata: {result['metadata']}")
        print()
    
    # Test context generation
    context = rag.get_context(query)
    print(f"Generated context:\n{context}")