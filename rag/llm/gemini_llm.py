# import os
# import google.generativeai as genai


# class GeminiLLM:
#     def __init__(self):
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise EnvironmentError("GEMINI_API_KEY not found")

#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel("gemini-1.5-flash-8b")

#     def generate_raw(self, prompt):
#         response = self.model.generate_content(
#             prompt, generation_config={"temperature": 0, "max_output_tokens": 100}
#         )
#         return response.text.strip()

#     def generate(self, query, context="", casual=False, fallback=False):
#         if casual:
#             prompt = f"""
#             You are a friendly assistant.

#             Conversation:
#             {context}

#             User: {query}
#             Reply naturally:"""
#         elif fallback:
#             prompt = f"""
#             You are a friendly assistant.

#             Conversation:
#             {context}

#             Provide a brief (1-3 line) helpful answer to the user's general question.
#             Do NOT mention company policy or explain that the question is out of scope.

#             User: {query}
#             """
#         else:
#             prompt = f"""
#             You are a Wamo labs Company Policy Assistant.
#             Use the following context to answer:

#             {context}

#             User: {query}
#             """

#         response = self.model.generate_content(
#             prompt, generation_config={"temperature": 0.3, "max_output_tokens": 300}
#         )
#         return response.text.strip()

#     def generate_stream(self, query, context="", casual=False, fallback=False):
#         # Build prompt (same as generate)
#         if casual:
#             prompt = f"""You are a friendly assistant handling casual greetings.

#         RULES:
#         - Be warm and brief (1–2 lines)
#         - Only respond to: greetings, thanks, farewells
#         - Do NOT try to answer questions
#         - Do NOT answer policy questions
#         - Respond naturally

#         User: {query}
#         Assistant:"""
#         elif fallback:
#             prompt = f"""You are Wamo Labs Policy Assistant.

#             STRICT RULE: This is a fallback - always refuse and redirect.
#             Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."

#             User: {query}
#             Assistant:"""
#         else:
#             prompt = f"""You are Wamo Labs Company Policy Assistant.

#             CRITICAL RULES:
#             1. If the context contains an answer to the user's question, provide it directly and clearly
#             2. Do NOT refuse to answer if the answer is in the context
#             3. If the question is about something NOT covered in the policy documents AND not in the context, then refuse:
#             Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."
#             4. Do NOT hallucinate or invent information beyond the context
#             5. Be structured and clear

#             CONTEXT:
#             {context}

#             User Question: {query}
#             Assistant:"""

#         try:
#             stream = self.client.chat.completions.create(
#                 model="gemini-1.5-flash-8b",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.1,
#                 max_tokens=300,
#                 stream=True,
#             )

#             count = 0
#             for chunk in stream:
#                 if count < 3:
#                     print("DEBUG STREAM CHUNK:", chunk)
#                     count += 1
#                 # --- Try a few known locations for delta text ---
#                 delta = None

#                 try:
#                     c0 = chunk.choices[0]

#                     # Most common in streaming:
#                     if getattr(c0, "delta", None) is not None:
#                         delta = getattr(c0.delta, "content", None)

#                     # Sometimes SDK uses message even in stream:
#                     if not delta and getattr(c0, "message", None) is not None:
#                         delta = getattr(c0.message, "content", None)

#                 except Exception:
#                     delta = None

#                 if delta:
#                     yield delta

#         except Exception as e:
#             print(f"Error in generate_stream: {e}")
#             return

import os
import google.generativeai as genai


class GeminiLLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY not found")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash-8b")

    def generate_raw(self, prompt):
        response = self.model.generate_content(
            prompt, generation_config={"temperature": 0, "max_output_tokens": 100}
        )
        return response.text.strip()

    def generate(self, query, context="", casual=False, fallback=False):
        if casual:
            prompt = f"""
            You are a friendly assistant.

            Conversation:
            {context}

            User: {query}
            Reply naturally:"""
        elif fallback:
            prompt = f"""
            You are a friendly assistant.

            Conversation:
            {context}

            Provide a brief (1-3 line) helpful answer to the user's general question.
            Do NOT mention company policy or explain that the question is out of scope.

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
            prompt, generation_config={"temperature": 0.3, "max_output_tokens": 300}
        )
        return response.text.strip()

    def generate_stream(self, query, context="", casual=False, fallback=False):
        """
        Stream response tokens using Gemini's native streaming API.
        Yields tuples: (event_name, data_dict)

        Expected events:
        - ("meta", {})
        - ("token", {"delta": "token_text"})
        - ("done", {})
        - ("error", {"message": "error text"})
        """

        # Build prompt
        if casual:
            prompt = f"""You are a friendly assistant handling casual greetings.

RULES:
- Be warm and brief (1–2 lines)
- Only respond to: greetings, thanks, farewells
- Do NOT try to answer questions
- Do NOT answer policy questions
- Respond naturally

User: {query}
Assistant:"""
        elif fallback:
            prompt = f"""You are Wamo Labs Policy Assistant.

STRICT RULE: This is a fallback - always refuse and redirect.
Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."

User: {query}
Assistant:"""
        else:
            prompt = f"""You are Wamo Labs Company Policy Assistant.

CRITICAL RULES:
1. If the context contains an answer to the user's question, provide it directly and clearly
2. Do NOT refuse to answer if the answer is in the context
3. If the question is about something NOT covered in the policy documents AND not in the context, then refuse:
Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."
4. Do NOT hallucinate or invent information beyond the context
5. Be structured and clear

CONTEXT:
{context}

User Question: {query}
Assistant:"""

        try:
            # Send initial meta event
            yield ("meta", {})

            # Use Gemini's native streaming API
            stream = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 300,
                },
                stream=True,
            )

            # Iterate through stream chunks
            for chunk in stream:
                if chunk.text:
                    # Yield each token
                    yield ("token", {"delta": chunk.text})

            # Send done event after stream completes
            yield ("done", {})

        except Exception as e:
            error_message = str(e)
            print(f"Error in generate_stream: {error_message}")
            yield ("error", {"message": f"Streaming failed: {error_message}"})
