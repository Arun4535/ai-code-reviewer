# Interview Discussion Guide

## Architecture Decisions

The backend follows clean architecture with FastAPI routes, services, repositories, SQLAlchemy models, Pydantic schemas, agent orchestration, and prompt files separated by concern.

The LLM layer uses a provider interface, so Groq and Claude can be swapped through configuration without changing agent logic.

## LangGraph Usage

The graph carries review state through PR analysis, security, performance, maintainability, and summary nodes. Each node emits structured `AgentResult` objects.

## Prompt Design

Prompts are stored in `backend/app/prompts` and are not hardcoded into service logic. Each prompt is scoped to one review skill.

## Evaluation Strategy

Every run stores the prompt name, model, input, output, and optional human feedback. This creates the basis for prompt regression testing and quality dashboards.

## Scaling Approach

Large PRs can be chunked by file and reviewed in parallel agent branches. Long-running reviews can move to a queue with persisted job status.

## Cost Optimization

Cache reviews by commit SHA, skip generated files, retrieve only relevant standards, and route simple follow-up questions to cheaper models.

## Security Considerations

Secrets are environment-based, CORS is explicit, inputs are validated, and security review prompts target OWASP, credential leakage, access control, injection, and unsafe logging.
