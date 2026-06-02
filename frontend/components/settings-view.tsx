import { Settings } from "lucide-react";
import type { SystemSettings } from "@/lib/types";

export function SettingsView({ settings }: { settings: SystemSettings }) {
  return (
    <div className="space-y-4">
      <header className="border-b border-line pb-4">
        <h1 className="flex items-center gap-2 text-2xl font-semibold"><Settings size={22} /> Settings</h1>
      </header>
      <section className="rounded-lg border border-line bg-white p-5">
        <div className="grid gap-4 md:grid-cols-2">
          <ReadonlyField label="LLM Provider" value={formatProvider(settings.llm_provider)} />
          <ReadonlyField label="Default Model" value={settings.default_model} />
          <ReadonlyField label="Vector Store" value={settings.vector_store} />
          <ReadonlyField label="Database" value={settings.database} />
        </div>
      </section>
    </div>
  );
}

function formatProvider(provider: string) {
  if (provider.toLowerCase() === "anthropic") {
    return "Anthropic";
  }
  if (provider.toLowerCase() === "claude") {
    return "Claude";
  }
  return provider.charAt(0).toUpperCase() + provider.slice(1);
}

function ReadonlyField({ label, value }: { label: string; value: string }) {
  return (
    <label className="text-sm font-medium">
      {label}
      <input suppressHydrationWarning readOnly value={value} className="mt-2 w-full rounded-md border border-line bg-slate-50 px-3 py-2 text-slate-700" />
    </label>
  );
}
