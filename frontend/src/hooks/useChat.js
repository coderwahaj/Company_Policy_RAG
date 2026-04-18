import { useState } from "react";

export function useChat({ provider }) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState(null);

  const send = (query) => {
    const q = query?.trim();
    if (!q) return;

    setError(null);
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setStreaming(true);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `(${provider.toUpperCase()}) Simulated answer for: "${q}"\n\nBased on policy documents, the notice period is typically 2 months unless otherwise stated in your contract.`,
          meta: {
            sources: ["employment_contract.pdf", "communication.pdf"],
          },
        },
      ]);
      setStreaming(false);
    }, 900);
  };

  const stop = () => {
    setStreaming(false);
  };

  const clear = () => {
    setMessages([]);
    setError(null);
    setStreaming(false);
  };

  return { messages, streaming, error, send, stop, clear };
}