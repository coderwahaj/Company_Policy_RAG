import os
import requests
import json


class QwenLLM:
    """
    LLM using OpenRouter API with Qwen3 Coder model.
    Supports both regular generation and streaming.
    """
    
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENROUTER_API_KEY not found in environment variables")
        
        self.api_key = api_key
        self.model = "qwen/qwen3-coder:free"  # Free Qwen3 Coder model
        self.base_url = "https://openrouter.ai/api/v1"

    def generate_raw(self, prompt):
        """
        Generate a single non-streaming response.
        Used for quick, simple completions.
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Wamo Policy Assistant",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            "max_tokens": 100,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
            else:
                return "Error: No response from model"
                
        except Exception as e:
            print(f"Error in generate_raw: {e}")
            return f"Error: {str(e)}"

    def generate(self, query, context="", casual=False, fallback=False):
        """
        Generate a single non-streaming response.
        Used for non-streaming endpoints.
        """
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

        return self.generate_raw(prompt)

    def generate_stream(self, query, context="", casual=False, fallback=False):
        """
        Stream response tokens using OpenRouter's streaming API.
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

        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Wamo Policy Assistant",
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 300,
            "stream": True,
        }

        try:
            # Send meta event
            yield ("meta", {})
            
            # Make streaming request
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            # Process stream
            for line in response.iter_lines():
                if not line:
                    continue
                
                # OpenRouter sends lines like: data: {"choices":[{"delta":{"content":"token"}}]}
                line_str = line.decode("utf-8") if isinstance(line, bytes) else line
                
                if line_str.startswith("data: "):
                    data_str = line_str[6:]  # Remove "data: " prefix
                    
                    # Skip [DONE] message
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                        
                        # Extract token from OpenRouter response format
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            choice = chunk["choices"][0]
                            
                            # Check for delta (streaming)
                            if "delta" in choice and "content" in choice["delta"]:
                                token = choice["delta"]["content"]
                                if token:
                                    yield ("token", {"delta": token})
                            
                            # Check for finish_reason (stream end)
                            if "finish_reason" in choice and choice["finish_reason"] is not None:
                                # Stream finished, will yield done event below
                                pass
                    
                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue
            
            # Send done event after stream completes
            yield ("done", {})
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            print(f"Error in generate_stream: {error_message}")
            yield ("error", {"message": f"Streaming failed: {error_message}"})
        except Exception as e:
            error_message = str(e)
            print(f"Unexpected error in generate_stream: {error_message}")
            yield ("error", {"message": f"Stream error: {error_message}"})