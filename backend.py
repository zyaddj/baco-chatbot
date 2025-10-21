# backend.py (project root)
# This is the "brain" of your chatbot - it loads the vector database and answers questions
# Think of it as a smart librarian that finds relevant info and gives you answers

import os
from typing import List
from dotenv import load_dotenv  # Loads API keys from .env file
from fastapi import FastAPI     # Creates web API endpoints (like /ask)
from pydantic import BaseModel  # Validates data structure for API requests

# Import LangChain components for AI functionality
from langchain_openai import OpenAIEmbeddings  # Converts questions to vectors for searching
from langchain_community.vectorstores import FAISS  # Loads the searchable vector database
from langchain_openai import ChatOpenAI      # OpenAI's ChatGPT for generating answers

# Load environment variables (especially the OpenAI API key)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env file")  # Stop if no API key

# Get private paths from environment
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")  # Private index path

# Create FastAPI application - this becomes your web server
app = FastAPI(title="Baco MVP Backend")

# 1) Load the vector database that was created by ingest.py
print(f"Loading FAISS vector database from {FAISS_INDEX_PATH}...")  # Show loading progress
embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY,
    model="text-embedding-3-small"  # Same model used in ingestion
)

# Load the saved FAISS index from private location
# allow_dangerous_deserialization=True is required because FAISS uses pickle (security warning)
# This is safe in your environment since you created the index yourself
if not os.path.exists(FAISS_INDEX_PATH):
    raise FileNotFoundError(f"FAISS index not found at {FAISS_INDEX_PATH}. Run ingest.py first.")

db = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
print("✅ Vector database loaded successfully!")

# Define the data structure for incoming questions
class Question(BaseModel):
    """
    Data model for API requests - ensures questions come in the right format
    Example: {"query": "What is the dress code?"}
    """
    query: str  # The user's question as a string

@app.post("/ask")
def ask(q: Question):
    """
    Main API endpoint that answers questions using the RAG (Retrieval Augmented Generation) process:
    1. Convert question to vector
    2. Find similar chunks in vector database  
    3. Send relevant chunks + question to ChatGPT
    4. Return the AI-generated answer with sources
    """
    
    print(f"🔍 Searching for: {q.query}")  # Log the incoming question
    
    # 2) Retrieve the most relevant chunks from vector database
    # similarity_search finds chunks with similar meaning to the question
    # k=4 means "get the top 4 most relevant chunks"
    docs = db.similarity_search(q.query, k=4)
    
    # Combine all retrieved chunks into one context string
    # This gives ChatGPT the relevant information to answer the question
    context = "\n\n".join([d.page_content for d in docs])
    
    # 3) Set up ChatGPT to generate the answer
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",   # Fast and cost-effective model
        temperature=0.1          # Low temperature = more focused, factual answers
    )
    
    # Create a prompt that tells ChatGPT exactly what to do
    # This is crucial - it ensures ChatGPT only uses the provided context
    prompt = (
        "You are a helpful HR assistant. Answer ONLY using the context below. "
        "Structure your response with a brief summary first, then details:\n\n"
        "**Format your response as follows:**\n"
        "1. **Brief Answer:** Start with 1-2 sentences summarizing the key point\n"
        "2. **Details:** Then provide organized details with:\n"
        "   - Use bullet points when listing multiple items\n"
        "   - Organize information logically (e.g., 'What's allowed' vs 'What's not allowed')\n"
        "   - Use clear headings with ** for important sections\n"
        "   - Keep sentences concise and well-structured\n"
        "- If the answer isn't in the context, say you don't know and suggest they refer to the handbook\n"
        "- I need you to assess if you have answered the question explicitly. If you are no able to, express appropriate uncertainty\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {q.query}\n\n"
        "Provide a well-formatted answer with brief summary first, then details:"
    )

    print("Searching through company materials...")  # Show AI processing step

    # Send the prompt to ChatGPT and get the answer
    answer = llm.predict(prompt)
    
    # 4) Extract source information for transparency
    # This tells users which documents the answer came from
    # Using 'set' removes duplicates, then convert back to list
    sources = list({ (d.metadata or {}).get('source', 'unknown') for d in docs })
    
    print(f"✅ Answer sourced from: {sources}")  # Log the sources used
    
    # Return the final response with answer and source documents
    return {
        "answer": answer,      # The AI-generated answer
        "sources": sources     # List of PDF files used to generate the answer
    }

# When you run this file directly, it will show helpful information
if __name__ == "__main__":
    print("🚀 Backend is ready!")
    print("To start the server, run: uvicorn backend:app --reload")
    print("Then visit: http://localhost:8000/docs to test the API")