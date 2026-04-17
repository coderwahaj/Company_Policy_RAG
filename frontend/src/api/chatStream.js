// frontend/src/api/chatStream.js
const API_BASE = import.meta.env.VITE_API_BASE_URL;

export function chatStream(
  { query, provider = "groq", history = [] },
  { onMeta, onToken, onDone, onError } = {}
) {
  const controller = new AbortController();

  async function start() {
    let gotDone = false;

    try {
      const res = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({ query, provider, history }),
        signal: controller.signal,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Request failed: ${res.status}`);
      }

      if (!res.body) {
        throw new Error("Streaming not supported: response body is empty.");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const lines = part.split("\n").filter(Boolean);

          let eventName = "message";
          let dataStr = "";

          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventName = line.slice("event:".length).trim();
            } else if (line.startsWith("data:")) {
              dataStr += line.slice("data:".length).trim() + "\n";
            }
          }

          dataStr = dataStr.trim();
          if (!dataStr) continue;

          let data;
          try {
            data = JSON.parse(dataStr);
          } catch {
            data = { raw: dataStr };
          }

          if (eventName === "meta") onMeta?.(data);
          else if (eventName === "token") onToken?.(data.delta || "");
          else if (eventName === "done") {
            gotDone = true;
            onDone?.(data);
          } else if (eventName === "error") {
            onError?.(data.message || "Unknown error");
          }
        }
      }

      if (!controller.signal.aborted && !gotDone) {
        onError?.("Stream ended before receiving 'done' event.");
      }
    } catch (err) {
      if (controller.signal.aborted) return;
      onError?.(err.message || String(err));
    }
  }

  start();

  return {
    abort() {
      controller.abort();
    },
  };
}