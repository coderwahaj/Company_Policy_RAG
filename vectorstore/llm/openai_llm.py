import os
import openai


class OpenAILLM:
    def __init__(self):
        # support either OPENAI_API_KEY or OPEN_API_KEY (your .env uses OPEN_API_KEY)
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_API_KEY") or os.getenv("OPENAPI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI API key not found. Set OPENAI_API_KEY or OPEN_API_KEY in your environment")
        openai.api_key = api_key
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate_raw(self, prompt):
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=120,
        )
        return resp.choices[0].message.content.strip()

    def generate(self, query, context="", casual=False, fallback=False):
        if casual:
            prompt = f"You are a friendly assistant.\nUser: {query}\nReply naturally:"
        elif fallback:
            prompt = f"""
You are a Wamo labs Company Policy Assistant.
You have to guide me as a personal assistant.
I don't know based on company policy.
However, generally, provide a brief 2-3 line answer to the user.

User: {query}
"""
        else:
            prompt = f"""
You are a a Wamo labs Company Policy Assistant.
You have to guide me as a personal assistant.
Use the following context to answer:

{context}

User: {query}
"""

        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )

        return resp.choices[0].message.content.strip()
