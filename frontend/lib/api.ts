import type { ReviewResponse, SystemSettings } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function createReview(repositoryUrl: string, pullRequestUrl: string): Promise<ReviewResponse> {
  const response = await fetch(`${API_BASE}/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repository_url: repositoryUrl, pull_request_url: pullRequestUrl })
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
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
