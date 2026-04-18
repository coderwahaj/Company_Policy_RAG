// import { useEffect, useMemo, useRef, useState } from "react";
// import { useChat } from "../hooks/useChat";
// import {
//   loadPipeline,
//   resetPipeline,
//   getPipelineStatus,
// } from "../api/pipeline";
// import Sidebar from "./Sidebar";
// import ReactMarkdown from "react-markdown";
// import remarkGfm from "remark-gfm";

// const INDEXED_DOCS = [
//   "communication.pdf",
//   "employment_contract.pdf",
//   "leave_policy.pdf",
// ];

// const SAMPLE_QUESTIONS = [
//   "How many leave days do I get?",
//   "What is the resignation notice period?",
//   "What is the communication allowance?",
//   "Can I carry forward unused annual leave?",
// ];

// export default function ChatPage() {
//   const [query, setQuery] = useState("");
//   const [provider, setProvider] = useState("groq");
//   const [pipelineReady, setPipelineReady] = useState(false);
//   const [chunkCount, setChunkCount] = useState("—");
//   const [pipelineLoading, setPipelineLoading] = useState(false);
//   const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

//   const { messages, streaming, error, send, stop, clear } = useChat({
//     provider,
//   });
//   const bottomRef = useRef(null);

//   useEffect(() => {
//     bottomRef.current?.scrollIntoView({
//       behavior: streaming ? "auto" : "smooth",
//       block: "end",
//     });
//   }, [messages, streaming]);

//   useEffect(() => {
//     let mounted = true;
//     (async () => {
//       try {
//         const status = await getPipelineStatus(provider);
//         if (!mounted) return;
//         setPipelineReady(!!status?.ready);
//         setChunkCount(status?.chunk_count ?? "—");
//       } catch {
//         if (!mounted) return;
//         setPipelineReady(false);
//         setChunkCount("—");
//       }
//     })();
//     return () => {
//       mounted = false;
//     };
//   }, [provider]);

//   const titleProvider = useMemo(
//     () => (provider === "groq" ? "Groq" : "Gemini"),
//     [provider],
//   );

//   async function handleLoadPipeline() {
//     try {
//       setPipelineLoading(true);
//       const data = await loadPipeline(provider);
//       setPipelineReady(true);
//       setChunkCount(data?.chunk_count ?? "—");
//     } catch (e) {
//       alert(`Load pipeline failed: ${e.message}`);
//       setPipelineReady(false);
//       setChunkCount("—");
//     } finally {
//       setPipelineLoading(false);
//     }
//   }

//   async function handleResetPipeline() {
//     try {
//       setPipelineLoading(true);
//       await resetPipeline(provider);
//       setPipelineReady(false);
//       setChunkCount("—");
//       clear();
//     } catch (e) {
//       alert(`Reset pipeline failed: ${e.message}`);
//     } finally {
//       setPipelineLoading(false);
//     }
//   }

//   function handleClearChat() {
//     clear();
//   }

//   // Auto-send sample question
//   function handleSuggestion(question) {
//     if (!pipelineReady || streaming) return;
//     send(question);
//   }

//   function onSubmit(e) {
//     e.preventDefault();
//     const trimmed = query.trim();
//     if (!trimmed || !pipelineReady || streaming) return;
//     send(trimmed);
//     setQuery("");
//   }

//   function copyToClipboard(text) {
//     navigator.clipboard?.writeText(text || "");
//   }

//   return (
//     <div className="h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#132237_0%,#070b12_45%,#05070b_100%)] text-slate-100">
//       <div className="h-full p-3 md:p-4">
//         <div className="flex h-full gap-3">
//           <Sidebar
//             collapsed={sidebarCollapsed}
//             onToggleCollapse={() => setSidebarCollapsed((v) => !v)}
//             botName="Wamo Labs Policy Assistant"
//             provider={provider}
//             setProvider={setProvider}
//             pipelineReady={pipelineReady}
//             onLoadPipeline={handleLoadPipeline}
//             onReset={handleResetPipeline}
//             onClear={handleClearChat}
//             chunkCount={chunkCount}
//             indexedDocs={INDEXED_DOCS}
//             suggestions={SAMPLE_QUESTIONS}
//             onSuggestion={handleSuggestion}
//             messagesCount={messages.length}
//             loading={pipelineLoading}
//           />

