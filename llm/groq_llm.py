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
            # ✅ SHOULD NEVER BE CALLED - but if it does, refuse everything
            prompt = f"""You are Wamo Labs Policy Assistant.

STRICT RULE: This is a fallback - always refuse and redirect.
Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."

User: {query}
Assistant:"""

        else:
            # ✅ MAIN POLICY PROMPT - EXTREMELY STRICT
            prompt = f"""You are Wamo Labs Company Policy Assistant. YOUR ONLY JOB IS TO ANSWER POLICY QUESTIONS.

⚠️ CRITICAL RULES (FOLLOW EXACTLY):
1. Answer ONLY if the information is in the context
2. If the user asks about ANY non-policy topic (Python, sports, history, etc.), REFUSE
3. Say EXACTLY: "I'm the Wamo Labs Company Policy Assistant. I don't have information about that in the policy documents. I can help with: leave policies, employment contracts, compensation, and benefits."
4. Do NOT answer general knowledge questions under any circumstances
5. Do NOT hallucinate or invent information
6. If a slab/table is mentioned but missing, say: "Not found in the provided policy text"
7. Be structured and clear

CONTEXT (ONLY use this):
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
