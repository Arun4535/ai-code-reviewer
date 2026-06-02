import type { Severity } from "@/lib/types";

export type WorkspaceFinding = {
  id: number;
  title: string;
  file: string;
  severity: Severity;
  category: string;
  owner: string;
  confidence: number;
  status: "Open" | "Triaged" | "Fixed" | "Ignored";
  ageHours: number;
};

export type ReviewQueueItem = {
  id: number;
  repository: string;
  pullRequest: string;
  risk: number;
  findings: number;
  status: "Queued" | "Running" | "Needs attention" | "Complete";
  updated: string;
};

export const workspaceFindings: WorkspaceFinding[] = [
  { id: 1, title: "Token is persisted in browser storage", file: "frontend/lib/api.ts", severity: "High", category: "Security", owner: "security", confidence: 91, status: "Open", ageHours: 4 },
  { id: 2, title: "Repository metrics endpoint performs unbounded scan", file: "backend/app/services/reporting_service.py", severity: "Medium", category: "Performance", owner: "backend", confidence: 84, status: "Triaged", ageHours: 8 },
  { id: 3, title: "Follow-up chat error path hides API failures", file: "frontend/components/review-details.tsx", severity: "Medium", category: "Reliability", owner: "frontend", confidence: 77, status: "Open", ageHours: 13 },
  { id: 4, title: "Review workflow lacks timeout budget per agent", file: "backend/app/agents/workflow.py", severity: "High", category: "Architecture", owner: "platform", confidence: 88, status: "Open", ageHours: 18 },
  { id: 5, title: "Generated summaries are stored without schema version", file: "backend/app/models/entities.py", severity: "Low", category: "Maintainability", owner: "backend", confidence: 71, status: "Ignored", ageHours: 28 },
  { id: 6, title: "Settings page has no unavailable-state fallback", file: "frontend/app/settings/page.tsx", severity: "Low", category: "UX", owner: "frontend", confidence: 69, status: "Fixed", ageHours: 35 },
  { id: 7, title: "GitHub patch parsing drops renamed files", file: "backend/app/services/github_service.py", severity: "Medium", category: "Correctness", owner: "integrations", confidence: 82, status: "Triaged", ageHours: 41 },
  { id: 8, title: "Feedback ratings accept out-of-policy values", file: "backend/app/schemas/feedback.py", severity: "High", category: "Data Quality", owner: "backend", confidence: 86, status: "Open", ageHours: 52 }
];

export const reviewQueue: ReviewQueueItem[] = [
  { id: 201, repository: "Arun4535/ai-code-reviewer", pullRequest: "#18", risk: 88, findings: 14, status: "Needs attention", updated: "3m ago" },
  { id: 202, repository: "acme/payments-api", pullRequest: "#412", risk: 72, findings: 9, status: "Running", updated: "7m ago" },
  { id: 203, repository: "acme/mobile-shell", pullRequest: "#105", risk: 35, findings: 3, status: "Complete", updated: "16m ago" },
  { id: 204, repository: "acme/data-pipeline", pullRequest: "#77", risk: 64, findings: 6, status: "Queued", updated: "22m ago" },
  { id: 205, repository: "acme/internal-tools", pullRequest: "#231", risk: 48, findings: 5, status: "Complete", updated: "37m ago" }
];
