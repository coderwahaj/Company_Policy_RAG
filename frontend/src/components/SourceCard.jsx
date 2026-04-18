export default function SourceCard({ source, onOpen, onCopy }) {
  const label =
    typeof source === "string"
      ? source
      : source?.document || source?.file || source?.name || JSON.stringify(source);

  return (
    <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] p-2">
      <div className="min-w-0 flex-1">
        <p className="truncate text-xs text-slate-200">{label}</p>
      </div>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onCopy?.(label)}
          className="rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
        >
          Copy
        </button>
        <button
          onClick={() => onOpen?.(source)}
          className="rounded-md border border-white/15 bg-white/[0.04] px-2 py-1 text-[11px] text-slate-200 hover:bg-white/[0.08]"
        >
          Open
        </button>
      </div>
    </div>
  );
}