# PR Review Optimization

This document explains the production issues in the original AI PR reviewer and describes the improvements made to support large pull requests reliably.

## Problem Summary

The original implementation suffered from several bottlenecks:

- Entire `PullRequestContext` was sent to every agent and summary call.
- The same diff content was reviewed repeatedly by multiple agents.
- Large diffs were truncated instead of chunked, causing lost context.
- GitHub file retrieval failed for PRs with more than 100 files.
- Ollama performed repeated `/api/tags` model discovery on every request.
- Large PRs timed out or returned incomplete reviews.
- Claude and Groq API usage was excessive because multiple full-context calls were made.

## Goals

The refactor prioritized:

- Lowest token consumption
- Lowest LLM latency and API cost
- Reliable large PR support
- Compatibility with Ollama and Groq
- Minimal changes to existing architecture

## Key Improvements

### 1. GitHub Pagination Fix

The GitHub file fetch now paginates through `/repos/{owner}/{repo}/pulls/{number}/files` until all pages are loaded.

Result:

- supports PRs with 100+ changed files
- avoids silently dropping files beyond the first page
- preserves the existing max review file limit while retrieving the complete file list

### 2. Chunk-based Review Instead of Truncation

Large diffs are now broken into reviewable chunks rather than cut off mid-stream.

Chunking is based on:

- Git diff hunk boundaries (`@@ ... @@`)
- semantic function/class boundaries when present
- maximum chunk size of 300 lines

This preserves code context while ensuring each prompt remains bounded.

### 3. File Prioritization

Changed files are scored and ordered so higher-risk areas are reviewed first.

Priority signals include:

- authentication/authorization
- database or payment code
- security-sensitive paths
- tests and docs are deprioritized

### 4. Unified Reviewer Model

The old multi-agent pipeline was collapsed into a single `Unified PR Review Agent`.

Now each chunk is reviewed once with a unified prompt that returns structured findings for:

- Bug Risk
- Security
- Performance
- Maintainability
- Readability
- Testing Coverage
- Architecture Concerns

This change reduces the number of LLM calls dramatically.

### 5. Concurrent Chunk Processing

Chunk reviews execute concurrently with a limit of 5 parallel LLM calls.

This reduces wall-clock review time while protecting local resources.

### 6. Ollama Optimization

Ollama model discovery is now cached per `OllamaChatModel` instance.

Result:

- no repeated `/api/tags` calls per chunk
- faster end-to-end inference for local models

### 7. Local Summary Aggregation

Final review summaries are synthesized locally from aggregated findings instead of requiring an additional LLM summary pass.

This preserves response format while eliminating a redundant review call.

## Files Changed

- `backend/app/core/config.py`
- `backend/app/services/github_service.py`
- `backend/app/agents/chunking.py`
- `backend/app/agents/workflow.py`
- `backend/app/prompts/unified_review.md`
- `backend/app/llm/ollama.py`
- `backend/tests/test_github_service.py`
- `backend/tests/test_workflow.py`
- `backend/tests/test_chunking.py`

## How the New Flow Works

1. Fetch PR metadata and all changed files from GitHub using pagination.
2. Prioritize changed files by risk and limit to the configured file review budget.
3. Split large patches into chunks by diff hunk boundaries and function/class proximity.
4. Send each chunk to the unified prompt exactly once.
5. Aggregate findings and build a final review summary locally.
6. Store results and return structured review output.

## Running Tests

From `backend`:

```bash
cd "d:\AI PR Reviewer\backend"
"d:/AI PR Reviewer/.venv/Scripts/python.exe" -m pytest -q -o addopts= tests/test_github_service.py tests/test_workflow.py tests/test_chunking.py
```

## Outcomes

- Reduced repeated context across LLM calls
- Reduced total model calls per review
- Better support for large PRs and multi-page GitHub file fetch
- More stable, predictable review behavior for change-heavy pull requests
