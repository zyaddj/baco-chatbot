# ingest.py (project root)
# This script converts PDF documents into searchable vector embeddings
# Think of it as creating an "index" that makes PDFs searchable by meaning, not just keywords

import os
from dotenv import load_dotenv  # Loads environment variables from .env file
from pypdf import PdfReader    # Library to read PDF files and extract text

# LangChain imports - these help us work with AI/LLM tools easily
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Breaks text into chunks
from langchain_community.vectorstores import FAISS       # Vector database to store embeddings
from langchain_openai import OpenAIEmbeddings  # Converts text to numerical vectors

# 1) Load OpenAI API key from .env file
# This is crucial - without the API key, we can't create embeddings
load_dotenv()  # Reads the .env file and loads variables into environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Gets the API key from environment
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env file")  # Stops if no key found

# 2) Read all PDF files and extract text with section context
def read_pdfs_with_context(folder: str) -> list[tuple[str, str, int]]:
    """
    Reads all PDF files in a folder and extracts their text content with page tracking
    Returns: List of tuples (filename, page_text, page_number)
    """
    docs = []  # Will store (filename, page_text, page_number) tuples
    
    # Loop through every file in the data folder
    for fname in os.listdir(folder):
        if fname.lower().endswith(".pdf"):  # Only process PDF files
            path = os.path.join(folder, fname)  # Get full file path
            reader = PdfReader(path)  # Create PDF reader object
            
            # Extract text from each page separately and track page numbers
            for page_num, page in enumerate(reader.pages, start=1):  # Start counting from 1
                extracted_text = page.extract_text() or ""  # Get text, or empty string if none
                if extracted_text.strip():  # Only add pages that have actual text
                    docs.append((fname, extracted_text, page_num))  # Store filename, text, and page number
    
    return docs

# 3) Break large text into chunks while capturing section context
def chunk_text_with_context(source_name: str, text: str, page_num: int, chunk_chars: int = 1200, overlap: int = 200):
    """
    Splits long text into smaller chunks while identifying section headings and context
    - chunk_chars: Maximum characters per chunk (about 200-300 words)
    - overlap: Characters to overlap between chunks (prevents cutting sentences)
    - page_num: The page number this text came from
    """
    # Find potential section headings (common patterns in PDFs)
    import re
    
    # Look for section headings - these patterns catch most document structures
    section_patterns = [
        r'^[A-Z][A-Z\s&-]{10,}$',           # ALL CAPS headings like "DRESS CODE POLICY"
        r'^\d+\.\s+[A-Z][A-Za-z\s&-]{5,}',  # Numbered sections like "1. Introduction"
        r'^[A-Z][a-zA-Z\s&-]{8,}:',         # Headings with colons like "Work Hours:"
        r'^[A-Z][a-z]+\s+[A-Z][a-z\s&-]+$', # Title case like "Remote Work Policy"
    ]
    
    # Find the most relevant section heading for this text
    current_section = "General Information"  # Default section name
    lines = text.split('\n')
    
    for line in lines[:10]:  # Check first 10 lines for section headings
        line = line.strip()
        if len(line) > 5:  # Skip very short lines
            for pattern in section_patterns:
                if re.match(pattern, line):
                    current_section = line[:50]  # Limit section name length
                    break
            if current_section != "General Information":
                break
    
    # RecursiveCharacterTextSplitter is smart - it tries to split at sentences, then paragraphs
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_chars, chunk_overlap=overlap)
    chunks = splitter.split_text(text)  # Split the text into chunks
    
    # Create metadata for each chunk including section context
    metadatas = []
    for i, chunk in enumerate(chunks):
        # Try to find a more specific section within this chunk
        chunk_section = current_section
        chunk_lines = chunk.split('\n')
        
        for line in chunk_lines[:5]:  # Check first few lines of chunk
            line = line.strip()
            if len(line) > 5:
                for pattern in section_patterns:
                    if re.match(pattern, line):
                        chunk_section = line[:50]
                        break
                if chunk_section != current_section:
                    break
        
        # Create rich metadata with location context
        metadata = {
            "source": source_name,
            "page": page_num,
            "section": chunk_section,
            "chunk": i,
            "location": f"{source_name} - {chunk_section} (p. {page_num})"
        }
        metadatas.append(metadata)
    
    return chunks, metadatas

def main():
    # Step 1: Read all PDFs from data folder with context tracking
    pdfs_with_context = read_pdfs_with_context("data")
    if not pdfs_with_context:
        raise RuntimeError("No PDFs found in ./data. Add files like handbook.pdf, policies.pdf")

    # Step 2: Set up OpenAI embeddings
    # Embeddings convert text into numerical vectors that capture meaning
    # "text-embedding-3-small" is OpenAI's efficient embedding model
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"  # Cheaper than ada-002, still very good
    )

    # Step 3: Process all PDF pages and collect chunks with section context
    all_texts = []  # Will store all text chunks from all PDFs
    all_meta  = []  # Will store metadata for each chunk including section info

    # Process each PDF page separately to maintain context tracking
    for fname, page_text, page_num in pdfs_with_context:
        print(f"Processing {fname}, page {page_num}...")  # Show progress with page numbers
        chunks, meta = chunk_text_with_context(fname, page_text, page_num)  # Break into chunks with context
        all_texts.extend(chunks)  # Add chunks to master list
        all_meta.extend(meta)     # Add metadata with section context to master list

    print(f"Ingesting {len(all_texts)} chunks from {len(set(fname for fname, _, _ in pdfs_with_context))} PDFs...")

    # Step 4: Create vector database
    # This is the magic - converts all text chunks into searchable vectors
    # FAISS is a fast similarity search library created by Facebook
    vs = FAISS.from_texts(all_texts, embedding=embeddings, metadatas=all_meta)

    # Step 5: Save the vector database to disk
    # This creates a folder called "faiss_index" with the searchable database
    vs.save_local("faiss_index")
    print("✅ Done. FAISS index saved to ./faiss_index")
    print("Your PDFs are now searchable with section context tracking! Run the chatbot app next.")

if __name__ == "__main__":
    main()  # Run the ingestion process
