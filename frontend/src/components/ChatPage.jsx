import { useEffect, useMemo, useRef, useState } from "react";
import { useChat } from "../hooks/useChat";
import Sidebar from "./Sidebar";
import SourceCard from "./SourceCard";

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

  // sidebar state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

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

  const titleProvider = useMemo(
    () => (provider === "groq" ? "Groq" : "Gemini"),
    [provider],
  );

  function handleLoadPipeline() {
    setPipelineReady(true);
    setChunkCount(1234);
  }

  function handleResetPipeline() {
    setPipelineReady(false);
    setChunkCount("—");
    clear();
  }

  function handleClearChat() {
    clear();
  }

  function handleSuggestion(question) {
    setQuery(question);
  }

  function onSubmit(e) {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed || !pipelineReady || streaming) return;
    send(trimmed);
    setQuery("");
  }

  function copyToClipboard(text) {
    navigator.clipboard?.writeText(text || "");
  }

  function openSource(source) {
    if (typeof source === "string" && source.startsWith("http")) {
      window.open(source, "_blank", "noopener,noreferrer");
      return;
    }
    alert(
      `Source: ${typeof source === "string" ? source : JSON.stringify(source)}`,
    );
  }

  return (
    // APP LEVEL: full viewport, no page scroll
    <div className="h-screen overflow-hidden bg-[radial-gradient(circle_at_top,#132237_0%,#070b12_45%,#05070b_100%)] text-slate-100">
      <div className="h-full p-3 md:p-4">
        {/* Full-height horizontal layout */}
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
          />

          {/* Main chat area takes remaining width */}
          <main className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl shadow-[0_20px_80px_rgba(0,0,0,0.4)]">
            {/* IMPORTANT: flex column + h-full to control internal scrolling */}
            <section className="flex h-full flex-col">
              {/* Header fixed in flow */}
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

              {/* Messages area = ONLY vertical scroll in main content */}
              <div className="min-h-0 flex-1 overflow-y-auto scroll-on-hover px-3 py-4 md:px-6">
                {messages.length === 0 ? (
                  <div className="mx-auto mt-8 max-w-2xl rounded-2xl border border-white/10 bg-white/[0.02] p-6 text-center">
                    <p className="text-lg font-medium text-slate-100">
                      Ask anything about Company Policies
                    </p>
                    <p className="mt-2 text-sm text-slate-400">
                      Try one of the sample questions below to begin.
                    </p>
                    <div className="mt-5 flex flex-wrap justify-center gap-2">
                      {SAMPLE_QUESTIONS.map((q) => (
                        <button
                          key={q}
                          onClick={() => handleSuggestion(q)}
                          className="rounded-full border border-white/15 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-200 transition hover:border-cyan-300/40 hover:bg-cyan-300/10"
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

                            <div className="whitespace-pre-wrap text-sm md:text-[15px] leading-relaxed text-slate-100">
                              {m.content}
                              {showCursor && (
                                <span className="ml-1 inline-block h-4 w-1 animate-pulse rounded bg-cyan-300 align-middle" />
                              )}
                            </div>

                            {m.meta?.sources?.length > 0 && (
                              <div className="mt-3 space-y-2">
                                <p className="text-xs font-medium text-slate-400">
                                  Citations
                                </p>
                                {m.meta.sources.map((s, i) => (
                                  <SourceCard
                                    key={i}
                                    source={s}
                                    onCopy={copyToClipboard}
                                    onOpen={openSource}
                                  />
                                ))}
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

              {/* Input area always visible at bottom */}
              <div className="shrink-0 border-t border-white/10 bg-[#060a12]/90 px-3 py-3 md:px-4 md:py-4 backdrop-blur supports-[backdrop-filter]:bg-[#060a12]/70">
                {error && (
                  <div className="mb-2 text-sm text-red-400">
                    Error: {error}
                  </div>
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
                    type="submit"
                    disabled={!pipelineReady || streaming || !query.trim()}
                    className="rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 px-4 py-3 text-sm font-semibold text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Send
                  </button>
                  <button
                    type="button"
                    onClick={stop}
                    disabled={!streaming}
                    className="rounded-xl border border-white/15 bg-white/[0.04] px-4 py-3 text-sm text-slate-200 transition hover:bg-white/[0.08] disabled:opacity-50"
                  >
                    Stop
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
