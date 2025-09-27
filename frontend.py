# frontend.py (project root)
# This is your chatbot's user interface - a simple, clean web app for asking questions
# Think of it as the "face" of your chatbot that employees will interact with

import streamlit as st  # Creates beautiful web apps with just Python code
import requests         # Makes HTTP requests to communicate with your backend API

# Configure the web page appearance and metadata
st.set_page_config(
    page_title="Baco Handbook Assistant",  # Shows in browser tab
    page_icon="📘"                         # Icon in browser tab
)

# Create the main heading for your chatbot interface
st.title("📘 Baco Handbook Assistant (MVP)")
st.write("Ask me anything about company policies, procedures, and guidelines!")

# Create an input box where users can type their questions
# st.text_input creates a single-line text field
q = st.text_input(
    "Ask a question about policies",        # Label shown above input box
    placeholder="e.g., What is the dress code?"  # Hint text inside the box
)

# Create a button that triggers the question-answering process
# The condition checks: button clicked AND question is not empty
if st.button("Ask") and q.strip():
    
    # Show a loading spinner while processing the question
    with st.spinner("Searching through company documents..."):
        
        try:
            # Send the user's question to your backend API
            # This makes an HTTP POST request to the /ask endpoint
            resp = requests.post(
                "http://127.0.0.1:8000/ask",    # Your backend server URL
                json={"query": q}               # Send question in JSON format
            )
            
            # Check if the request was successful (no HTTP errors)
            resp.raise_for_status()  # Raises exception if status code indicates error
            
            # Parse the JSON response from your backend
            data = resp.json()  # Converts JSON response to Python dictionary
            
            # Display the AI-generated answer
            st.markdown("**Answer:**")  # Bold heading using markdown
            answer = data.get("answer", "No answer")  # Get answer or default text
            st.write(answer)  # Display the answer text
            
            # Display source information (which PDFs were used)
            sources = data.get("sources") or []  # Get sources list, or empty list if none
            
            if sources:  # Only show sources if there are any
                # Create a smaller, grayed-out text showing source documents
                source_text = ", ".join(sources)  # Join multiple sources with commas
                st.caption(f"📄 Sources: {source_text}")  # Display as caption text
            
        except requests.exceptions.RequestException as e:
            # Handle network/connection errors (backend not running, etc.)
            st.error("❌ Could not connect to backend. Make sure it's running!")
            st.error(f"Technical details: {e}")
            
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (400, 500 status codes, etc.)
            st.error("❌ Backend returned an error")
            st.error(f"Technical details: {e}")
            
        except Exception as e:
            # Handle any other unexpected errors
            st.error("❌ Something went wrong")
            st.error(f"Technical details: {e}")

# Add helpful information in the sidebar
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
    
    st.header("📋 Status")
    # Show connection status to help with troubleshooting
    try:
        # Quick health check to see if backend is responding
        health_resp = requests.get("http://127.0.0.1:8000/docs", timeout=2)
        if health_resp.status_code == 200:
            st.success("✅ Backend connected")
        else:
            st.warning("⚠️ Backend issues")
    except:
        st.error("❌ Backend offline")