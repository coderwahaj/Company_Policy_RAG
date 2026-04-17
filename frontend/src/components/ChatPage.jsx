import { useState } from "react";
import { chat } from "../api/chat";

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]); // {role: 'user'|'assistant', content: string}
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSend(e) {
    e.preventDefault();
    setError("");

    const trimmed = query.trim();
    if (!trimmed) return;

    // optimistic UI
    const nextMessages = [...messages, { role: "user", content: trimmed }];
    setMessages(nextMessages);
    setQuery("");
    setLoading(true);

    try {
      const data = await chat({
        query: trimmed,
        provider: "groq",
        history: [], // we’ll wire history properly later
      });

      const answer =
        data?.answer ??
        data?.response ??
        data?.message ??
        JSON.stringify(data, null, 2);

      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
      <h2>Company Policy Chat</h2>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 8,
          padding: 12,
          minHeight: 300,
          marginBottom: 12,
          whiteSpace: "pre-wrap",
        }}
      >
        {messages.length === 0 ? (
          <div style={{ color: "#666" }}>Ask a question to start…</div>
        ) : (
          messages.map((m, idx) => (
            <div key={idx} style={{ marginBottom: 10 }}>
              <strong>{m.role === "user" ? "You" : "Assistant"}:</strong>{" "}
              {m.content}
            </div>
          ))
        )}
        {loading && <div style={{ color: "#666" }}>Thinking…</div>}
      </div>

      {error && (
        <div style={{ color: "crimson", marginBottom: 12 }}>
          Error: {error}
        </div>
      )}

      <form onSubmit={onSend} style={{ display: "flex", gap: 8 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your question…"
          style={{ flex: 1, padding: 10 }}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
}