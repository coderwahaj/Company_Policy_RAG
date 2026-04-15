# 🏢 Wamo Labs Company Policy Assistant (RAG + Hybrid Search)

An **intelligent Retrieval-Augmented Generation (RAG) system** designed to answer company policy-related queries with high accuracy, grounded responses, and zero hallucination.

This system leverages **Hybrid Search (FAISS + BM25)**, **Reranking**, and **LLM reasoning** to deliver reliable answers strictly from company documents.

---

##  Features

* 🔍 **Hybrid Retrieval (FAISS + BM25)**

  * Combines dense + sparse search for improved recall
* 🧠 **LLM-Powered Answer Generation**

  * Context-aware, grounded responses using Groq / Gemini
* 🎯 **Query Classification**

  * Separates:

    * Policy queries
    * Casual queries
    * Out-of-context queries
*  **Hallucination Control**

  * Refuses to answer outside company policy scope
*  **Reranking Layer**

  * Improves relevance of retrieved chunks
*  **Conversational Memory**

  * Maintains short-term chat context
*  **Cached Pipeline**

  * Saves and loads FAISS index + metadata
*  **Evaluation Framework**

  * Retrieval accuracy
  * RAG performance testing
  * Before/After Hybrid Search comparison

---

## 🏗️ Architecture

```
User Query
   │
   ▼
Query Classification (policy / casual / unknown)
   │
   ├── Casual → Direct LLM response
   ├── Unknown → Safe fallback response
   ▼
Query Rewrite
   ▼
Hybrid Retrieval
   ├── FAISS (Dense Embeddings)
   ├── BM25 (Keyword Search)
   ▼
Merge Results
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
│   └── loader.py               # Load PDFs
│
├── processing/
│   └── chunker.py              # Chunk documents
│
├── embeddings/
│   └── embedder.py             # SentenceTransformer embeddings
│
├── vectorstore/
│   └── faiss_store.py          # FAISS implementation (with save/load)
│
├── retriever/
│   └── bm25_retriever.py       # BM25 search
│
├── reranker/
│   └── reranker.py             # Reranking logic
│
├── llm/
│   ├── groq_llm.py             # Groq integration
│   └── __init__.py             # LLM selector
│
├── eval/
│   ├── dataset.py              # Evaluation dataset
│   ├── eval_utils.py           # Evaluation pipeline
│   └── eval_comparison.py      # Baseline vs Hybrid comparison
│
├── vector_store/
│   ├── faiss.index
│   ├── docstore.pkl
│   └── manifest.json
│
├── app.py                      # Streamlit UI (main app)
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/rag-company-policy.git
cd rag-company-policy
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
HF_API_KEY=your_huggingface_token
```

---

## ▶️ Running the Application

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## 🧪 Evaluation

### Run evaluation:

```bash
python eval/eval_utils.py
```

### Compare Baseline vs Hybrid:

```bash
python -m eval.eval_comparison
```

---

##  Evaluation Metrics

*  Retrieval Accuracy
*  Context Relevance
*  Answer Faithfulness
*  Hallucination Rate

---

## 🧠 Key Design Decisions

### 🔹 Hybrid Search (FAISS + BM25)

* FAISS → semantic similarity
* BM25 → keyword matching
* Combined → better recall + robustness

### 🔹 Query Classification

* Prevents unnecessary retrieval
* Blocks out-of-domain queries

### 🔹 Reranking

* Improves Top-K relevance
* Reduces noisy context

### 🔹 Context Truncation

* Prevents token overflow
* Keeps most relevant content

---

##  Limitations

* Limited to provided policy documents
* No long-term memory (only session-based)
* BM25 currently unweighted (future improvement)

---

##  Future Improvements

*  Hybrid score weighting (FAISS + BM25)
*  Advanced metrics (MRR, Recall@K)
*  Long-term memory (vector DB persistence)
*  Evaluation dashboard (LangSmith-like)
*  Multi-language support

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📜 License

This project is for educational and internal use.

---

## 👨‍💻 Author

**Wahaj**
Software Engineer | AI Enthusiast

---

## ⭐ Acknowledgements

* SentenceTransformers
* FAISS
* Rank-BM25
* Groq API
* Streamlit

---
