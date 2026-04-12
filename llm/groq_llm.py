# from groq import Groq
# import os

# # =========================
# # GroqLLM
# # =========================


# class GroqLLM:
#     def __init__(self):
#         self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#     # Raw generation (classifier / rewrite)
#     def generate_raw(self, prompt):
#         response = self.client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0,
#             max_tokens=100,
#         )
#         return response.choices[0].message.content.strip()

#     def generate(self, query, context="", casual=False, fallback=False):

#         if casual:
#             prompt = f"""
#     You are a friendly, natural conversational policy assistant.

#     - Be warm, human-like, and engaging
#     - Keep replies short (2–3 lines)
#     - Do NOT mention company policy
#     - Respond naturally like a real person

#     User: {query}
#     Assistant:
#     """

#         elif fallback:
#             prompt = f"""
#     You are a friendly, natural conversational assistant.

#     - Be warm and human-like
#     - Keep replies short (1–3 lines)
#     - Answer the user's question naturally without mentioning company policy

#     User: {query}
#     Assistant:
#     """

#         else:
#             prompt = f"""
#     You are Wamo Labs Company Policy Assistant.

#     - Answer ONLY using the given context
#     - Be clear and structured
#     - If unsure, say you don't know

#     Context:
#     {context}

#     User: {query}
#     Assistant:
#     """

#         # Send the prompt to the Groq chat completion endpoint and return text
#         try:
#             response = self.client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 max_tokens=300,
#             )
#             return response.choices[0].message.content.strip()
#         except Exception:
#             return ""


from groq import Groq
import os


# =========================
# GroqLLM
# =========================


class GroqLLM:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)

    # Raw generation (classifier / rewrite)
    def generate_raw(self, prompt):
        """Generate raw response for classification/rewrite tasks.
        
        Returns:
            str: Generated text (never None)
        """
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )
            
            # ✅ Guard against None at each step
            if response is None:
                return ""
            if response.choices is None or len(response.choices) == 0:
                return ""
            
            message = response.choices[0].message
            if message is None:
                return ""
            
            content = message.content
            if content is None:
                return ""
            
            return content.strip()
            
        except Exception as e:
            print(f"⚠️ Error in generate_raw: {e}")
            return ""

    def generate(self, query, context="", casual=False, fallback=False):
        """Generate response for user query.
        
        Args:
            query: User's question
            context: Policy context (for policy mode)
            casual: Generate casual response (ignore context)
            fallback: Generate fallback response when no context found
            
        Returns:
            str: Generated text (never None, returns "" on error)
        """

        if casual:
            prompt = f"""
You are a friendly, natural conversational policy assistant.

- Be warm, human-like, and engaging
- Keep replies short (2–3 lines)
- Do NOT mention company policy
- Respond naturally like a real person

User: {query}
Assistant:
"""

        elif fallback:
            prompt = f"""
You are a friendly, natural conversational assistant.

- Be warm and human-like
- Keep replies short (1–3 lines)
- Answer the user's question naturally without mentioning company policy

User: {query}
Assistant:
"""

        else:
            prompt = f"""
You are Wamo Labs Company Policy Assistant.

- Answer ONLY using the given context
- Be clear and structured
- If unsure, say you don't know

Context:
{context}

User: {query}
Assistant:
"""

        # Send the prompt to the Groq chat completion endpoint
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
            )
            
            # ✅ CRITICAL: Guard against None at each step
            if response is None:
                print("⚠️ API returned None response")
                return ""
            
            if response.choices is None or len(response.choices) == 0:
                print("⚠️ API returned empty choices")
                return ""
            
            message = response.choices[0].message
            if message is None:
                print("⚠️ API returned None message")
                return ""
            
            content = message.content
            if content is None:
                print("⚠️ API returned None content")
                return ""
            
            result = content.strip()
            
            # ✅ Defensive: ensure result is a string
            if not isinstance(result, str):
                print(f"⚠️ Unexpected content type: {type(result)}")
                return ""
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error in generate: {type(e).__name__}: {e}")
            return ""