# API Documentation

Base URL: `/api/v1`

## Create Review

`POST /reviews`

```json
{
  "repository_url": "https://github.com/owner/repo",
  "pull_request_url": "https://github.com/owner/repo/pull/123"
}
```

Returns a persisted review with executive summary, findings, and agent outputs.

## Get Review

`GET /reviews/{review_id}`

Returns the same review payload stored in PostgreSQL.

## Ask Follow-up

`POST /reviews/{review_id}/ask`

```json
{
  "question": "What is the security risk?"
}
```

Answers using the stored review summary and finding context.

## Feedback

`POST /feedback`

```json
{
  "review_id": 1,
  "finding_id": 5,
  "rating": 1,
  "comment": "Useful finding"
}
```

## Repository Metrics

`GET /reports/repositories/metrics?repository=owner/repo`

Returns aggregated review statistics for a repository, including total reviews,
finding counts, severity counts, category confidence, agent confidence, and the
highest-risk review IDs.

## Review Export

`GET /reports/reviews/{review_id}/export`

Returns a compact, shareable export payload for one review with the summary,
prioritized actions, pull request URL, and flattened finding details.
