// export default function Sidebar({
//   collapsed = false,
//   onToggleCollapse,
//   botName,
//   provider,
//   setProvider,
//   pipelineReady,
//   onLoadPipeline,
//   onReset,
//   onClear,
//   chunkCount = "—",
//   messagesCount = 0,
//   indexedDocs = [],
//   suggestions = [],
//   onSuggestion,

// }) {
//   return (
//     <aside
//       className={[
//         "h-full shrink-0 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl",
//         "shadow-[0_20px_70px_rgba(0,0,0,0.35)] transition-all duration-300",
//         collapsed
//           ? "w-[78px]"
//           : "w-fit max-w-[260px] min-w-[220px]",
//       ].join(" ")}
//     >
//       <div className="h-full min-h-0 px-3 py-3 overflow-y-auto scroll-on-hover scroll-smooth">

//         {/* Header */}
//         <div className="mb-4 flex items-start justify-between gap-2">
//           <div className="flex items-start gap-2 min-w-0">
//             <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-violet-400 text-slate-900 font-bold shrink-0">
//               AI
//             </div>

//             {!collapsed && (
//               <div className="min-w-0 pr-1">
//                 <h2 className="text-lg font-semibold text-slate-100 leading-tight">
//                   {botName}
//                 </h2>
//                 <p className="text-xs text-slate-400 mt-0.5">
//                   Modern RAG Assistant
//                 </p>
//               </div>
//             )}
//           </div>

//           <button
//             onClick={onToggleCollapse}
//             className="mt-0.5 shrink-0 rounded-lg border border-white/15 bg-white/[0.04] px-2 py-1 text-xs text-slate-200 hover:bg-white/[0.08]"
//           >
//             {collapsed ? "»" : "«"}
//           </button>
//         </div>

//         {!collapsed && (
//           <>
//             {/* Model Select */}
//             <div className="mb-4">
//               <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">
//                 Choose Model
//               </label>
//               <select
//                 value={provider}
//                 onChange={(e) => setProvider(e.target.value)}
//                 className="w-full max-w-[200px] rounded-xl border border-white/15 bg-black/30 px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-300/50"
//               >
//                 <option value="groq">Groq</option>
//                 <option value="gemini">Gemini</option>
//               </select>
//             </div>

//             {/* Buttons */}
//             <div className="mb-4 flex flex-wrap gap-2">
//               <button
//                 onClick={onLoadPipeline}
//                 className="w-fit rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 px-3 py-2 text-sm font-semibold text-slate-900 hover:brightness-110"
//               >
//                 Load Pipeline
//               </button>

//               <button
//                 onClick={onReset}
//                 className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 hover:bg-white/[0.08]"
//               >
//                 Reset Pipeline
//               </button>

//               <button
//                 onClick={onClear}
//                 className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 hover:bg-white/[0.08]"
//               >
//                 Clear Chat
//               </button>
//             </div>

//             {/* Pipeline Card */}
//             {pipelineReady && (
//               <div className="mb-4 rounded-xl border border-cyan-300/20 bg-gradient-to-br from-cyan-300/10 to-violet-300/10 p-4">
//                 <p className="text-[11px] font-semibold uppercase tracking-wider text-cyan-200">
//                   Pipeline Ready
//                 </p>

//                 <div className="mt-3 grid grid-cols-2 gap-3">
//                   <div className="rounded-lg bg-black/30 px-3 py-2">
//                     <p className="text-[10px] uppercase tracking-wide text-slate-400">
//                       Model
//                     </p>
//                     <p className="text-sm font-semibold text-white">
//                       {provider.toUpperCase()}
//                     </p>
//                   </div>

//                   <div className="rounded-lg bg-black/30 px-3 py-2">
//                     <p className="text-[10px] uppercase tracking-wide text-slate-400">
//                       Messages
//                     </p>
//                     <p className="text-sm font-semibold text-white">
//                       {messagesCount}
//                     </p>
//                   </div>

//                   <div className="col-span-2 rounded-lg bg-black/30 px-3 py-2">
//                     <p className="text-[10px] uppercase tracking-wide text-slate-400">
//                       Indexed Chunks
//                     </p>
//                     <p className="text-sm font-semibold text-white">
//                       {chunkCount}
//                     </p>
//                   </div>
//                 </div>
//               </div>
//             )}

//             {/* Indexed Documents */}
//             <div className="mb-4">
//               <div className="flex items-center justify-between mb-2">
//                 <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
//                   Indexed Documents
//                 </p>
//                 <span className="text-[11px] text-slate-500">
//                   {indexedDocs.length} files
//                 </span>
//               </div>

//               <div className="space-y-2">
//                 {indexedDocs.map((doc) => (
//                   <div
//                     key={doc}
//                     className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 hover:bg-white/[0.06] transition"
//                   >
//                     <span>📄</span>
//                     <span className="text-xs text-slate-200 truncate max-w-[170px]">
//                       {doc}
//                     </span>
//                   </div>
//                 ))}
//               </div>
//             </div>

//             {/* Suggestions */}
//             <div>
//               <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
//                 Sample Questions
//               </p>

//               <div className="space-y-2">
//                 {suggestions.map((s) => (
//                   <button
//                     key={s}
//                     onClick={() => onSuggestion?.(s)}
//                     className="w-fit max-w-[200px] rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-left text-xs text-slate-200 hover:border-cyan-300/30 hover:bg-cyan-300/10"
//                   >
//                     <span className="break-words">{s}</span>
//                   </button>
//                 ))}
//               </div>
//             </div>
//           </>
//         )}

