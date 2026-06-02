export type Severity = "Critical" | "High" | "Medium" | "Low";

export type ReviewFinding = {
  file_path: string;
  line_start?: number | null;
  line_end?: number | null;
  category: string;
  severity: Severity;
  confidence: number;
  title: string;
  explanation: string;
  recommended_fix: string;
  agent: string;
};

export type AgentOutput = {
  agent: string;
  intent?: string | null;
  findings: ReviewFinding[];
  notes: string[];
};

export type ReviewResponse = {
  id: number;
  repository_url: string;
  pull_request_url: string;
  summary: {
    verdict: string;
    risk_score: number;
    executive_summary: string;
    prioritized_actions: string[];
  };
  findings: ReviewFinding[];
  agent_outputs: AgentOutput[];
};

export type SystemSettings = {
  llm_provider: string;
  default_model: string;
  vector_store: string;
  database: string;
};
