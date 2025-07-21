#!/usr/bin/env python3
"""
Test script for RAG system with Ollama
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_rag_system():
    print("Testing RAG System with Ollama...")
    
    # Test 1: Add a sample document
    print("\n1. Adding a sample document...")
    sample_content = """
    Python is a high-level programming language known for its simplicity and readability.
    It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
    Python is widely used in web development, data science, artificial intelligence, and automation.
    The language was created by Guido van Rossum and first released in 1991.
    """
    
    # Create a temporary file
    with open("sample_doc.txt", "w") as f:
        f.write(sample_content)
    
    add_response = requests.post(f"{BASE_URL}/api/rag/add_file", 
        json={
            "file_path": "sample_doc.txt",
            "metadata": {
                "category": "programming",
                "topic": "python"
            }
        })
    
    if add_response.status_code == 200:
        result = add_response.json()
        print(f"✓ Document added successfully! Created {result['chunks_created']} chunks")
    else:
        print(f"✗ Failed to add document: {add_response.status_code} - {add_response.text}")
        return
    
    # Test 2: Search for similar content
    print("\n2. Searching for content...")
    search_response = requests.post(f"{BASE_URL}/api/rag/search",
        json={
            "query": "What is Python programming language?",
            "n_results": 3
        })
    
    if search_response.status_code == 200:
        results = search_response.json()['results']
        print(f"✓ Found {len(results)} results:")
        for i, result in enumerate(results):
            print(f"  Result {i+1}: Similarity: {result['similarity']:.3f}")
            print(f"    Content: {result['content'][:100]}...")
    else:
        print(f"✗ Search failed: {search_response.status_code} - {search_response.text}")
    
    # Test 3: List documents
    print("\n3. Listing documents...")
    docs_response = requests.get(f"{BASE_URL}/api/rag/documents")
    
    if docs_response.status_code == 200:
        documents = docs_response.json()['documents']
        print(f"✓ Found {len(documents)} documents in collection")
        for doc in documents:
            print(f"  - {doc['filename']}: {doc['chunk_count']} chunks")
    else:
        print(f"✗ Failed to list documents: {docs_response.status_code}")
    
    print("\n✓ RAG system test completed!")

if __name__ == "__main__":
    print("Make sure the server is running on port 8000...")
    print("Starting test in 3 seconds...")
    time.sleep(3)
    test_rag_system()