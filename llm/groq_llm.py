# from groq import Groq
# import os


# class GroqLLM:
#     def __init__(self):
#         self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#     # =========================
#     # RAW GENERATION (for classifier + rewriting)
#     # =========================
#     def generate_raw(self, prompt):
#         response = self.client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0,
#             max_tokens=100,
#         )
#         return response.choices[0].message.content.strip()
# def generate(self, query, context="", casual=False, fallback=False):
#     if casual:
#         prompt = f"You are a friendly assistant.\nUser: {query}\nReply naturally:"
#     elif fallback:
#         prompt = f"""
# You are a Company Policy Assistant.
# I don't know based on company policy.
# However, generally, provide a brief 2-3 line answer to the user.

# User: {query}
# """
#     else:
#         prompt = f"""
# You are a Company Policy Assistant.
# Use the following context to answer:
# {context}
# User: {query}
# """

#     response = self.client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.3,
#         max_tokens=300
#     )
#     return response.choices[0].message.content.strip()
#     # =========================
#     # MAIN GENERATION (for answers)
#     # =========================
# #     def generate(self, query, context, casual=False, fallback=False):

# #         if casual:
# #             prompt = f"""
# # You are a friendly assistant.

# # User: {query}
# # Reply naturally:
# # """

# #         elif fallback:
# #             prompt = f"""
# # You are a Company Policy Assistant.

# # No exact policy found.

# # 1. Say you don't know based on company policy
# # 2. Then give general professional guidance

# # User: {query}
# # """

# #         else:
# #             prompt = f"""
# # You are a Company Policy Assistant.

# # Instructions:
# # - Use the context if relevant
# # - If answer not found → say "I don't know based on company policy"
# # - Then give general helpful guidance

# # Context:
# # {context}

# # User Question:
# # {query}

# # Answer:
# # """

# #         response = self.client.chat.completions.create(
# #             model="llama-3.3-70b-versatile",
# #             messages=[{"role": "user", "content": prompt}],
# #             temperature=0.3,
# #             max_tokens=500,
# #         )

# #         return response.choices[0].message.content.strip()


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
