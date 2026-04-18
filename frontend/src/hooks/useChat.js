// import { useState } from "react";

// export function useChat({ provider }) {
//   const [messages, setMessages] = useState([]);
//   const [streaming, setStreaming] = useState(false);
//   const [error, setError] = useState(null);

//   const send = (query) => {
//     const q = query?.trim();
//     if (!q) return;

//     setError(null);
//     setMessages((prev) => [...prev, { role: "user", content: q }]);
//     setStreaming(true);

//     setTimeout(() => {
//       setMessages((prev) => [
//         ...prev,
//         {
//           role: "assistant",
//           content: `(${provider.toUpperCase()}) Simulated answer for: "${q}"\n\nBased on policy documents, the notice period is typically 2 months unless otherwise stated in your contract.`,
//           meta: {
//             sources: ["employment_contract.pdf", "communication.pdf"],
//           },
//         },
//       ]);
//       setStreaming(false);
//     }, 900);
//   };

//   const stop = () => {
//     setStreaming(false);
//   };

//   const clear = () => {
//     setMessages([]);
//     setError(null);
//     setStreaming(false);
//   };

//   return { messages, streaming, error, send, stop, clear };
// }

import { useEffect, useRef, useState } from "react";
import { chatStream } from "../api/chatStream";

export function useChat({ provider = "groq" } = {}) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState("");

  const streamRef = useRef(null);
  const queueRef = useRef([]);
  const doneReceivedRef = useRef(false);
  const finalMetaRef = useRef(null);
  const typerTimerRef = useRef(null);

  const CHARS_PER_TICK = 3;
  const TICK_MS = 24;

  function appendToLastAssistant(text) {
    if (!text) return;
    setMessages((prev) => {
      const out = [...prev];
      for (let i = out.length - 1; i >= 0; i--) {
        if (out[i].role === "assistant") {
          out[i] = { ...out[i], content: (out[i].content || "") + text };
          break;
        }
      }
      return out;
    });
  }

  function attachMetaToLastAssistant(meta) {
    setMessages((prev) => {
      const out = [...prev];
      for (let i = out.length - 1; i >= 0; i--) {
        if (out[i].role === "assistant") {
          out[i] = { ...out[i], meta: meta || {} };
          break;
        }
      }
      return out;
    });
  }

  function stopTyper() {
    if (typerTimerRef.current) {
      clearInterval(typerTimerRef.current);
      typerTimerRef.current = null;
    }
  }

  function flushAll() {
    if (queueRef.current.length === 0) return;
    const all = queueRef.current.join("");
    queueRef.current = [];
    appendToLastAssistant(all);
  }

  function startTyper() {
    if (typerTimerRef.current) return;

    typerTimerRef.current = setInterval(() => {
      if (queueRef.current.length > 0) {
        const next = queueRef.current[0];
        if (!next) {
          queueRef.current.shift();
          return;
        }

        const emit = next.slice(0, CHARS_PER_TICK);
        const rest = next.slice(CHARS_PER_TICK);
        appendToLastAssistant(emit);

        if (rest) queueRef.current[0] = rest;
        else queueRef.current.shift();
        return;
      }

      if (doneReceivedRef.current) {
        stopTyper();
        setStreaming(false);
        streamRef.current = null;

        if (finalMetaRef.current) {
          attachMetaToLastAssistant(finalMetaRef.current);
          finalMetaRef.current = null;
        }
      }
    }, TICK_MS);
  }

  function send(query) {
    const trimmed = (query || "").trim();
    if (!trimmed || streaming) return;

    setError("");
    setStreaming(true);

    queueRef.current = [];
    doneReceivedRef.current = false;
    finalMetaRef.current = null;
    startTyper();

    setMessages((prev) => {
      const next = [
        ...prev,
        { role: "user", content: trimmed },
        { role: "assistant", content: "" },
      ];

      const history = next.slice(0, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      streamRef.current?.abort?.();

      streamRef.current = chatStream(
        { query: trimmed, provider, history },
        {
          onMeta: () => {},
          onToken: (delta) => {
            if (delta) queueRef.current.push(delta);
          },
          onDone: (final) => {
            finalMetaRef.current = {
              status: final?.status || "ok",
              sources: final?.sources || [],
              context: final?.context || "",
            };
            doneReceivedRef.current = true;
          },
          onError: (msg) => {
            doneReceivedRef.current = true;
            flushAll();
            stopTyper();
            setStreaming(false);
            streamRef.current = null;
            setError(msg || "Streaming failed");
          },
        }
      );

      return next;
    });
  }

  function stop() {
    streamRef.current?.abort?.();
    streamRef.current = null;

    doneReceivedRef.current = true;
    flushAll();
    stopTyper();
    setStreaming(false);

    if (finalMetaRef.current) {
      attachMetaToLastAssistant(finalMetaRef.current);
      finalMetaRef.current = null;
    }
  }

  function clear() {
    stop();
    setMessages([]);
    setError("");
    queueRef.current = [];
    doneReceivedRef.current = false;
    finalMetaRef.current = null;
  }

  useEffect(() => {
    return () => {
      stopTyper();
      streamRef.current?.abort?.();
    };
  }, []);

  return { messages, streaming, error, send, stop, clear };
}