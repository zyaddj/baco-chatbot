#!/usr/bin/env python3
"""
Quick terminal test for the BACO chatbot
Run with: python test_chatbot.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

def load_vector_db():
    """Load the private FAISS vector database"""
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        print(f"📁 Loading FAISS index from: {FAISS_INDEX_PATH}")
        
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}")
            
        db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        print("✅ Vector database loaded successfully!")
        return db
        
    except Exception as e:
        print(f"❌ Error loading vector database: {e}")
        return None

def ask_question(query, db):
    """Process user question and return AI answer with sources"""
    try:
        print(f"\n🔍 Searching for: '{query}'")
        
        # Search for relevant chunks
        docs = db.similarity_search(query, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        
        # Set up LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=500,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create prompt
        prompt = f"""You are a helpful assistant for BACO Realty. Answer the question using ONLY the context provided below.

Context:
{context}

Question: {query}

Provide a clear, helpful answer based only on the context above. If the context doesn't contain relevant information, say so politely.
"""
        
        print("🤖 Generating answer...")
        answer = llm.predict(prompt)
        
        # Extract sources
        sources = list(set([
            doc.metadata.get('source', 'Unknown') 
            for doc in docs 
            if doc.metadata
        ]))
        
        return answer, sources
        
    except Exception as e:
        return f"Error processing question: {e}", []

def main():
    """Main terminal interface"""
    print("🏢 BACO Realty Knowledge Assistant - Terminal Mode")
    print("=" * 50)
    
    # Load database
    db = load_vector_db()
    if not db:
        print("❌ Failed to load database. Exiting.")
        return
    
    # Test with predefined questions or interactive mode
    test_questions = [
        "What is the dress code policy?",
        "What are the office hours?", 
        "What is BACO's vacation policy?",
        "How many sick days do employees get?"
    ]
    
    print("\n🧪 Running test questions:")
    print("-" * 30)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        answer, sources = ask_question(question, db)
        
        print(f"\n🤖 Answer:")
        print(answer)
        
        if sources:
            print(f"\n📚 Sources: {', '.join(sources)}")
        
        print("-" * 50)
    
    # Interactive mode
    print("\n🎯 Interactive mode - Type your questions (or 'quit' to exit):")
    while True:
        try:
            user_question = input("\n❓ Your question: ").strip()
            
            if user_question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_question:
                continue
                
            answer, sources = ask_question(user_question, db)
            
            print(f"\n🤖 Answer:")
            print(answer)
            
            if sources:
                print(f"\n📚 Sources: {', '.join(sources)}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()