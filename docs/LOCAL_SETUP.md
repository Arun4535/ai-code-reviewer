# Local Setup Guide

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker compose up postgres
```

Backend:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

To use your Claude API key, set this in `backend/.env`:

```text
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<your claude key>
ANTHROPIC_MODEL=claude-sonnet-4-5
```