//         {/* Collapsed icons */}
//         {collapsed && (
//           <div className="mt-2 flex flex-col items-center gap-2">
//             <button
//               onClick={onLoadPipeline}
//               className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900"
//             >
//               ⬆
//             </button>
//             <button
//               onClick={onReset}
//               className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200"
//             >
//               ↺
//             </button>
//             <button
//               onClick={onClear}
//               className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200"
//             >
//               🗑
//             </button>
//           </div>
//         )}
//       </div>
//     </aside>
//   );
// }
export default function Sidebar({
  collapsed = false,
  onToggleCollapse,
  botName = "Wamo Labs Policy Assistant",
  provider,
  setProvider,
  pipelineReady,
  onLoadPipeline,
  onReset,
  onClear,
  chunkCount = "—",
  messagesCount = 0,
  indexedDocs = [],
  suggestions = [],
  onSuggestion,
  loading = false,
}) {
  return (
    <aside
      className={[
        "h-full shrink-0 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl",
        "shadow-[0_20px_70px_rgba(0,0,0,0.35)] transition-all duration-300",
        collapsed ? "w-[68px]" : "w-[280px]",
      ].join(" ")}
    >
      {/* Independent sidebar scroll */}
      <div className="h-full min-h-0 overflow-y-auto scroll-on-hover scroll-smooth p-3 md:p-4">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between gap-2">
          <div className="flex min-w-0 items-start gap-2">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-violet-400 font-bold text-slate-900">
              AI
            </div>

            {!collapsed && (
              <div className="min-w-0 pr-1">
                {/* No truncate: wraps naturally */}
                <h2 className="break-words text-[22px] font-semibold leading-6 text-slate-100">
                  {botName}
                </h2>
                <p className="mt-1 break-words text-xs leading-4 text-slate-400">
                  Modern RAG Policy Assistant
                </p>
              </div>
            )}
          </div>

          <button
            onClick={onToggleCollapse}
            className="mt-0.5 shrink-0 rounded-lg border border-white/15 bg-white/[0.04] px-2 py-1 text-xs text-slate-200 hover:bg-white/[0.08]"
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? "»" : "«"}
          </button>
        </div>

        {!collapsed ? (
          <>
            {/* Model select */}
            <div className="mb-4">
              <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">
                Choose Model
              </label>

              <div className="grid grid-cols-2 gap-2 rounded-xl border border-white/15 bg-black/30 p-1">
                {["groq", "gemini"].map((m) => {
                  const active = provider === m;
                  return (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setProvider(m)}
                      disabled={loading}
                      className={[
                        "rounded-lg px-3 py-2 text-sm font-medium transition",
                        active
                          ? "bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900 shadow"
                          : "text-slate-300 hover:bg-white/10",
                        "disabled:cursor-not-allowed disabled:opacity-60",
                      ].join(" ")}
                    >
                      {m === "groq" ? "Groq" : "Gemini"}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Action buttons */}
            <div className="mb-4 flex flex-wrap gap-2">
              {!pipelineReady && (
                <button
                  onClick={onLoadPipeline}
                  disabled={loading}
                  className="w-fit rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 px-4 py-2.5 text-sm font-semibold text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Working..." : "Load Pipeline"}
                </button>
              )}

              <button
                onClick={onReset}
                disabled={loading}
                className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-60"
              >
                Reset Pipeline
              </button>

              <button
                onClick={onClear}
                disabled={loading}
                className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-60"
              >
                Clear Chat
              </button>
            </div>

            {/* Pipeline status card */}
            {pipelineReady && (
              <div className="mb-4 rounded-xl border border-cyan-300/20 bg-gradient-to-br from-cyan-300/10 to-violet-300/10 p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-cyan-200">
                  Pipeline Ready
                </p>

                <div className="mt-3 grid grid-cols-2 gap-3">
                  <div className="rounded-lg bg-black/30 px-3 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-slate-400">
                      Model
                    </p>
                    <p className="text-sm font-semibold text-white">
                      {String(provider || "").toUpperCase()}
                    </p>
                  </div>

                  <div className="rounded-lg bg-black/30 px-3 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-slate-400">
                      Messages
                    </p>
                    <p className="text-sm font-semibold text-white">
                      {messagesCount}
                    </p>
                  </div>

                  <div className="col-span-2 rounded-lg bg-black/30 px-3 py-2">
                    <p className="text-[10px] uppercase tracking-wide text-slate-400">
                      Indexed Chunks
                    </p>
                    <p className="text-sm font-semibold text-white">
                      {chunkCount}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Indexed docs */}
            <div className="mb-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Indexed Documents
                </p>
                <span className="text-[11px] text-slate-500">
                  {indexedDocs.length} files
                </span>
              </div>

              <div className="space-y-2">
                {indexedDocs.map((doc) => (
                  <div
                    key={doc}
                    className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 transition hover:bg-white/[0.06]"
                  >
                    <span className="shrink-0">📄</span>
                    <span className="min-w-0 truncate text-xs text-slate-200">
                      {doc}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Suggestions */}
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Sample Questions
              </p>

              <div className="space-y-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => onSuggestion?.(s)}
                    className="block w-fit max-w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-left text-xs text-slate-200 transition hover:border-cyan-300/30 hover:bg-cyan-300/10"
                  >
                    <span className="break-words">{s}</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Collapsed icons */
          <div className="mt-2 flex flex-col items-center gap-2">
            {!pipelineReady && (
              <button
                onClick={onLoadPipeline}
                disabled={loading}
                className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900 disabled:opacity-60"
                title="Load Pipeline"
              >
                ⬆
              </button>
            )}
            <button
              onClick={onReset}
              disabled={loading}
              className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200 disabled:opacity-60"
              title="Reset Pipeline"
            >
              ↺
            </button>

            <button
              onClick={onClear}
              disabled={loading}
              className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200 disabled:opacity-60"
              title="Clear Chat"
            >
              🗑
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
