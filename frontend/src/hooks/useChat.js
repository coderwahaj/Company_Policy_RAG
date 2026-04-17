// // frontend/src/hooks/useChat.js
// import { useEffect, useRef, useState } from "react";
// import { chatStream } from "../api/chatStream";

// /**
//  * GPT-like streaming:
//  * - Receive deltas fast
//  * - Render them at a controlled pace
//  */
// export function useChat({ provider = "groq" } = {}) {
//   const [messages, setMessages] = useState([]);
//   const [streaming, setStreaming] = useState(false);
//   const [error, setError] = useState("");

//   const streamRef = useRef(null);

//   // Queue of incoming deltas
//   const queueRef = useRef([]);
//   // Timer that "types" from the queue into the UI
//   const typerTimerRef = useRef(null);

//   // Tune these to match GPT feel
//   const CHARS_PER_TICK = 2;  // how many chars to render per tick
//   const TICK_MS = 50;        // tick interval (25ms ~ smooth)

//   function appendToLastAssistant(text) {
//     if (!text) return;
//     setMessages((prev) => {
//       const out = [...prev];
//       for (let i = out.length - 1; i >= 0; i--) {
//         if (out[i].role === "assistant") {
//           out[i] = { ...out[i], content: out[i].content + text };
//           break;
//         }
//       }
//       return out;
//     });
//   }

//   function startTyper() {
//     if (typerTimerRef.current) return;

//     typerTimerRef.current = setInterval(() => {
//       if (queueRef.current.length === 0) return;

//       // Take next chunk from queue
//       let next = queueRef.current[0];
//       if (!next) {
//         queueRef.current.shift();
//         return;
//       }

//       // Render up to CHARS_PER_TICK chars
//       const emit = next.slice(0, CHARS_PER_TICK);
//       const rest = next.slice(CHARS_PER_TICK);

//       appendToLastAssistant(emit);

//       if (rest) queueRef.current[0] = rest;
//       else queueRef.current.shift();
//     }, TICK_MS);
//   }

//   function stopTyper() {
//     if (typerTimerRef.current) {
//       clearInterval(typerTimerRef.current);
//       typerTimerRef.current = null;
//     }
//   }

//   function flushAll() {
//     // Immediately render everything remaining (useful on Done/Stop)
//     if (queueRef.current.length === 0) return;
//     const all = queueRef.current.join("");
//     queueRef.current = [];
//     appendToLastAssistant(all);
//   }

//   function stop() {
//     streamRef.current?.abort?.();
//     streamRef.current = null;

//     flushAll();
//     stopTyper();

//     setStreaming(false);
//   }

//   function send(query) {
//     const trimmed = (query || "").trim();
//     if (!trimmed) return;

//     setError("");
//     setStreaming(true);

//     // reset queue for new answer
//     queueRef.current = [];
//     startTyper();

//     setMessages((prev) => {
//       const next = [
//         ...prev,
//         { role: "user", content: trimmed },
//         { role: "assistant", content: "" },
//       ];

//       const history = next
//         .slice(0, -1)
//         .map((m) => ({ role: m.role, content: m.content }));

//       streamRef.current = chatStream(
//         { query: trimmed, provider, history },
//         {
//           onToken: (delta) => {
//             // Push fast incoming tokens into queue
//             if (delta) queueRef.current.push(delta);
//           },
//           onDone: () => {
//             // Ensure we show everything
//             flushAll();
//             stopTyper();
//             setStreaming(false);
//             streamRef.current = null;

//             // OPTIONAL: attach metadata to last assistant message later
//             // (sources/context/status)
//           },
//           onError: (msg) => {
//             flushAll();
//             stopTyper();
//             setStreaming(false);
//             streamRef.current = null;
//             setError(msg);
//           },
//         }
//       );

//       return next;
//     });
//   }

//   useEffect(() => {
//     return () => {
//       stopTyper();
//       streamRef.current?.abort?.();
//     };
//   }, []);

//   return { messages, streaming, error, send, stop };
// }
// frontend/src/hooks/useChat.js
import { useEffect, useRef, useState } from "react";
import { chatStream } from "../api/chatStream";

export function useChat({ provider = "groq" } = {}) {
  const [messages, setMessages] = useState([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState("");

  const streamRef = useRef(null);

  // incoming deltas
  const queueRef = useRef([]);
  // server finished streaming (done received), but UI may still be typing
  const doneReceivedRef = useRef(false);

  const typerTimerRef = useRef(null);

  // Tune these to match GPT feel
  const CHARS_PER_TICK = 2; // slower typing; try 3–5 if too slow
  const TICK_MS = 35;       // 35–45 feels good

  function appendToLastAssistant(text) {
    if (!text) return;
    setMessages((prev) => {
      const out = [...prev];
      for (let i = out.length - 1; i >= 0; i--) {
        if (out[i].role === "assistant") {
          out[i] = { ...out[i], content: out[i].content + text };
          break;
        }
      }
      return out;
    });
  }

  function startTyper() {
    if (typerTimerRef.current) return;

    typerTimerRef.current = setInterval(() => {
      // drain queue gradually
      if (queueRef.current.length > 0) {
        let next = queueRef.current[0];
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

      // queue is empty: if backend already done, we can end streaming now
      if (doneReceivedRef.current) {
        stopTyper();
        setStreaming(false);
        streamRef.current = null;
      }
    }, TICK_MS);
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

  function stop() {
    // user pressed Stop: abort server + flush remaining immediately
    streamRef.current?.abort?.();
    streamRef.current = null;

    doneReceivedRef.current = true;
    flushAll();
    stopTyper();
    setStreaming(false);
  }

  function send(query) {
    const trimmed = (query || "").trim();
    if (!trimmed) return;

    setError("");
    setStreaming(true);

    // reset state for this run
    queueRef.current = [];
    doneReceivedRef.current = false;

    startTyper();

    setMessages((prev) => {
      const next = [
        ...prev,
        { role: "user", content: trimmed },
        { role: "assistant", content: "" },
      ];

      const history = next
        .slice(0, -1)
        .map((m) => ({ role: m.role, content: m.content }));

      // abort any existing stream (safety)
      streamRef.current?.abort?.();

      streamRef.current = chatStream(
        { query: trimmed, provider, history },
        {
          onToken: (delta) => {
            if (delta) queueRef.current.push(delta);
          },
          onDone: () => {
            // IMPORTANT: do NOT flush here.
            // Let the typer drain the queue naturally like ChatGPT.
            doneReceivedRef.current = true;
          },
          onError: (msg) => {
            doneReceivedRef.current = true;
            flushAll(); // show what we have
            stopTyper();
            setStreaming(false);
            streamRef.current = null;
            setError(msg);
          },
        }
      );

      return next;
    });
  }

  // StrictMode-safe cleanup
  useEffect(() => {
    return () => {
      stopTyper();
      streamRef.current?.abort?.();
    };
  }, []);

  return { messages, streaming, error, send, stop };
}