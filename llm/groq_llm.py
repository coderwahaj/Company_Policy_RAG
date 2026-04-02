from groq import Groq
import os


class GroqLLM:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, query, context):
        prompt = f"""
You are a Company Policy Assistant.

Rules:
- Answer ONLY from the provided context
- Do NOT use external knowledge
- If answer is not clearly present → say "I don't know"
- If multiple answers exist → mention both clearly
- Keep answers concise and structured

Context:
{context}

Question:
{query}

Answer:
"""

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500,
        )

        return response.choices[0].message.content