# Deployment Guide

## Supabase PostgreSQL

Create a free Supabase project and copy the pooled PostgreSQL connection string into `DATABASE_URL`.

## Render Backend

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `DATABASE_URL`, `GROQ_API_KEY` or `ANTHROPIC_API_KEY`, `LLM_PROVIDER`, `GITHUB_TOKEN`, `CORS_ORIGINS`

For Claude:

```text
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<your claude key>
ANTHROPIC_MODEL=claude-sonnet-4-5
```

Run migrations during release with:

```bash
alembic upgrade head
```

## Vercel Frontend

- Root directory: `frontend`
- Environment variable: `NEXT_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com/api/v1`

Set `CORS_ORIGINS` on Render to the Vercel deployment URL.
