// frontend/src/api/chat.js
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function chat({ query, provider = "groq", history = [] }) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, provider, history }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }

  return res.json();
}