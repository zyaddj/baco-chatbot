# app.py - Complete chatbot with authentication for deployment
# This combines frontend, backend, and login into one deployable Streamlit app

import streamlit as st
import os
from dotenv import load_dotenv
import hashlib

# LangChain imports for RAG functionality
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ OpenAI API key not found. Please check your environment variables.")
    st.stop()

# Simple authentication - you can modify these credentials
VALID_USERS = {
    "admin": "password123",        # Change this username/password
    "baco": "handbook2024",        # Add more users as needed
    "employee": "welcome123"       # Example additional user
}

def hash_password(password):
    """Simple password hashing for basic security"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Authentication function with session state"""
    
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Show login form
    st.title("🔐 Baco Handbook Assistant - Login")
    st.markdown("Please enter your credentials to access the company handbook assistant.")
    
    # Create login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            # Check credentials
            if username in VALID_USERS and VALID_USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.login_attempts = 0
                st.success("✅ Login successful! Redirecting...")
                st.rerun()  # Refresh to show main app
            else:
                st.session_state.login_attempts += 1
                st.error("❌ Invalid username or password")
                
                # Show attempt counter
                if st.session_state.login_attempts >= 3:
                    st.error("🚨 Too many failed attempts. Please contact administrator.")
                    st.info("**Valid test credentials:** admin / password123")
    
    # Show help information
    st.info("""
    **For Demo/Testing:**
    - Username: `admin`
    - Password: `password123`
    
    **For Production:** Change credentials in the code before deployment.
    """)
    
    return False

@st.cache_resource
def load_vector_database():
    """Load the FAISS vector database (cached for performance)"""
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        # Load the FAISS index
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        st.error(f"❌ Could not load vector database: {e}")
        st.error("Make sure you've run the ingestion script first!")
        return None

def ask_question(query, db):
    """Process user question and return AI answer with sources"""
    try:
        # Search for relevant chunks
        docs = db.similarity_search(query, k=4)
        context = "\n\n".join([d.page_content for d in docs])
        
        # Set up ChatGPT
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        # Enhanced prompt for better formatting
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
        
        # Generate answer
        answer = llm.predict(prompt)
        
        # Extract sources
        sources = list({ (d.metadata or {}).get('source', 'unknown') for d in docs })
        
        return answer, sources
        
    except Exception as e:
        return f"❌ Error processing question: {e}", []

def main_app():
    """Main chatbot interface"""
    
    # App header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📘 Baco Handbook Assistant")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("Ask me anything about company policies, procedures, and guidelines!")
    
    # Load vector database
    db = load_vector_database()
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
            
        # Display answer
        st.markdown("### 💬 Answer")
        st.markdown(answer)
        
        # Display sources
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
        st.info(f"📄 Documents indexed: {len(os.listdir('data')) if os.path.exists('data') else 0} PDFs")

def main():
    """Main application entry point"""
    
    # Page configuration
    st.set_page_config(
        page_title="Baco Handbook Assistant",
        page_icon="📘",
        layout="wide"
    )
    
    # Check authentication
    if check_password():
        main_app()

if __name__ == "__main__":
    main()