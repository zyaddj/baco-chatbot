# ingest_flexible.py
# Flexible ingestion script that can process different data folders
# Usage: python ingest_flexible.py --data_folder test_data --output_folder test_vectors

import os
import argparse
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env file")

def read_pdfs(folder: str) -> list[tuple[str, str]]:
    """Read all PDF files from specified folder"""
    docs = []
    
    if not os.path.exists(folder):
        print(f"❌ Folder {folder} does not exist!")
        return docs
    
    for fname in os.listdir(folder):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(folder, fname)
            try:
                reader = PdfReader(path)
                text_parts = []
                
                for page in reader.pages:
                    extracted_text = page.extract_text() or ""
                    text_parts.append(extracted_text)
                
                text = "\n".join(text_parts)
                docs.append((fname, text))
                print(f"✅ Processed: {fname} ({len(text)} characters)")
            except Exception as e:
                print(f"❌ Error reading {fname}: {e}")
    
    return docs

def chunk_text(source_name: str, text: str, chunk_chars: int = 1200, overlap: int = 200):
    """Split text into chunks with metadata"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_chars, chunk_overlap=overlap)
    chunks = splitter.split_text(text)
    metadatas = [{"source": source_name, "chunk": i} for i in range(len(chunks))]
    return chunks, metadatas

def main():
    parser = argparse.ArgumentParser(description="Flexible PDF ingestion")
    parser.add_argument("--data_folder", default="data", help="Folder containing PDF files")
    parser.add_argument("--output_folder", default="faiss_index", help="Output folder for vector index")
    args = parser.parse_args()
    
    data_folder = args.data_folder
    output_folder = args.output_folder
    
    print(f"📁 Data folder: {data_folder}")
    print(f"📁 Output folder: {output_folder}")
    
    # Read PDFs
    pdfs = read_pdfs(data_folder)
    if not pdfs:
        print(f"❌ No PDF files found in {data_folder}")
        return
    
    # Process all PDFs
    all_texts = []
    all_meta = []
    
    for fname, text in pdfs:
        chunks, meta = chunk_text(fname, text)
        all_texts.extend(chunks)
        all_meta.extend(meta)
    
    print(f"📊 Processing {len(all_texts)} chunks from {len(pdfs)} PDFs...")
    
    # Create embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    
    # Create vector database
    vs = FAISS.from_texts(all_texts, embedding=embeddings, metadatas=all_meta)
    
    # Save to specified output folder
    vs.save_local(output_folder)
    print(f"✅ Vector database saved to {output_folder}")
    print(f"🚀 Ready to use with: --vector_path {output_folder}")

if __name__ == "__main__":
    main()