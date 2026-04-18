#  Wamo Labs — Company Policy Assistant  
### RAG + Hybrid Search + FastAPI Streaming + React UI + Streamlit UI

An intelligent **Retrieval-Augmented Generation (RAG)** system built to answer internal company policy questions with **grounded, source-backed, low-hallucination responses**.

This project now supports:

- ⚡ **FastAPI backend** with **SSE token streaming**
- 💬 **React Chat UI** (ChatGPT-like experience)
- 🖥️ **Streamlit UI** (rapid demo/testing interface)
- 🧠 **Hybrid Retrieval Pipeline** (FAISS + BM25 + reranking)

---

## ✨ Core Features

- **Hybrid Retrieval (FAISS + BM25)** for stronger recall
- **Cross-Encoder Reranking** for high-quality top-k context
- **Streaming Responses (SSE)** from backend to frontend
- **LLM-backed generation** (Groq / Gemini support)
- **Query classification** (`policy` / `casual` / `unknown`)
- **Hallucination control** (safe fallback outside domain)
- **Conversational memory** (short session context)
- **Pipeline caching** (index persistence + warm loading)
- **Pipeline lifecycle APIs** (`load`, `status`, `reset`)
- **Evaluation scripts** for retrieval and answer quality
- **Dockerized deployment**

---

## 🏗️ High-Level Architecture

```text
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
   ├── FAISS (Dense semantic search)
   └── BM25  (Sparse keyword search)
   ▼
Merge + Deduplicate
   ▼
Reranker (Top-K)
   ▼
Context Builder (+ truncation)
   ▼
LLM Generation (Grounded)
   ▼
Response + Citations + Context
   ▼
FastAPI SSE Stream → React UI / Streamlit UI
```

---

## 📂 Project Structure

```text
Company_Policy_RAG/
│
├── backend/
│   └── app/
│       ├── api/
│       │   ├── routes.py                 # Standard REST endpoints
│       │   ├── stream_routes.py          # /chat/stream (SSE)
│       │   └── pipeline_routes.py        # /pipeline/load|status|reset
│       ├── core/
│       │   ├── pipeline.py               # Cached pipeline lifecycle
│       │   ├── rag_service.py            # RAG + streaming generator
│       │   └── settings.py
│       ├── models/
│       │   └── schemas.py                # Pydantic request/response models
│       └── main.py                       # FastAPI app entrypoint
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── chatStream.js             # SSE client parser
│   │   │   └── pipeline.js               # Pipeline API client
│   │   ├── hooks/
│   │   │   └── useChat.js                # Stream state + stop/abort logic
│   │   ├── components/
│   │   │   ├── ChatPage.jsx
│   │   │   └── Sidebar.jsx
│   │   └── main.jsx
│   └── .env                              # VITE_API_BASE_URL
│
├── rag/
│   ├── ingestion/loader.py
│   ├── processing/chunker.py
│   ├── embeddings/embedder.py
│   ├── vectorstore/faiss_store.py
│   ├── retriever/bm25_retriever.py
│   ├── reranker/reranker.py
│   └── llm/                              # Groq / Gemini integrations
│
├── data/policy/                          # Source policy PDFs
├── vector_store/                         # Generated FAISS + manifest (gitignored)
├── eval/
│   ├── eval_utils.py
│   └── eval_comparison.py
│
├── app.py                                # Streamlit UI entrypoint
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## ⚙️ Setup (Local Development)

## 1) Clone

```bash
git clone https://github.com/coderwahaj/Company_Policy_RAG.git
cd Company_Policy_RAG
```

## 2) Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

## 3) Install dependencies

```bash
pip install -r requirements.txt
```

## 4) Environment variables

Create `.env` in project root:

```env
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_huggingface_token
GEMINI_API_KEY=your_gemini_api_key
```

---

## 🚀 Run FastAPI Backend (Streaming API)

```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URL: **http://127.0.0.1:8000**

---

## 💬 Run React Frontend (Chat UI)

In a new terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run frontend:

```bash
npm run dev
```

Frontend URL (Vite): usually **http://127.0.0.1:5173**

---

## 🖥️ Run Streamlit UI (Optional)

```bash
streamlit run app.py
```

Streamlit URL: **http://localhost:8501**

> You can run both UIs (React + Streamlit) against the same backend/pipeline stack.

---

## 🔌 API Endpoints (FastAPI)

### Chat Streaming
- `POST /chat/stream`
- Content-Type: `application/json`
- Response: `text/event-stream` (events: `meta`, `token`, `done`, `error`)

Request body:
```json
{
  "query": "What is the notice period?",
  "provider": "groq",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ]
}
```

### Pipeline Control
- `POST /pipeline/load`
- `GET /pipeline/status?provider=groq`
- `POST /pipeline/reset`

---

## 🧪 Evaluation

```bash
python -m eval.eval_utils
python -m eval.eval_comparison
```

### Metrics tracked
- Retrieval accuracy
- Context relevance
- Answer faithfulness
- Hallucination rate

---

## 🐳 Docker

### Build
```bash
docker build -t wamo-policy-assistant .
```

### Run
```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY="your_groq_api_key" \
  -e HF_API_KEY="your_huggingface_token" \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -v $(pwd)/data:/app/data \
  wamo-policy-assistant
```

Adjust command if your Dockerfile starts Streamlit instead of FastAPI.

---

## 🧠 Design Decisions

| Component | Choice | Why |
|---|---|---|
| Retrieval | FAISS + BM25 | Better recall than dense-only |
| Ranking | Cross-encoder reranker | Improved top-k relevance |
| Safety | Query classification + fallback | Reduces hallucination risk |
| Serving | FastAPI + SSE | Real-time token streaming |
| UI | React + Streamlit | Product UI + rapid experimentation |
| Performance | Pipeline cache + persisted index | Faster warm starts |

---

## ⚠️ Current Limitations

- Scope limited to provided policy documents
- Session-level memory only (no long-term user memory)
- BM25 fusion weighting not yet optimized
- Access control/auth not added yet (recommended for internal rollout)

---

## 🛣️ Roadmap

- [ ] Weighted hybrid score fusion (FAISS + BM25)
- [ ] Retrieval metrics expansion (MRR, Recall@K, nDCG)
- [ ] Persistent user/session memory
- [ ] Admin dashboard for evaluation + observability
- [ ] Multi-language support
- [ ] Docker Compose for full stack (backend + frontend)

---

## 👨‍💻 Author

**Wahaj**  
Software Engineer | AI Enthusiast

---

## 🙏 Acknowledgements

[SentenceTransformers](https://www.sbert.net/) · [FAISS](https://faiss.ai/) · [Rank-BM25](https://github.com/dorianbrown/rank_bm25) · [Groq](https://groq.com/) · [Gemini](https://ai.google.dev/) · [FastAPI](https://fastapi.tiangolo.com/) · [React](https://react.dev/) · [Streamlit](https://streamlit.io/)