//           <main className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl shadow-[0_20px_80px_rgba(0,0,0,0.4)]">
//             <section className="flex h-full flex-col">
//               <header className="shrink-0 flex items-center justify-between gap-4 border-b border-white/10 px-4 py-4 md:px-6">
//                 <div className="min-w-0">
//                   <h1 className="truncate text-lg md:text-2xl font-semibold tracking-tight">
//                     Company Policy Chat
//                   </h1>
//                   <p className="truncate text-xs md:text-sm text-slate-400">
//                     Grounded answers with citations • Model: {titleProvider}
//                   </p>
//                 </div>
//                 <div className="shrink-0 rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-200">
//                   {pipelineReady ? "Pipeline Loaded" : "Pipeline Not Loaded"}
//                 </div>
//               </header>

//               <div className="min-h-0 flex-1 overflow-y-auto scroll-on-hover px-3 py-4 md:px-6">
//                 {messages.length === 0 ? (
//                   <div className="mx-auto mt-8 max-w-2xl rounded-2xl border border-white/10 bg-white/[0.02] p-6 text-center">
//                     <p className="text-lg font-medium text-slate-100">
//                       Ask anything about Company Policies
//                     </p>
//                     <p className="mt-2 text-sm text-slate-400">
//                       Click one sample question to ask instantly.
//                     </p>
//                     <div className="mt-5 flex flex-wrap justify-center gap-2">
//                       {SAMPLE_QUESTIONS.map((q) => (
//                         <button
//                           key={q}
//                           onClick={() => handleSuggestion(q)}
//                           disabled={!pipelineReady || streaming}
//                           className="rounded-full border border-white/15 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-200 transition hover:border-cyan-300/40 hover:bg-cyan-300/10 disabled:opacity-50"
//                         >
//                           {q}
//                         </button>
//                       ))}
//                     </div>
//                   </div>
//                 ) : (
//                   <div className="space-y-4 pb-2">
//                     {messages.map((m, idx) => {
//                       const isUser = m.role === "user";
//                       const isLast = idx === messages.length - 1;
//                       const showCursor = streaming && isLast && !isUser;

//                       return (
//                         <div
//                           key={idx}
//                           className={`flex ${isUser ? "justify-end" : "justify-start"}`}
//                         >
//                           <div
//                             className={[
//                               "max-w-[88%] rounded-2xl px-4 py-3 shadow-lg",
//                               isUser
//                                 ? "border border-cyan-300/30 bg-gradient-to-br from-cyan-400/20 to-violet-400/20"
//                                 : "border border-white/10 bg-white/[0.04]",
//                             ].join(" ")}
//                           >
//                             <div className="mb-1 text-xs uppercase tracking-wide text-slate-400">
//                               {isUser ? "You" : "Assistant"}
//                             </div>

//                             <div className="prose prose-invert max-w-none text-sm md:text-[15px] leading-relaxed">
//                               <ReactMarkdown remarkPlugins={[remarkGfm]}>
//                                 {m.content || ""}
//                               </ReactMarkdown>
//                             </div>
//                             {showCursor && (
//                               <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded bg-cyan-300 align-middle" />
//                             )}

//                             {/* Markdown-like collapsible citations/context */}
//                             {(m.meta?.sources?.length > 0 ||
//                               m.meta?.context) && (
//                               <div className="mt-3 space-y-2">
//                                 {m.meta?.sources?.length > 0 && (
//                                   <details className="rounded-lg border border-white/10 bg-black/20 p-2">
//                                     <summary className="cursor-pointer text-xs font-medium text-slate-300">
//                                       Citations ({m.meta.sources.length})
//                                     </summary>
//                                     <div className="mt-2 space-y-2">
//                                       {m.meta.sources.map((s, i) => (
//                                         <div
//                                           key={i}
//                                           className="flex items-center justify-between gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2"
//                                         >
//                                           <span className="truncate text-xs text-slate-200">
//                                             {String(s)}
//                                           </span>
//                                           <button
//                                             onClick={() =>
//                                               copyToClipboard(String(s))
//                                             }
//                                             className="shrink-0 rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
//                                           >
//                                             Copy
//                                           </button>
//                                         </div>
//                                       ))}
//                                     </div>
//                                   </details>
//                                 )}
                                
