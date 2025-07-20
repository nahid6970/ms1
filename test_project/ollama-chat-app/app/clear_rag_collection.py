# filename: clear_rag_collection.py
from rag_system import NomicRAGSystem

def clear_and_rebuild_collection():
    """Clear the existing collection and rebuild with new model dimensions"""
    print("Clearing existing RAG collection...")
    
    # Initialize RAG system
    rag = NomicRAGSystem()
    
    # Clear the collection completely
    rag.clear_collection()
    print("✅ Collection cleared successfully!")
    
    # Add some test documents to verify it works
    test_docs = [
        {
            "content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
            "metadata": {"topic": "programming", "language": "python", "source": "test"}
        },
        {
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from and make predictions on data. Popular frameworks include TensorFlow, PyTorch, and scikit-learn.",
            "metadata": {"topic": "machine_learning", "category": "AI", "source": "test"}
        }
    ]
    
    print("Adding test documents...")
    for i, doc in enumerate(test_docs, 1):
        chunk_ids = rag.add_document(doc["content"], doc["metadata"])
        print(f"✅ Added test document {i} with {len(chunk_ids)} chunks")
    
    # Test search
    print("\nTesting search functionality...")
    results = rag.search("Python programming", n_results=2)
    
    if results:
        print(f"✅ Search working! Found {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Distance: {result['distance']:.4f}")
            print(f"     Content: {result['content'][:100]}...")
    else:
        print("❌ Search returned no results")
    
    print("\n🎉 RAG collection rebuilt successfully with Nomic embeddings!")
    print("You can now add your documents via the RAG interface at:")
    print("http://localhost:8000/rag_interface.html")

if __name__ == "__main__":
    clear_and_rebuild_collection()