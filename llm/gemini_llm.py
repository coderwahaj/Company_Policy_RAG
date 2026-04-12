import os
import google.generativeai as genai


class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY not found")

        genai.configure(api_key=api_key)

        # BEST FREE MODEL
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    def generate_raw(self, prompt):
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 100
            }
        )
        return response.text.strip()

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
You are a Wamo labs Company Policy Assistant.
Use the following context to answer:

{context}

User: {query}
"""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 300
            }
        )

        return response.text.strip()