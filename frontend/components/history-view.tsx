import { History } from "lucide-react";

export function HistoryView() {
  return (
    <div className="rounded-lg border border-line bg-white p-6">
      <div className="flex items-center gap-2 text-xl font-semibold"><History size={20} /> Review History</div>
      <p className="mt-3 text-sm text-slate-600">Persisted reviews are available through the backend API. Add authentication to scope this list per user in production.</p>
    </div>
  );
}
