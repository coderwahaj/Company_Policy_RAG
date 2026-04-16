import re

def classify_query(query, llm):
    query_lower = (query or "").lower().strip()
    identity_phrases = [
        "who are you","what are you","your name",
        "tell me about yourself","who is this","introduce yourself","what is this",
    ]
    policy_keywords = [
        "policy","leave","employment","contract","resign","resignation",
        "notice period","salary","compensation","commission","allowance",
        "communication","wallet","slab","withdrawal","year 1","year 2","year 3",
        "benefits","pf","esi","bonus","incentive","deduction","wamo labs","wamo","company",
    ]
    casual_triggers = [
        "hi","hello","hey","good morning","good afternoon","good evening",
        "how are you","how's your day","have a good day","bye","goodbye",
        "thanks","thank you","ok","okay","sure",
    ]

    if any(p in query_lower for p in identity_phrases):
        return "identity"
    if any(k in query_lower for k in policy_keywords):
        return "policy"
    if any(t == query_lower or query_lower.startswith(t + " ") for t in casual_triggers):
        return "casual"

    prompt = f"""Classify STRICTLY into: policy, casual, or unknown.
If question is NOT about company policy, answer "unknown".
Query: {query}
Answer (one word only):"""
    try:
        result = (llm.generate_raw(prompt) or "").lower().strip()
        if "policy" in result:
            return "policy"
        if "casual" in result:
            return "casual"
    except Exception:
        pass
    return "unknown"

def rewrite_query(query, llm):
    prompt = f"""Rewrite the query using company policy terminology.
Example: commission → allowance, salary → compensation
Query: {query}
Rewritten:"""
    return llm.generate_raw(prompt)

def truncate_context(context, max_chars=600):
    if not context:
        return ""
    if len(context) <= max_chars:
        return context
    sentences = re.split(r"(?<=[.!?]) +", context)
    truncated = ""
    for s in sentences:
        if len(truncated) + len(s) > max_chars:
            break
        truncated += s + " "
    return truncated.strip()

def run_rag(query, embedder, vector_store, llm, reranker, bm25, history=None):
    history = history or []
    recent = history[-8:]
    conversation_text = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in recent]
    )

    q_type = classify_query(query, llm)

    if q_type == "identity":
        return (
            "I'm the **Wamo Labs Company Policy Assistant** 🏢\n\n"
            "I help employees understand company policies, leave policies, "
            "employment contracts, compensation, and benefits.",
            [],
            "",
            "identity",
        )

    if q_type == "casual":
        answer = llm.generate(query, context=conversation_text, casual=True) or ""
        return answer, [], "", "casual"

    rewritten_query = rewrite_query(query, llm)
    qe = embedder.embed_query(rewritten_query)
    dense_results = vector_store.search(qe, k=20, threshold=0.2)
    sparse_results = bm25.search(query, k=15)

    sparse_results_formatted = [
        {
            "text": r["text"],
            "score": r["score"],
            "metadata": {"file_name": "unknown", "page": "N/A", "doc_type": "unknown"},
        }
        for r in sparse_results
    ]

    combined = dense_results + sparse_results_formatted
    docs = [{"text": r["text"], "metadata": r["metadata"]} for r in combined]
    reranked = reranker.rerank(query, docs, top_k=5)

    if not reranked:
        return (
            "I'm the **Wamo Labs Company Policy Assistant** 🏢\n\n"
            "I don't have information about that question in the company policy documents. "
            "Ask me about leave policies, compensation, contracts, or benefits.",
            [],
            "",
            "out_of_context",
        )

    context = "\n\n".join([r["text"] for r in reranked])
    full_context = (conversation_text + "\n\n" + context).strip()
    answer = llm.generate(query, full_context) or ""

    sources, seen = [], set()
    for r in reranked:
        src = f"{r['metadata']['file_name']} — Page {r['metadata']['page']}"
        if src not in seen:
            sources.append(src)
            seen.add(src)

    return answer, sources, context[:800], "ok"