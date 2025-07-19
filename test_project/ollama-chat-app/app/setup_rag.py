# filename: setup_rag.py
import subprocess
import sys
import os

def install_requirements():
    """Install required packages for RAG system"""
    print("Installing RAG system requirements...")
    
    requirements = [
        "sentence-transformers",
        "chromadb",
        "numpy",
        "faiss-cpu"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            return False
    
    return True

def test_rag_system():
    """Test if RAG system can be imported and initialized"""
    print("\nTesting RAG system...")
    
    try:
        from rag_system import NomicRAGSystem
        rag = NomicRAGSystem()
        print("✓ RAG system initialized successfully")
        
        # Test with a simple document
        test_content = "This is a test document for the RAG system."
        chunk_ids = rag.add_document(test_content, {"test": True})
        print(f"✓ Test document added with {len(chunk_ids)} chunks")
        
        # Test search
        results = rag.search("test document", n_results=1)
        if results:
            print("✓ Search functionality working")
        else:
            print("⚠ Search returned no results")
        
        # Clean up
        rag.clear_collection()
        print("✓ Test completed and cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG system test failed: {e}")
        return False

def main():
    print("RAG System Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Installation failed. Please check the errors above.")
        return
    
    # Test the system
    if test_rag_system():
        print("\n✅ RAG system setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python server.py")
        print("2. Open: http://localhost:8000 for the main chat interface")
        print("3. Open: http://localhost:8000/rag_interface.html for RAG management")
        print("\nThe RAG system will automatically enhance your chat responses with relevant context.")
    else:
        print("\n❌ Setup completed but RAG system test failed.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()