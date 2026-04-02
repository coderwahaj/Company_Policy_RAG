def evaluate_retrieval(vector_store, embedder, dataset, k=5):
    results = []

    for item in dataset:
        query = item["question"]
        query_embedding = embedder.embed_query(query)

        retrieved = vector_store.search(query_embedding, k=k)

        retrieved_texts = [r["text"].lower() for r in retrieved]

        score = 0
        for keyword in item["expected_keywords"]:
            if any(keyword.lower() in text for text in retrieved_texts):
                score += 1

        precision = score / len(item["expected_keywords"])

        results.append({
            "query": query,
            "retrieval_score": precision
        })

    return results


def evaluate_rag(vector_store, embedder, llm, dataset, reranker=None):

    def context_builder(query):
        query_embedding = embedder.embed_query(query)
        retrieved = vector_store.search(query_embedding, k=10)

        if reranker:
            docs = [{"text": r["text"], "metadata": r["metadata"]} for r in retrieved]
            retrieved = reranker.rerank(query, docs, top_k=3)

        context = "\n\n".join([r["text"][:500] for r in retrieved])
        return context

    results = []

    for item in dataset:
        query = item["question"]

        context = context_builder(query)
        answer = llm.generate(query, context).lower()

        score = 0
        for keyword in item["expected_keywords"]:
            if keyword.lower() in answer:
                score += 1

        faithfulness = score / len(item["expected_keywords"])

        results.append({
            "query": query,
            "faithfulness_score": faithfulness,
            "answer": answer
        })

    return results