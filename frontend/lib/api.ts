import type { ReviewResponse, SystemSettings } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const REVIEW_TIMEOUT_MS = 15 * 60 * 1000;

export async function createReview(repositoryUrl: string, pullRequestUrl: string): Promise<ReviewResponse> {
  try {
    const response = await fetch(`${API_BASE}/reviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repository_url: repositoryUrl, pull_request_url: pullRequestUrl }),
      signal: AbortSignal.timeout(REVIEW_TIMEOUT_MS)
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === "TimeoutError") {
      throw new Error("The review is taking longer than 15 minutes. Try a smaller PR or use a smaller local Ollama model.");
    }
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new Error(`Could not reach the backend at ${API_BASE}. Make sure FastAPI is running and CORS points to this frontend URL.`);
    }
    throw error;
  }
}

export async function getReview(reviewId: number): Promise<ReviewResponse> {
  const response = await fetch(`${API_BASE}/reviews/${reviewId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function askReview(reviewId: number, question: string): Promise<{ answer: string; citations: string[] }> {
  const response = await fetch(`${API_BASE}/reviews/${reviewId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function getSystemSettings(): Promise<SystemSettings> {
  const response = await fetch(`${API_BASE}/system/settings`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function getWorkflowTestPrStatus(): Promise<{ workflow_test_pr: string; branch: string }> {
  const response = await fetch(`${API_BASE}/test-pr`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}
