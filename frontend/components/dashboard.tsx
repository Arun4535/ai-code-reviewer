"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GitPullRequest, Loader2, ShieldCheck, Zap } from "lucide-react";
import { createReview } from "@/lib/api";
import { ReviewWorkspace } from "@/components/review-workspace";

export function Dashboard() {
  const router = useRouter();
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [pullRequestUrl, setPullRequestUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError("");
    setLoading(true);
    try {
      const review = await createReview(repositoryUrl, pullRequestUrl);
      router.push(`/reviews/${review.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Review failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col justify-between gap-4 border-b border-line pb-5 md:flex-row md:items-end">
        <div>
          <h1 className="text-2xl font-semibold">Pull Request Review</h1>
          <p className="mt-1 text-sm text-slate-600">Submit a GitHub PR and inspect model findings, agent traces, and follow-up answers.</p>
        </div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          <Metric icon={ShieldCheck} label="Security" value="OWASP" />
          <Metric icon={Zap} label="Model" value="Groq" />
          <Metric icon={GitPullRequest} label="Workflow" value="LangGraph" />
        </div>
      </header>

      <section className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <div className="rounded-lg border border-line bg-white p-5">
          <div className="grid gap-4">
            <label className="text-sm font-medium">
              Repository URL
              <input suppressHydrationWarning value={repositoryUrl} onChange={(event) => setRepositoryUrl(event.target.value)} placeholder="https://github.com/owner/repo" className="mt-2 w-full rounded-md border border-line px-3 py-2 outline-none focus:border-brand" />
            </label>
            <label className="text-sm font-medium">
              Pull Request URL
              <input suppressHydrationWarning value={pullRequestUrl} onChange={(event) => setPullRequestUrl(event.target.value)} placeholder="https://github.com/owner/repo/pull/123" className="mt-2 w-full rounded-md border border-line px-3 py-2 outline-none focus:border-brand" />
            </label>
            {error ? <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
            <button onClick={submit} disabled={loading || !repositoryUrl || !pullRequestUrl} className="inline-flex w-fit items-center gap-2 rounded-md bg-brand px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50">
              {loading ? <Loader2 className="animate-spin" size={16} /> : <GitPullRequest size={16} />}
              Review PR
            </button>
          </div>
        </div>
        <div className="rounded-lg border border-line bg-white p-5">
          <h2 className="font-semibold">Review Coverage</h2>
          <div className="mt-4 space-y-3 text-sm text-slate-700">
            {["Bug Risk", "Security", "Performance", "Maintainability", "Readability", "Testing Coverage", "Architecture Concerns"].map((item) => (
              <div key={item} className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span>{item}</span>
                <span className="font-medium text-brand">Enabled</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <ReviewWorkspace />
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-white px-3 py-2">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon size={15} />
        {label}
      </div>
      <div className="mt-1 font-semibold">{value}</div>
    </div>
  );
}
