# 🔐 BACO Chatbot Security & Privacy

## 📋 Privacy Implementation

This chatbot has been configured with privacy-first architecture to protect sensitive company documents.

### 🛡️ Security Measures Implemented

#### **1. Document Isolation**
- ✅ **Sensitive documents removed from Git tracking**
- ✅ **Documents stored in private directory outside repository**
- ✅ **FAISS vector index stored privately**
- ✅ **Updated .gitignore to prevent future document commits**

#### **2. Private Data Locations**
```bash
# Documents are now stored here (PRIVATE):
/Users/zyaddjouad/Documents/vale shi/private_baco_data/documents/

# FAISS index is now stored here (PRIVATE):
/Users/zyaddjouad/Documents/vale shi/private_baco_data/faiss_index/

# Repository only contains (PUBLIC):
- Application code (app.py, ingest.py, etc.)
- Configuration files
- Dependencies (requirements.txt)
```

#### **3. Environment Variables**
```env
# .env file (NOT committed to Git)
OPENAI_API_KEY=your_api_key_here
PRIVATE_DATA_PATH=/Users/zyaddjouad/Documents/vale shi/private_baco_data
DOCUMENTS_PATH=/Users/zyaddjouad/Documents/vale shi/private_baco_data/documents
FAISS_INDEX_PATH=/Users/zyaddjouad/Documents/vale shi/private_baco_data/faiss_index
```

### 🚀 Deployment Privacy

#### **For Production Deployment:**

1. **Streamlit Cloud Secrets:**
   ```toml
   OPENAI_API_KEY = "your_api_key"
   DOCUMENTS_PATH = "/mount/private/documents"
   FAISS_INDEX_PATH = "/mount/private/faiss_index"
   ```

2. **Document Upload Process:**
   - Documents uploaded via secure admin interface
   - Processed immediately into vector database
   - Original files can be deleted after processing
   - No document content stored in application code

3. **Multi-Tenant Privacy:**
   - Each client gets isolated data directory
   - Client A cannot access Client B's documents
   - Separate FAISS indexes per client
   - Role-based access controls

### 📁 Directory Structure

```
📦 Project Structure
├── 🔓 baco-chatbot/ (PUBLIC REPOSITORY)
│   ├── app.py              # Application code
│   ├── ingest.py           # Document processing
│   ├── backend.py          # API endpoints
│   ├── requirements.txt    # Dependencies
│   ├── .env               # API keys (ignored)
│   └── .gitignore         # Privacy protection
│
├── 🔒 private_baco_data/ (PRIVATE - NOT IN GIT)
│   ├── documents/         # Original PDFs
│   │   ├── BACO Realty-Employee Handbook 2023.pdf
│   │   └── FMOG_Final_2023V1.pdf
│   └── faiss_index/      # Processed vector database
│       ├── index.faiss
│       └── index.pkl
```

### 🔧 Setup Instructions

#### **Initial Setup:**
```bash
# 1. Clone repository (public code only)
git clone https://github.com/zyaddj/baco-chatbot.git

# 2. Create private data directory
mkdir -p "/path/to/private/documents"
mkdir -p "/path/to/private/faiss_index"

# 3. Copy your documents to private location
cp your_documents.pdf "/path/to/private/documents/"

# 4. Configure environment variables
echo "DOCUMENTS_PATH=/path/to/private/documents" >> .env
echo "FAISS_INDEX_PATH=/path/to/private/faiss_index" >> .env

# 5. Run ingestion to process private documents
python ingest.py

# 6. Start application
streamlit run app.py
```

### 🚨 Security Best Practices

#### **What's Protected:**
- ✅ Company handbook content
- ✅ Internal policy documents  
- ✅ Processed document embeddings
- ✅ API keys and credentials
- ✅ Client-specific data

#### **What's Public:**
- ✅ Application source code
- ✅ Dependencies and requirements
- ✅ General configuration structure
- ✅ Documentation and setup guides

#### **Compliance Features:**
- 🔐 **Data Encryption**: Documents stored with file system encryption
- 📝 **Audit Logging**: All document access logged (future)
- 🗑️ **Data Deletion**: Easy document removal process
- 🌍 **Data Residency**: Control where documents are stored
- 👥 **Access Control**: Authentication required for all access

### 🔄 Migration Notes

If moving from the old public setup:
1. Documents automatically moved to private location
2. Code updated to use environment-based paths
3. Git history cleaned of sensitive files
4. FAISS index rebuilt in private location

### 📞 Support

For security questions or issues:
- Check environment variable configuration
- Verify private directory permissions
- Ensure .env file is properly configured
- Contact admin if document access issues occur

---

**🎯 Result**: Your chatbot is now privacy-compliant and ready for production deployment while keeping sensitive documents completely private!