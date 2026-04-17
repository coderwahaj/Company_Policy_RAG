import { useState } from "react";
import { useChat } from "../hooks/useChat";

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const { messages, streaming, error, send, stop } = useChat({ provider: "groq" });

  function onSubmit(e) {
    e.preventDefault();
    send(query);
    setQuery("");
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
      <h2>Company Policy Chat (Streaming)</h2>

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
        {streaming && <div style={{ color: "#666" }}>Streaming…</div>}
      </div>

      {error && (
        <div style={{ color: "crimson", marginBottom: 12 }}>
          Error: {error}
        </div>
      )}

      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8 }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your question…"
          style={{ flex: 1, padding: 10 }}
          disabled={streaming}
        />
        <button type="submit" disabled={streaming}>
          Send
        </button>
        <button type="button" onClick={stop} disabled={!streaming}>
          Stop
        </button>
      </form>
    </div>
  );
}