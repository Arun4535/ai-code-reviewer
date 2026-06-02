# Architecture

The system is a monorepo with a FastAPI backend, Next.js frontend, PostgreSQL persistence, and a LangGraph agent workflow.

```mermaid
flowchart TB
  Client["Next.js Review UI"] --> Routes["FastAPI Routes"]
  Routes --> Service["Review Service"]
  Service --> GitHub["GitHub API"]
  Service --> Workflow["LangGraph Workflow"]
  Workflow --> Agents["PR, Security, Performance, Maintainability, Summary Agents"]
  Agents --> LLM["Groq Llama 3.3 70B"]
  Service --> Repo["SQLAlchemy Repositories"]
  Repo --> Postgres["PostgreSQL"]
  Service --> RAG["ChromaDB-ready Knowledge Base"]
```

Clean architecture boundaries keep transport, business logic, persistence, model calls, and prompts independently testable.
