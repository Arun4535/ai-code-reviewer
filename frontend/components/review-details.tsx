"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, MessageSquare, Send, SlidersHorizontal } from "lucide-react";
import { askReview, getReview } from "@/lib/api";
import type { ReviewResponse, Severity } from "@/lib/types";

const severities: Array<Severity | "All"> = ["All", "Critical", "High", "Medium", "Low"];

export function ReviewDetails({ reviewId }: { reviewId: number }) {
  const [review, setReview] = useState<ReviewResponse | null>(null);
  const [severity, setSeverity] = useState<Severity | "All">("All");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; text: string }>>([]);

  useEffect(() => {
    getReview(reviewId).then(setReview).catch((error) => setMessages([{ role: "assistant", text: error.message }]));
  }, [reviewId]);

  const filtered = useMemo(() => {
    if (!review) return [];
    return severity === "All" ? review.findings : review.findings.filter((finding) => finding.severity === severity);
  }, [review, severity]);

  async function ask() {
    if (!question.trim()) return;
    const current = question;
    setQuestion("");
    setMessages((items) => [...items, { role: "user", text: current }]);
    const answer = await askReview(reviewId, current);
    setMessages((items) => [...items, { role: "assistant", text: answer.answer }]);
  }

  if (!review) {
    return <div className="rounded-lg border border-line bg-white p-5 text-sm text-slate-600">Loading review...</div>;
  }

  return (
    <div className="space-y-6">
      <header className="border-b border-line pb-5">
        <div className="text-sm text-slate-500">{review.repository_url}</div>
        <h1 className="mt-1 text-2xl font-semibold">{review.summary.verdict}</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-700">{review.summary.executive_summary}</p>
      </header>

      <section className="grid gap-4 md:grid-cols-4">
        <Score label="Risk Score" value={`${review.summary.risk_score}/100`} />
        <Score label="Findings" value={String(review.findings.length)} />
        <Score label="Agents" value={String(review.agent_outputs.length)} />
        <Score label="PR" value={`#${reviewId}`} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <SlidersHorizontal size={18} />
            {severities.map((item) => (
              <button key={item} onClick={() => setSeverity(item)} className={`rounded-md border px-3 py-1.5 text-sm ${severity === item ? "border-brand bg-brand text-white" : "border-line bg-white text-slate-700"}`}>
                {item}
              </button>
            ))}
          </div>
          {filtered.map((finding, index) => (
            <article key={`${finding.file_path}-${index}`} className="rounded-lg border border-line bg-white p-4">
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded bg-slate-100 px-2 py-1 font-medium">{finding.severity}</span>
                <span className="rounded bg-cyan-50 px-2 py-1 text-brand">{finding.category}</span>
                <span className="text-slate-500">{finding.confidence}% confidence</span>
              </div>
              <h2 className="mt-3 font-semibold">{finding.title}</h2>
              <div className="mt-1 text-sm text-slate-500">{finding.file_path}{finding.line_start ? `:${finding.line_start}` : ""}</div>
              <p className="mt-3 text-sm text-slate-700">{finding.explanation}</p>
              <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{finding.recommended_fix}</div>
            </article>
          ))}
        </div>

        <aside className="space-y-4">
          <div className="rounded-lg border border-line bg-white p-4">
            <div className="mb-3 flex items-center gap-2 font-semibold"><Bot size={18} /> Agent Outputs</div>
            <div className="space-y-3">
              {review.agent_outputs.map((agent) => (
                <details key={agent.agent} className="rounded-md border border-line p-3">
                  <summary className="cursor-pointer text-sm font-medium">{agent.agent}</summary>
                  <p className="mt-2 text-sm text-slate-600">{agent.intent ?? "No intent provided."}</p>
                  {agent.notes.map((note) => <div key={note} className="mt-2 text-xs text-slate-500">{note}</div>)}
                </details>
              ))}
            </div>
          </div>
          <div className="rounded-lg border border-line bg-white p-4">
            <div className="mb-3 flex items-center gap-2 font-semibold"><MessageSquare size={18} /> Follow-up</div>
            <div className="h-64 space-y-2 overflow-y-auto rounded-md border border-line bg-slate-50 p-3">
              {messages.map((message, index) => (
                <div key={index} className={`text-sm ${message.role === "user" ? "text-ink" : "text-brand"}`}>{message.text}</div>
              ))}
            </div>
            <div className="mt-3 flex gap-2">
              <input suppressHydrationWarning value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about a finding" className="min-w-0 flex-1 rounded-md border border-line px-3 py-2 text-sm outline-none focus:border-brand" />
              <button onClick={ask} className="rounded-md bg-brand p-2 text-white" aria-label="Send"><Send size={18} /></button>
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}

function Score({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value}</div>
    </div>
  );
}
