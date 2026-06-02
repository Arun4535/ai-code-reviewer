"use client";

import { useMemo, useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, Filter, Search, SlidersHorizontal } from "lucide-react";
import { reviewQueue, workspaceFindings, type WorkspaceFinding } from "@/lib/workspace-fixtures";
import type { Severity } from "@/lib/types";

const severityOrder: Severity[] = ["Critical", "High", "Medium", "Low"];
const statuses = ["All", "Open", "Triaged", "Fixed", "Ignored"] as const;

export function ReviewWorkspace() {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<(typeof statuses)[number]>("All");
  const [minimumConfidence, setMinimumConfidence] = useState(70);

  const filteredFindings = useMemo(() => {
    return workspaceFindings
      .filter((finding) => status === "All" || finding.status === status)
      .filter((finding) => finding.confidence >= minimumConfidence)
      .filter((finding) => {
        const haystack = `${finding.title} ${finding.file} ${finding.category} ${finding.owner}`.toLowerCase();
        return haystack.includes(query.toLowerCase());
      })
      .sort((a, b) => severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity) || b.confidence - a.confidence);
  }, [minimumConfidence, query, status]);

  const openCount = workspaceFindings.filter((finding) => finding.status === "Open").length;
  const highRiskCount = workspaceFindings.filter((finding) => finding.severity === "Critical" || finding.severity === "High").length;
  const averageConfidence = Math.round(workspaceFindings.reduce((total, finding) => total + finding.confidence, 0) / workspaceFindings.length);

  return (
    <section className="space-y-5">
      <div className="flex flex-col justify-between gap-3 border-b border-line pb-4 md:flex-row md:items-end">
        <div>
          <h2 className="text-xl font-semibold">Review Workspace</h2>
          <p className="mt-1 text-sm text-slate-600">Monitor active reviews, triage findings, and keep high-confidence issues moving.</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <Activity size={16} />
          Live queue preview
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <ScoreCard icon={AlertTriangle} label="High risk findings" value={String(highRiskCount)} tone="text-red-600" />
        <ScoreCard icon={Filter} label="Open findings" value={String(openCount)} tone="text-amber-600" />
        <ScoreCard icon={CheckCircle2} label="Avg confidence" value={`${averageConfidence}%`} tone="text-emerald-600" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_380px]">
        <div className="rounded-lg border border-line bg-white p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            <label className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search findings, files, owners" className="w-full rounded-md border border-line py-2 pl-9 pr-3 text-sm outline-none focus:border-brand" />
            </label>
            <select value={status} onChange={(event) => setStatus(event.target.value as (typeof statuses)[number])} className="rounded-md border border-line px-3 py-2 text-sm outline-none focus:border-brand">
              {statuses.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>
            <label className="flex min-w-56 items-center gap-2 text-sm text-slate-600">
              <SlidersHorizontal size={16} />
              <input type="range" min={50} max={100} value={minimumConfidence} onChange={(event) => setMinimumConfidence(Number(event.target.value))} className="w-full" />
              {minimumConfidence}%
            </label>
          </div>

          <div className="mt-4 overflow-hidden rounded-md border border-line">
            <table className="w-full border-collapse text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Finding</th>
                  <th className="px-3 py-2">Severity</th>
                  <th className="px-3 py-2">Owner</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2 text-right">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {filteredFindings.map((finding) => (
                  <FindingRow key={finding.id} finding={finding} />
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <aside className="rounded-lg border border-line bg-white p-4">
          <h3 className="font-semibold">Active Review Queue</h3>
          <div className="mt-4 space-y-3">
            {reviewQueue.map((item) => (
              <div key={item.id} className="rounded-md border border-slate-100 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{item.repository}</div>
                    <div className="text-xs text-slate-500">{item.pullRequest} updated {item.updated}</div>
                  </div>
                  <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-700">{item.status}</span>
                </div>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <QueueMetric label="Risk" value={item.risk} suffix="/100" />
                  <QueueMetric label="Findings" value={item.findings} />
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </section>
  );
}

function ScoreCard({ icon: Icon, label, value, tone }: { icon: React.ElementType; label: string; value: string; tone: string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-slate-600">{label}</div>
        <Icon className={tone} size={18} />
      </div>
      <div className="mt-3 text-2xl font-semibold">{value}</div>
    </div>
  );
}

function FindingRow({ finding }: { finding: WorkspaceFinding }) {
  return (
    <tr className="border-t border-line">
      <td className="px-3 py-3">
        <div className="font-medium">{finding.title}</div>
        <div className="mt-1 text-xs text-slate-500">{finding.file} · {finding.category} · {finding.ageHours}h old</div>
      </td>
      <td className="px-3 py-3">
        <span className="rounded-full bg-slate-100 px-2 py-1 text-xs">{finding.severity}</span>
      </td>
      <td className="px-3 py-3 text-slate-600">{finding.owner}</td>
      <td className="px-3 py-3 text-slate-600">{finding.status}</td>
      <td className="px-3 py-3 text-right font-medium">{finding.confidence}%</td>
    </tr>
  );
}

function QueueMetric({ label, value, suffix = "" }: { label: string; value: number; suffix?: string }) {
  return (
    <div className="rounded-md bg-slate-50 px-2 py-2">
      <div className="text-slate-500">{label}</div>
      <div className="mt-1 font-semibold">{value}{suffix}</div>
    </div>
  );
}