//                                 {typeof m.meta?.context === "string" &&
//                                   m.meta.context.trim().length > 0 && (
//                                     <details className="mt-2 rounded-lg border border-white/10 bg-black/20 p-2">
//                                       <summary className="cursor-pointer text-xs font-medium text-slate-300">
//                                         Context Snippet
//                                       </summary>

//                                       <div className="mt-2 space-y-2">
//                                         <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-lg border border-white/10 bg-white/[0.03] p-3 text-xs text-slate-200">
//                                           {m.meta.context}
//                                         </pre>

//                                         <button
//                                           onClick={() =>
//                                             navigator.clipboard?.writeText(
//                                               String(m.meta.context),
//                                             )
//                                           }
//                                           className="rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
//                                         >
//                                           Copy Context
//                                         </button>
//                                       </div>
//                                     </details>
//                                   )}
//                               </div>
//                             )}
//                           </div>
//                         </div>
//                       );
//                     })}
//                     <div ref={bottomRef} />
//                   </div>
//                 )}
//               </div>

//               <div className="shrink-0 border-t border-white/10 bg-[#060a12]/90 px-3 py-3 md:px-4 md:py-4 backdrop-blur supports-[backdrop-filter]:bg-[#060a12]/70">
//                 {error && (
//                   <div className="mb-2 text-sm text-red-400">
//                     Error: {error}
//                   </div>
//                 )}

//                 <form onSubmit={onSubmit} className="flex items-center gap-2">
//                   <input
//                     value={query}
//                     onChange={(e) => setQuery(e.target.value)}
//                     placeholder={
//                       pipelineReady
//                         ? "Ask about company policies..."
//                         : "Load pipeline first"
//                     }
//                     disabled={!pipelineReady || streaming}
//                     className="flex-1 rounded-xl border border-white/15 bg-black/30 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-cyan-300/50 disabled:opacity-60"
//                   />

//                   {/* Single interchangeable icon button */}
//                   <button
//                     type={streaming ? "button" : "submit"}
//                     onClick={streaming ? stop : undefined}
//                     disabled={!pipelineReady || (!streaming && !query.trim())}
//                     title={streaming ? "Stop" : "Send"}
//                     className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
//                   >
//                     {streaming ? (
//                       <span className="h-3.5 w-3.5 rounded-sm bg-slate-900" />
//                     ) : (
//                       <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current">
//                         <path d="M3.4 20.4 21.85 12 3.4 3.6 3.38 10.2 16 12 3.38 13.8z" />
//                       </svg>
//                     )}
//                   </button>
//                 </form>
//               </div>
//             </section>
//           </main>
//         </div>
//       </div>
//     </div>
//   );
// }


