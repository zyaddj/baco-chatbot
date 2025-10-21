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

# 1) Load OpenAI API key and private paths from .env file
# This is crucial - without the API key, we can't create embeddings
load_dotenv()  # Reads the .env file and loads variables into environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Gets the API key from environment
DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "data")  # Private documents path
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")  # Private index path

if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env file")  # Stops if no key found

print(f"📁 Using private documents path: {DOCUMENTS_PATH}")
print(f"🔍 Using private index path: {FAISS_INDEX_PATH}")

# 2) Read all PDF files from the ./data folder
def read_pdfs(folder: str) -> list[tuple[str, str]]:
    """
    Reads all PDF files in a folder and extracts their text content
    Returns: List of tuples (filename, full_text_content)
    """
    docs = []  # Will store (filename, text) pairs
    
    # Loop through every file in the data folder
    for fname in os.listdir(folder):
        if fname.lower().endswith(".pdf"):  # Only process PDF files
            path = os.path.join(folder, fname)  # Get full file path
            reader = PdfReader(path)  # Create PDF reader object
            text_parts = []  # Will collect text from all pages
            
            # Extract text from each page in the PDF
            for page in reader.pages:
                extracted_text = page.extract_text() or ""  # Get text, or empty string if none
                text_parts.append(extracted_text)
            
            # Combine all pages into one big text string
            text = "\n".join(text_parts)
            docs.append((fname, text))  # Store filename and full text
    
    return docs

# 3) Break large text into smaller, manageable chunks
def chunk_text(source_name: str, text: str, chunk_chars: int = 1200, overlap: int = 200):
    """
    Splits long text into smaller chunks for better AI processing
    - chunk_chars: Maximum characters per chunk (about 200-300 words)
    - overlap: Characters to overlap between chunks (prevents cutting sentences)
    """
    # RecursiveCharacterTextSplitter is smart - it tries to split at sentences, then paragraphs
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_chars, chunk_overlap=overlap)
    chunks = splitter.split_text(text)  # Split the text into chunks
    
    # Create metadata for each chunk so we can trace back to original PDF
    metadatas = [{"source": source_name, "chunk": i} for i in range(len(chunks))]
    return chunks, metadatas

def main():
    # Step 1: Read all PDFs from private documents folder
    pdfs = read_pdfs(DOCUMENTS_PATH)
    if not pdfs:
        raise RuntimeError(f"No PDFs found in {DOCUMENTS_PATH}. Add files like handbook.pdf, policies.pdf")

    # Step 2: Set up OpenAI embeddings
    # Embeddings convert text into numerical vectors that capture meaning
    # "text-embedding-3-small" is OpenAI's efficient embedding model
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"  # Cheaper than ada-002, still very good
    )

    # Step 3: Process all PDFs and collect chunks
    all_texts = []  # Will store all text chunks from all PDFs
    all_meta  = []  # Will store metadata for each chunk

    # Process each PDF file
    for fname, text in pdfs:
        print(f"Processing {fname}...")  # Show progress
        chunks, meta = chunk_text(fname, text)  # Break into chunks
        all_texts.extend(chunks)  # Add chunks to master list
        all_meta.extend(meta)     # Add metadata to master list

    print(f"Ingesting {len(all_texts)} chunks from {len(pdfs)} PDFs...")

    # Step 4: Create vector database
    # This is the magic - converts all text chunks into searchable vectors
    # FAISS is a fast similarity search library created by Facebook
    vs = FAISS.from_texts(all_texts, embedding=embeddings, metadatas=all_meta)

    # Step 5: Save the vector database to private location
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    vs.save_local(FAISS_INDEX_PATH)
    print(f"✅ Done. FAISS index saved to {FAISS_INDEX_PATH}")
    print("Your PDFs are now searchable! Run the chatbot app next.")

if __name__ == "__main__":
    main()  # Run the ingestion process
