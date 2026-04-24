// export default function Sidebar({
//   collapsed = false,
//   onToggleCollapse,
//   botName = "Wamo Labs Policy Assistant",
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
//   loading = false,
// }) {
//   return (
//     <aside
//       className={[
//         "h-full shrink-0 rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl",
//         "shadow-[0_20px_70px_rgba(0,0,0,0.35)] transition-all duration-300",
//         collapsed ? "w-[68px]" : "w-[280px]",
//       ].join(" ")}
//     >
//       {/* Independent sidebar scroll */}
//       <div className="h-full min-h-0 overflow-y-auto scroll-on-hover scroll-smooth p-3 md:p-4">
//         {/* Header */}
//         <div className="mb-4 flex items-start justify-between gap-2">
//           <div className="flex min-w-0 items-start gap-2">
//             <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-violet-400 font-bold text-slate-900">
//               AI
//             </div>

//             {!collapsed && (
//               <div className="min-w-0 pr-1">
//                 {/* No truncate: wraps naturally */}
//                 <h2 className="break-words text-[22px] font-semibold leading-6 text-slate-100">
//                   {botName}
//                 </h2>
//                 <p className="mt-1 break-words text-xs leading-4 text-slate-400">
//                   Modern RAG Policy Assistant
//                 </p>
//               </div>
//             )}
//           </div>

//           <button
//             onClick={onToggleCollapse}
//             className="mt-0.5 shrink-0 rounded-lg border border-white/15 bg-white/[0.04] px-2 py-1 text-xs text-slate-200 hover:bg-white/[0.08]"
//             title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
//           >
//             {collapsed ? "»" : "«"}
//           </button>
//         </div>

//         {!collapsed ? (
//           <>
            
//             {/* Model Badge - Groq only */}
// <div className="mb-4">
//   <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-400">
//     Model
//   </label>

//   <div className="rounded-xl border border-cyan-300/30 bg-gradient-to-r from-cyan-300/10 to-violet-300/10 px-4 py-3">
//     <p className="text-sm font-semibold text-cyan-200">Groq</p>
//   </div>
// </div>

//             {/* Action buttons */}
//             <div className="mb-4 flex flex-wrap gap-2">
//               {!pipelineReady && (
//                 <button
//                   onClick={onLoadPipeline}
//                   disabled={loading}
//                   className="w-fit rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 px-4 py-2.5 text-sm font-semibold text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
//                 >
//                   {loading ? "Working..." : "Load Pipeline"}
//                 </button>
//               )}

//               <button
//                 onClick={onReset}
//                 disabled={loading}
//                 className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-60"
//               >
//                 Reset Pipeline
//               </button>

//               <button
//                 onClick={onClear}
//                 disabled={loading}
//                 className="w-fit rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 transition hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-60"
//               >
//                 Clear Chat
//               </button>
//             </div>

//             {/* Pipeline status card */}
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
//                       {String(provider || "").toUpperCase()}
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

//             {/* Indexed docs */}
//             <div className="mb-4">
//               <div className="mb-2 flex items-center justify-between">
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
//                     className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 transition hover:bg-white/[0.06]"
//                   >
//                     <span className="shrink-0">📄</span>
//                     <span className="min-w-0 truncate text-xs text-slate-200">
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
//                     className="block w-fit max-w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-left text-xs text-slate-200 transition hover:border-cyan-300/30 hover:bg-cyan-300/10"
//                   >
//                     <span className="break-words">{s}</span>
//                   </button>
//                 ))}
//               </div>
//             </div>
//           </>
//         ) : (
//           /* Collapsed icons */
//           <div className="mt-2 flex flex-col items-center gap-2">
//             {!pipelineReady && (
//               <button
//                 onClick={onLoadPipeline}
//                 disabled={loading}
//                 className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-r from-cyan-300 to-violet-300 text-slate-900 disabled:opacity-60"
//                 title="Load Pipeline"
//               >
//                 ⬆
//               </button>
//             )}
//             <button
//               onClick={onReset}
//               disabled={loading}
//               className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200 disabled:opacity-60"
//               title="Reset Pipeline"
//             >
//               ↺
//             </button>

//             <button
//               onClick={onClear}
//               disabled={loading}
//               className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200 disabled:opacity-60"
//               title="Clear Chat"
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
  onClear,
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
      <div className="h-full min-h-0 overflow-y-auto scroll-on-hover scroll-smooth p-3 md:p-4">

        {/* ================= COLLAPSED MODE ================= */}
        {collapsed ? (
          <div className="flex flex-col items-center gap-3">

            {/* Logo */}
            <div className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-violet-400 font-bold text-slate-900">
              W
            </div>

            {/* Toggle */}
            <button
              onClick={onToggleCollapse}
              className="rounded-lg border border-white/15 bg-white/[0.04] px-2 py-1 text-xs text-slate-200 hover:bg-white/[0.08]"
              title="Expand sidebar"
            >
              »
            </button>

            {/* Minimal quick action */}
            <button
              onClick={() => onClear?.()}
              className="mt-2 grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/[0.04] text-slate-200"
              title="Clear Chat"
            >
              🗑
            </button>
          </div>
        ) : (
          <>
            {/* ================= HEADER ================= */}
            <div className="mb-5 flex items-start justify-between gap-2">
              <div className="flex min-w-0 items-start gap-2">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-cyan-300 to-violet-400 font-bold text-slate-900">
                  W
                </div>

                <div className="min-w-0">
                  <h2 className="text-[20px] font-semibold text-slate-100 leading-6">
                    {botName}
                  </h2>
                  <p className="mt-1 text-xs text-slate-400">
                    Your HR & Policy knowledge assistant
                  </p>
                </div>
              </div>

              <button
                onClick={onToggleCollapse}
                className="shrink-0 rounded-lg border border-white/15 bg-white/[0.04] px-2 py-1 text-xs text-slate-200 hover:bg-white/[0.08]"
                title="Collapse sidebar"
              >
                «
              </button>
            </div>

            {/* ================= CAPABILITIES ================= */}
            <div className="mb-4 rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                What I can help with
              </p>

              <ul className="space-y-1 text-xs text-slate-300">
                <li>• Leave & HR policies</li>
                <li>• Employment contracts</li>
                <li>• Workplace rules</li>
                <li>• Company procedures</li>
              </ul>
            </div>

            {/* ================= QUICK ACTIONS ================= */}
            <div className="mb-4">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Quick Actions
              </p>

              <button
                onClick={() => onClear?.()}
                disabled={loading}
                className="rounded-xl border border-white/15 bg-white/[0.04] px-3 py-2 text-xs text-slate-200 hover:bg-white/[0.08] disabled:opacity-50"
              >
                Clear Chat
              </button>
            </div>

            {/* ================= KNOWLEDGE BASE ================= */}
            <div className="mb-4">
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Knowledge Base
                </p>
                <span className="text-[11px] text-slate-500">
                  {indexedDocs.length} files
                </span>
              </div>

              <div className="space-y-2">
                {indexedDocs.map((doc) => (
                  <div
                    key={doc}
                    className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2"
                  >
                    <span>📄</span>
                    <span className="truncate text-xs text-slate-200">
                      {doc}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* ================= SUGGESTIONS ================= */}
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Try asking
              </p>

              <div className="space-y-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => onSuggestion?.(s)}
                    className="w-full rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2 text-left text-xs text-slate-200 hover:bg-cyan-300/10 hover:border-cyan-300/30"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}