import { useEffect, useMemo, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import {
  loadPipeline,
  resetPipeline,
  getPipelineStatus,
} from "../api/pipeline";
import Sidebar from "./Sidebar";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const INDEXED_DOCS = [
  "communication.pdf",
  "employment_contract.pdf",
  "leave_policy.pdf",
];

const SAMPLE_QUESTIONS = [
  "How many leave days do I get?",
  "What is the resignation notice period?",
  "What is the communication allowance?",
  "Can I carry forward unused annual leave?",
];

export default function ChatPage() {
  const [query, setQuery] = useState("");
  const [provider, setProvider] = useState("groq");
  const [pipelineReady, setPipelineReady] = useState(false);
  const [chunkCount, setChunkCount] = useState("—");
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [copiedKey, setCopiedKey] = useState("");

  const { messages, streaming, error, send, stop, clear } = useChat({
    provider,
  });

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: streaming ? "auto" : "smooth",
      block: "end",
    });
  }, [messages, streaming]);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const status = await getPipelineStatus(provider);
        if (!mounted) return;
        setPipelineReady(!!status?.ready);
        setChunkCount(status?.chunk_count ?? "—");
      } catch {
        if (!mounted) return;
        setPipelineReady(false);
        setChunkCount("—");
      }
    })();

    return () => {
      mounted = false;
    };
  }, [provider]);

  const titleProvider = useMemo(
    () => (provider === "groq" ? "Groq" : "Gemini"),
    [provider]
  );

  async function handleLoadPipeline() {
    try {
      setPipelineLoading(true);
      const data = await loadPipeline(provider);
      setPipelineReady(true);
      setChunkCount(data?.chunk_count ?? "—");
    } catch (e) {
      alert(`Load pipeline failed: ${e.message}`);
      setPipelineReady(false);
      setChunkCount("—");
    } finally {
      setPipelineLoading(false);
    }
  }

  async function handleResetPipeline() {
    try {
      setPipelineLoading(true);
      await resetPipeline(provider);
      setPipelineReady(false);
      setChunkCount("—");
      clear();
    } catch (e) {
      alert(`Reset pipeline failed: ${e.message}`);
    } finally {
      setPipelineLoading(false);
    }
  }

  function handleClearChat() {
    clear();
  }

  // Auto-send sample question
  function handleSuggestion(question) {
    if (!pipelineReady || streaming) return;
    send(question);
  }

  function onSubmit(e) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !pipelineReady || streaming) return;
    send(trimmed);
    setQuery("");
  }

  function copyToClipboard(text, key = "") {
    navigator.clipboard?.writeText(text || "");
    setCopiedKey(key);
    setTimeout(() => {
      setCopiedKey((prev) => (prev === key ? "" : prev));
    }, 1200);
  }

  return (
    <div className="h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#132237_0%,#070b12_45%,#05070b_100%)] text-slate-100">
      <div className="h-full p-3 md:p-4">
        <div className="flex h-full gap-3">
          <Sidebar
            collapsed={sidebarCollapsed}
            onToggleCollapse={() => setSidebarCollapsed((v) => !v)}
            botName="Wamo Labs Policy Assistant"
            provider={provider}
            setProvider={setProvider}
            pipelineReady={pipelineReady}
            onLoadPipeline={handleLoadPipeline}
            onReset={handleResetPipeline}
            onClear={handleClearChat}
            chunkCount={chunkCount}
            indexedDocs={INDEXED_DOCS}
            suggestions={SAMPLE_QUESTIONS}
            onSuggestion={handleSuggestion}
            messagesCount={messages.length}
            loading={pipelineLoading}
          />

          <main className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl shadow-[0_20px_80px_rgba(0,0,0,0.4)]">
            <section className="flex h-full flex-col">
              <header className="shrink-0 flex items-center justify-between gap-4 border-b border-white/10 px-4 py-4 md:px-6">
                <div className="min-w-0">
                  <h1 className="truncate text-lg md:text-2xl font-semibold tracking-tight">
                    Company Policy Chat
                  </h1>
                  <p className="truncate text-xs md:text-sm text-slate-400">
                    Grounded answers with citations • Model: {titleProvider}
                  </p>
                </div>
                <div className="shrink-0 rounded-full border border-cyan-300/30 bg-cyan-300/10 px-3 py-1 text-xs text-cyan-200">
                  {pipelineReady ? "Pipeline Loaded" : "Pipeline Not Loaded"}
                </div>
              </header>

              <div className="min-h-0 flex-1 overflow-y-auto scroll-on-hover px-3 py-4 md:px-6">
                {messages.length === 0 ? (
                  <div className="mx-auto mt-8 max-w-2xl rounded-2xl border border-white/10 bg-white/[0.02] p-6 text-center">
                    <p className="text-lg font-medium text-slate-100">
                      Ask anything about Company Policies
                    </p>
                    <p className="mt-2 text-sm text-slate-400">
                      Click one sample question to ask instantly.
                    </p>
                    <div className="mt-5 flex flex-wrap justify-center gap-2">
                      {SAMPLE_QUESTIONS.map((q) => (
                        <button
                          key={q}
                          onClick={() => handleSuggestion(q)}
                          disabled={!pipelineReady || streaming}
                          className="rounded-full border border-white/15 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-200 transition hover:border-cyan-300/40 hover:bg-cyan-300/10 disabled:opacity-50"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 pb-2">
                    {messages.map((m, idx) => {
                      const isUser = m.role === "user";
                      const isLast = idx === messages.length - 1;
                      const showCursor = streaming && isLast && !isUser;

                      return (
                        <div
                          key={idx}
                          className={`flex ${isUser ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={[
                              "max-w-[88%] rounded-2xl px-4 py-3 shadow-lg",
                              isUser
                                ? "border border-cyan-300/30 bg-gradient-to-br from-cyan-400/20 to-violet-400/20"
                                : "border border-white/10 bg-white/[0.04]",
                            ].join(" ")}
                          >
                            <div className="mb-1 text-xs uppercase tracking-wide text-slate-400">
                              {isUser ? "You" : "Assistant"}
                            </div>

                            <div className="prose prose-invert max-w-none text-sm md:text-[15px] leading-relaxed">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {m.content || ""}
                              </ReactMarkdown>
                            </div>

                            {showCursor && (
                              <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded bg-cyan-300 align-middle" />
                            )}

                            {!isUser && (
                              <div className="mt-3 flex justify-end">
                                <button
                                  onClick={() =>
                                    copyToClipboard(m.content || "", `resp-${idx}`)
                                  }
                                  className="rounded-md border border-white/15 bg-white/[0.04] px-2.5 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
                                >
                                  {copiedKey === `resp-${idx}`
                                    ? "Copied!"
                                    : "Copy Response"}
                                </button>
                              </div>
                            )}

                            {(m.meta?.sources?.length > 0 ||
                              (typeof m.meta?.context === "string" &&
                                m.meta.context.trim().length > 0)) && (
                              <div className="mt-3 space-y-2">
                                {m.meta?.sources?.length > 0 && (
                                  <details className="rounded-lg border border-white/10 bg-black/20 p-2">
                                    <summary className="cursor-pointer text-xs font-medium text-slate-300">
                                      Citations ({m.meta.sources.length})
                                    </summary>
                                    <div className="mt-2 space-y-2">
                                      {m.meta.sources.map((s, i) => (
                                        <div
                                          key={i}
                                          className="flex items-center justify-between gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2"
                                        >
                                          <span className="truncate text-xs text-slate-200">
                                            {String(s)}
                                          </span>
                                          <button
                                            onClick={() =>
                                              copyToClipboard(
                                                String(s),
                                                `src-${idx}-${i}`
                                              )
                                            }
                                            className="shrink-0 rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
                                          >
                                            {copiedKey === `src-${idx}-${i}`
                                              ? "Copied!"
                                              : "Copy"}
                                          </button>
                                        </div>
                                      ))}
                                    </div>
                                  </details>
                                )}

                                {typeof m.meta?.context === "string" &&
                                  m.meta.context.trim().length > 0 && (
                                    <details className="rounded-lg border border-white/10 bg-black/20 p-2">
                                      <summary className="cursor-pointer text-xs font-medium text-slate-300">
                                        Context Snippet
                                      </summary>

                                      <div className="mt-2 space-y-2">
                                        <pre className="max-h-56 overflow-auto whitespace-pre-wrap rounded-lg border border-white/10 bg-white/[0.03] p-3 text-xs text-slate-200">
                                          {m.meta.context}
                                        </pre>

                                        <button
                                          onClick={() =>
                                            copyToClipboard(
                                              String(m.meta.context),
                                              `ctx-${idx}`
                                            )
                                          }
                                          className="rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
                                        >
                                          {copiedKey === `ctx-${idx}`
                                            ? "Copied!"
                                            : "Copy Context"}
                                        </button>
                                      </div>
                                    </details>
                                  )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                    <div ref={bottomRef} />
                  </div>
                )}
              </div>

              <div className="shrink-0 border-t border-white/10 bg-[#060a12]/90 px-3 py-3 md:px-4 md:py-4 backdrop-blur supports-[backdrop-filter]:bg-[#060a12]/70">
                {error && (
                  <div className="mb-2 text-sm text-red-400">Error: {error}</div>
                )}

                <form onSubmit={onSubmit} className="flex items-center gap-2">
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={
                      pipelineReady
                        ? "Ask about company policies..."
                        : "Load pipeline first"
                    }
                    disabled={!pipelineReady || streaming}
                    className="flex-1 rounded-xl border border-white/15 bg-black/30 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-cyan-300/50 disabled:opacity-60"
                  />

                  <button
                    type={streaming ? "button" : "submit"}
                    onClick={streaming ? stop : undefined}
                    disabled={!pipelineReady || (!streaming && !query.trim())}
                    title={streaming ? "Stop" : "Send"}
                    className="grid h-11 w-11 place-items-center rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {streaming ? (
                      <span className="h-3.5 w-3.5 rounded-sm bg-slate-900" />
                    ) : (
                      <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current">
                        <path d="M3.4 20.4 21.85 12 3.4 3.6 3.38 10.2 16 12 3.38 13.8z" />
                      </svg>
                    )}
                  </button>
                </form>
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}