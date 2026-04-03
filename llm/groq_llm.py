from groq import Groq
import os

# =========================
# GroqLLM
# =========================
class GroqLLM:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Raw generation (classifier / rewrite)
    def generate_raw(self, prompt):
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()

    # Main generation (answers)
    def generate(self, query, context="", casual=False, fallback=False):
        if casual:
            prompt = f"You are a friendly assistant.\nUser: {query}\nReply naturally:"
        elif fallback:
            prompt = f"""
You are a Company Policy Assistant.
I don't know based on company policy.
However, generally, provide a brief 2-3 line answer to the user.

User: {query}
"""
        else:
            prompt = f"""
You are a Company Policy Assistant.
Use the following context to answer:

{context}

User: {query}
"""
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
