# app_flexible.py
# Flexible chatbot that can switch between different data sources
# Run with: streamlit run app_flexible.py -- --vector_path test_vectors

import streamlit as st
import os
import argparse
import sys
from dotenv import load_dotenv
import hashlib

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key not found. Please check your environment variables.")
    st.stop()

# Parse command line arguments
def get_vector_path():
    """Get vector path from command line or use default"""
    # Check if running with streamlit
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument("--vector_path", default="faiss_index", help="Path to vector database")
        
        # Handle streamlit's -- separator
        try:
            if "--" in sys.argv:
                idx = sys.argv.index("--")
                args = parser.parse_args(sys.argv[idx+1:])
            else:
                args = parser.parse_args()
            return args.vector_path
        except:
            return "faiss_index"  # Default fallback
    return "faiss_index"

# Simple authentication
VALID_USERS = {
    "test": "test123"
}

def hash_password(password):
    """Simple password hashing for basic security"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Authentication function with session state"""
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    
    if st.session_state.authenticated:
        return True
    
    st.title("🔐 Baco Handbook Assistant - Login")
    st.markdown("Please enter your credentials to access the company handbook assistant.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.login_attempts = 0
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                st.error("❌ Invalid username or password")
                
                if st.session_state.login_attempts >= 3:
                    st.error("🚨 Too many failed attempts. Please contact administrator.")
    
    return False

@st.cache_resource
def load_vector_database(vector_path):
    """Load the FAISS vector database from specified path"""
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        if not os.path.exists(vector_path):
            st.error(f"❌ Vector database not found at: {vector_path}")
            st.error("Available options:")
            st.error("- Original data: faiss_index")
            st.error("- Test data: test_vectors") 
            return None
        
        db = FAISS.load_local(vector_path, embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        st.error(f"❌ Could not load vector database: {e}")
        return None

def ask_question(query, db):
    """Process user question and return AI answer with sources"""
    try:
        docs = db.similarity_search(query, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
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
            "- If you can give an answer but it's not completely clear, express appropriate uncertainty\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Provide a well-formatted answer with brief summary first, then details:"
        )
        
        answer = llm.invoke(prompt)
        sources = list({ (d.metadata or {}).get('source', 'unknown') for d in docs })
        
        return answer.content if hasattr(answer, 'content') else str(answer), sources
        
    except Exception as e:
        return f"❌ Error processing question: {e}", []

def main_app():
    """Main chatbot interface"""
    
    # Get vector path
    vector_path = get_vector_path()
    
    # App header with logout and data source indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title("📘 Baco Handbook Assistant")
    with col2:
        data_source = "Original" if vector_path == "faiss_index" else "Test Data"
        st.info(f"📊 Source: {data_source}")
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("Ask me anything about company policies, procedures, and guidelines!")
    
    # Data source switcher
    with st.expander("🔄 Switch Data Source"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 Use Original Data"):
                st.info("Restart app with: streamlit run app_flexible.py")
        with col2:
            if st.button("🧪 Use Test Data"):
                st.info("Restart app with: streamlit run app_flexible.py -- --vector_path test_vectors")
    
    # Load vector database
    db = load_vector_database(vector_path)
    if not db:
        st.stop()
    
    # Chat interface
    question = st.text_input(
        "Ask a question about policies",
        placeholder="e.g., What is the dress code?"
    )
    
    if st.button("Ask", type="primary") and question.strip():
        
        with st.spinner("🔍 Searching through company documents..."):
            answer, sources = ask_question(question, db)
            
        st.markdown("### 💬 Answer")
        st.markdown(answer)
        
        if sources:
            st.markdown("### 📄 Sources")
            source_text = ", ".join(sources)
            st.caption(f"Information retrieved from: {source_text}")
    
    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ How it works")
        st.write("""
        1. Type your question in the text box
        2. Click 'Ask' to search company documents
        3. Get AI-powered answers with source citations
        
        **Example questions:**
        - What is the dress code policy?
        - How many vacation days do I get?
        - What are the safety procedures?
        - When are the office hours?
        """)
        
        st.header("📊 System Status")
        st.success("✅ Vector Database: Loaded")
        st.success("✅ AI Assistant: Ready")
        st.info(f"📄 Data source: {vector_path}")

def main():
    """Main application entry point"""
    
    st.set_page_config(
        page_title="Baco Handbook Assistant",
        page_icon="📘",
        layout="wide"
    )
    
    if check_password():
        main_app()

if __name__ == "__main__":
    main()