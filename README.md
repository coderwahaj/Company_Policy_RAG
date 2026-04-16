# 🏢 Wamo Labs — Company Policy Assistant (RAG + Hybrid Search)

An intelligent **Retrieval-Augmented Generation (RAG)** system designed to answer company policy queries with high accuracy, grounded responses, and zero hallucination.

Built with **Hybrid Search (FAISS + BM25)**, **Reranking**, and **LLM reasoning** to deliver reliable answers strictly from company documents.

---

## ✨ Features

-  **Hybrid Retrieval (FAISS + BM25)** — Dense + sparse search for improved recall
-  **LLM-Powered Answer Generation** — Context-aware, grounded responses via Groq / Gemini
-  **Query Classification** — Separates policy, casual, and out-of-context queries
-  **Hallucination Control** — Refuses to answer outside company policy scope
-  **Reranking Layer** — Improves relevance of retrieved chunks
-  **Conversational Memory** — Maintains short-term chat context
-  **Cached Pipeline** — Saves and loads FAISS index + metadata
-  **Evaluation Framework** — Retrieval accuracy + RAG performance testing
-  **Docker Support** — Fully containerized for consistent deployment

---

## 🏗️ Architecture

```
User Query
   │
   ▼
Query Classification (policy / casual / unknown)
   │
   ├── Casual  → Direct LLM response
   ├── Unknown → Safe fallback response
   ▼
Query Rewrite
   ▼
Hybrid Retrieval
   ├── FAISS (Dense Embeddings)
   └── BM25  (Keyword Search)
   ▼
Merge + Deduplicate Results
   ▼
Reranker (Top-K selection)
   ▼
Context Builder
   ▼
LLM (Grounded Answer Generation)
   ▼
Final Response + Sources
```

---

## 📂 Project Structure

```
rag_company_doc/
│
├── data/
│   └── policy/                  # Source documents (PDFs)
│
├── ingestion/
│   └── loader.py                # Load and parse PDFs
│
├── processing/
│   └── chunker.py               # Chunk documents
│
├── embeddings/
│   └── embedder.py              # SentenceTransformer embeddings
│
├── vectorstore/
│   └── faiss_store.py           # FAISS implementation (with save/load)
│
├── retriever/
│   └── bm25_retriever.py        # BM25 keyword search
│
├── reranker/
│   └── reranker.py              # Cross-encoder reranking
│
├── llm/
│   ├── groq_llm.py              # Groq LLM integration
│   └── __init__.py              # LLM selector (Groq / Gemini)
│
├── eval/
│   ├── dataset.py               # Evaluation dataset
│   ├── eval_utils.py            # Evaluation pipeline
│   └── eval_comparison.py       # Baseline vs Hybrid comparison
│
├── vector_store/                # Auto-generated (gitignored)
│   ├── faiss.index
│   ├── docstore.pkl
│   └── manifest.json
│
├── Dockerfile                   # Docker container definition
├── .dockerignore                # Files excluded from Docker build
├── app.py                       # Streamlit UI (main entry point)
├── main.py                      # RAG pipeline logic
├── requirements.txt             # Python dependencies
└── README.md
```

---

## ⚙️ Installation (Local)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/coderwahaj/Company_Policy_RAG.git
cd Company_Policy_RAG
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\activate         # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_huggingface_token
GEMINI_API_KEY=your_gemini_api_key
```

### ▶️ Run the App
```bash
streamlit run app.py
```

Open: **http://localhost:8501**

---

## 🐳 Docker (Recommended)

### Build the Image
```bash
docker build -t wamo-policy-chatbot .
```

### Run the Container
```bash
docker run -p 8501:8501 \
  -e GROQ_API_KEY="your_groq_api_key" \
  -e HF_API_KEY="your_huggingface_token" \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -v $(pwd)/data:/app/data \
  wamo-policy-chatbot
```

Open: **http://localhost:8501**

> **Note:** If port 8501 is in use, change `-p 8501:8501` to `-p 8502:8501` and open `http://localhost:8502`

### Useful Docker Commands
```bash
docker ps                          # List running containers
docker stop <container_id>         # Stop a container
docker images                      # List all images
docker logs <container_id>         # View container logs
docker rmi wamo-policy-chatbot     # Remove image to rebuild fresh
```

---

## 🧪 Evaluation

```bash
# Run retrieval + RAG evaluation
python -m eval.eval_utils

# Compare Baseline vs Hybrid Search
python -m eval.eval_comparison
```

### Metrics
- ✅ Retrieval Accuracy
- ✅ Context Relevance
- ✅ Answer Faithfulness
- ✅ Hallucination Rate

---

## 🧠 Key Design Decisions

| Component | Decision | Reason |
|---|---|---|
| **Hybrid Search** | FAISS + BM25 | Better recall than dense-only |
| **Query Classification** | LLM-based | Blocks out-of-domain queries |
| **Reranking** | Cross-encoder | Improves Top-K relevance |
| **Context Truncation** | Sentence-boundary | Prevents token overflow |
| **Containerization** | Docker | Consistent, portable deployment |

---

## ⚠️ Limitations

- Limited to provided policy documents
- No long-term memory (session-based only)
- BM25 currently unweighted

---

## 🚀 Future Improvements

- [ ] Hybrid score weighting (FAISS + BM25 fusion)
- [ ] Advanced metrics (MRR, Recall@K)
- [ ] Long-term memory (persistent vector DB)
- [ ] Evaluation dashboard
- [ ] Multi-language support
- [ ] Docker Compose setup

---

## 📜 License

This project is for educational and internal use at Wamo Labs.

---

## 👨‍💻 Author

**Wahaj** — Software Engineer | AI Enthusiast

---

## ⭐ Acknowledgements

[SentenceTransformers](https://www.sbert.net/) · [FAISS](https://faiss.ai/) · [Rank-BM25](https://github.com/dorianbrown/rank_bm25) · [Groq API](https://groq.com/) · [Streamlit](https://streamlit.io/)
