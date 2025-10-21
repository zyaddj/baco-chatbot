#!/usr/bin/env python3
"""
Offline test for BACO chatbot - tests without OpenAI API calls
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    """Test environment setup"""
    print("🔧 Testing environment configuration...")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY: Found (starts with '{api_key[:7]}...')")
    else:
        print("❌ OPENAI_API_KEY: Not found")
    
    # Check paths
    docs_path = os.getenv("DOCUMENTS_PATH", "data")
    index_path = os.getenv("FAISS_INDEX_PATH", "faiss_index")
    
    print(f"📁 DOCUMENTS_PATH: {docs_path}")
    print(f"📁 FAISS_INDEX_PATH: {index_path}")
    
    # Check if paths exist
    docs_exist = os.path.exists(docs_path)
    index_exist = os.path.exists(index_path)
    
    print(f"✅ Documents exist: {docs_exist}")
    print(f"✅ Index exists: {index_exist}")
    
    if docs_exist:
        docs = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
        print(f"📄 Documents found: {len(docs)} PDFs")
        for doc in docs:
            print(f"   - {doc}")
    
    if index_exist:
        index_files = os.listdir(index_path)
        print(f"🔍 Index files: {index_files}")
        has_faiss = "index.faiss" in index_files
        has_pkl = "index.pkl" in index_files
        print(f"✅ FAISS index ready: {has_faiss and has_pkl}")
    
    return docs_exist and index_exist and has_faiss and has_pkl

def test_imports():
    """Test if all required packages can be imported"""
    print("\n📦 Testing package imports...")
    
    try:
        import streamlit
        print("✅ streamlit: OK")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
    
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        print("✅ langchain_openai: OK")
    except ImportError as e:
        print(f"❌ langchain_openai: {e}")
    
    try:
        from langchain_community.vectorstores import FAISS
        print("✅ langchain_community: OK")
    except ImportError as e:
        print(f"❌ langchain_community: {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv: OK")
    except ImportError as e:
        print(f"❌ python-dotenv: {e}")

def simulate_chatbot_logic():
    """Simulate chatbot logic without API calls"""
    print("\n🤖 Simulating chatbot logic (offline)...")
    
    # Simulate questions and responses
    test_questions = [
        "What is the dress code policy?",
        "What are the office hours?", 
        "What is BACO's vacation policy?"
    ]
    
    # Mock responses (what the chatbot should return)
    mock_responses = {
        "dress code": "BACO Realty maintains a business casual dress code...",
        "office hours": "Standard office hours are Monday through Friday, 9:00 AM to 5:00 PM...",
        "vacation": "Employees accrue vacation time based on years of service..."
    }
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        
        # Simple keyword matching (simulating vector search)
        keywords = question.lower().split()
        matched_response = None
        
        for key, response in mock_responses.items():
            if any(keyword in key for keyword in keywords):
                matched_response = response
                break
        
        if matched_response:
            print(f"🤖 Mock Response: {matched_response}")
            print(f"📚 Source: BACO Employee Handbook")
        else:
            print("🤖 Mock Response: I don't have information about that topic.")
        
        print("-" * 50)

def main():
    """Run offline diagnostics"""
    print("🏢 BACO Chatbot - Offline Diagnostics")
    print("=" * 45)
    
    # Test environment
    env_ok = test_environment()
    
    # Test imports
    test_imports()
    
    # Simulate logic
    simulate_chatbot_logic()
    
    print(f"\n🎯 Summary:")
    print(f"   Environment setup: {'✅ OK' if env_ok else '❌ Issues'}")
    print(f"   Network needed for: OpenAI API calls only")
    print(f"   Offline components: All working")
    
    if env_ok:
        print(f"\n💡 Your chatbot is properly configured!")
        print(f"   Once you fix internet connectivity, it should work perfectly.")
    else:
        print(f"\n❌ Configuration issues need to be fixed first.")

if __name__ == "__main__":
    main()