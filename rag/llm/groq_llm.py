from groq import Groq
import os


class GroqLLM:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)

    def generate_raw(self, prompt):
        """Generate raw response for classification/rewrite tasks."""
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )
            if response is None or not response.choices:
                return ""
            return (
                response.choices[0].message.content.strip()
                if response.choices[0].message
                else ""
            )
        except Exception as e:
            print(f"⚠️ Error in generate_raw: {e}")
            return ""

    def generate(self, query, context="", casual=False, fallback=False):
        """Generate response for user query."""

        if casual:
            prompt = f"""You are a friendly assistant handling casual greetings.

            RULES:
            - Be warm and brief (1–2 lines)
            - Only respond to: greetings, thanks, farewells
            - Do NOT try to answer questions
            - Respond naturally

            User: {query}
            Assistant:"""

        elif fallback:
            # SHOULD NEVER BE CALLED - but if it does, refuse everything
            prompt = f"""You are Wamo Labs Policy Assistant.

            STRICT RULE: This is a fallback - always refuse and redirect.
            Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."

            User: {query}
            Assistant:"""

        else:
            #  MAIN POLICY PROMPT - ANSWER FROM CONTEXT
            prompt = f"""You are Wamo Labs Company Policy Assistant.

            ⚠️ CRITICAL RULES:
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
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # ✅ VERY LOW - near-deterministic
                max_tokens=300,
            )

            if response is None or not response.choices:
                return ""

            content = (
                response.choices[0].message.content
                if response.choices[0].message
                else ""
            )
            return content.strip() if content else ""

        except Exception as e:
            print(f"⚠️ Error in generate: {e}")
            return ""

    def generate_stream(self, query, context="", casual=False, fallback=False):
        # Build prompt (same as generate)
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
            stream = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
                stream=True,
            )

            count = 0
            for chunk in stream:
                if count < 3:
                    print("DEBUG STREAM CHUNK:", chunk)
                    count += 1
                # --- Try a few known locations for delta text ---
                delta = None

                try:
                    c0 = chunk.choices[0]

                    # Most common in streaming:
                    if getattr(c0, "delta", None) is not None:
                        delta = getattr(c0.delta, "content", None)

                    # Sometimes SDK uses message even in stream:
                    if not delta and getattr(c0, "message", None) is not None:
                        delta = getattr(c0.message, "content", None)

                except Exception:
                    delta = None

                if delta:
                    yield delta

        except Exception as e:
            print(f"Error in generate_stream: {e}")
            return
