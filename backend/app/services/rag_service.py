from dataclasses import dataclass


@dataclass
class RetrievedStandard:
    source: str
    text: str


class ReviewKnowledgeBase:
    """Small RAG facade; Chroma-backed ingestion can be enabled without changing agents."""

    def retrieve(self, query: str, limit: int = 4) -> list[RetrievedStandard]:
        standards = [
            RetrievedStandard("OWASP Top 10", "Validate authorization on every privileged operation."),
            RetrievedStandard("FastAPI Best Practices", "Avoid blocking calls inside async endpoints."),
            RetrievedStandard("Clean Code Principles", "Prefer cohesive functions with explicit error handling."),
            RetrievedStandard("Python Best Practices", "Keep secrets out of source code and logs."),
        ]
        query_lower = query.lower()
        ranked = [item for item in standards if any(word in item.text.lower() for word in query_lower.split())]
        return (ranked or standards)[:limit]
