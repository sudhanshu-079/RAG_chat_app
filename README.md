 🧠 AI Knowledge Vault (RAG System)

A production-style Retrieval-Augmented Generation (RAG) system built using:

- 🔹 OpenAI GPT (gpt-4o-mini)
- 🔹 OpenAI Embeddings (text-embedding-3-small)
- 🔹 FAISS (Vector Database)
- 🔹 Python
- 🔹 dotenv (Secure API key management)

This system loads documents, creates embeddings, stores them in FAISS, retrieves relevant chunks, and generates accurate answers using GPT.

---

# 🚀 Features

✅ Document ingestion and chunking  
✅ OpenAI embedding generation  
✅ FAISS vector similarity search  
✅ Context-aware answer generation  
✅ Secure API key handling using `.env`  
✅ Modular and clean architecture  

---

# 🏗️ Project Architecture

```
ai-knowledge-vault/
│
├── rag.py              # Core RAG engine
├── vector_store.py     # FAISS handling (if separated)
├── test_rag.py         # RAG system testing
├── test_llm.py         # Direct LLM testing
│
├── data/
│   ├── knowledge.txt   # Sample document
│   └── faiss.index     # Generated vector index
│
├── .env                # API key (NOT pushed to GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ How It Works

### 1️⃣ Document Loading
- Reads a text file
- Splits into chunks

### 2️⃣ Embedding Creation
- Uses `text-embedding-3-small`
- Converts chunks into 1536-dimension vectors

### 3️⃣ Vector Storage
- Stores embeddings inside FAISS index

### 4️⃣ Retrieval
- Converts user query into embedding
- Finds top-k similar chunks

### 5️⃣ Answer Generation
- Sends retrieved context to `gpt-4o-mini`
- Generates structured response

---

# 🛠️ Installation & Setup

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-knowledge-vault.git
cd ai-knowledge-vault
```

---

## Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Add OpenAI API Key

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

⚠️ Never upload `.env` to GitHub.

---

# ▶️ Running the Project

## Test LLM Directly

```bash
python test_llm.py
```

---

## Test Full RAG Pipeline

```bash
python test_rag.py
```

---

# 📦 Dependencies

- openai
- python-dotenv
- faiss-cpu
- numpy

Install manually if needed:

```bash
pip install openai python-dotenv faiss-cpu numpy
```

---

# 🔐 Security

- API keys stored securely in `.env`
- `.env` excluded using `.gitignore`
- No hardcoded credentials

---

# 💡 Future Improvements

- Token-based chunking
- Cosine similarity optimization
- Flask API integration
- Frontend UI
- Streaming responses
- Support for PDF ingestion
- Multi-document support

---

# 🎯 Use Cases

- Research assistant
- Internal knowledge base
- Document Q&A system
- AI-powered FAQ bot
- Academic project demonstration

---

# 🧑‍💻 Author

Sudhanshu Kumar Suman  
AI/ML Developer | Backend Enthusiast | RAG Systems Builder

---

# ⭐ If You Like This Project

Give it a ⭐ on GitHub!
