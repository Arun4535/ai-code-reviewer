from typing import Any, TypedDict

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - lets tests run without optional import failures.
    END = "__end__"
    StateGraph = None

from app.agents.prompts import load_prompt
from app.llm.base import ChatModel
from app.schemas.review import AgentResult, PullRequestContext, ReviewFinding, ReviewSummary


class ReviewState(TypedDict, total=False):
    context: PullRequestContext
    agent_outputs: list[AgentResult]
    findings: list[ReviewFinding]
    summary: ReviewSummary


class ReviewWorkflow:
    def __init__(self, model: ChatModel):
        self.model = model

    async def run(self, context: PullRequestContext) -> tuple[ReviewSummary, list[ReviewFinding], list[AgentResult]]:
        if StateGraph is None:
            return await self._run_sequential(context)
        graph = StateGraph(ReviewState)
        graph.add_node("pr_analysis", self._agent_node("pr_analysis", "PR Analysis Agent"))
        graph.add_node("security", self._agent_node("security", "Security Review Agent"))
        graph.add_node("performance", self._agent_node("performance", "Performance Review Agent"))
        graph.add_node("maintainability", self._agent_node("maintainability", "Maintainability Agent"))
        graph.add_node("summary", self._summary_node)
        graph.set_entry_point("pr_analysis")
        graph.add_edge("pr_analysis", "security")
        graph.add_edge("security", "performance")
        graph.add_edge("performance", "maintainability")
        graph.add_edge("maintainability", "summary")
        graph.add_edge("summary", END)
        result = await graph.compile().ainvoke({"context": context, "agent_outputs": [], "findings": []})
        return result["summary"], result["findings"], result["agent_outputs"]

    def _agent_node(self, prompt_name: str, agent_name: str):
        async def node(state: ReviewState) -> dict[str, Any]:
            result = await self.model.structured(
                system_prompt=load_prompt(prompt_name),
                user_payload={
                    "agent": agent_name,
                    "pull_request": state["context"].model_dump(mode="json"),
                    "existing_findings": [f.model_dump(mode="json") for f in state.get("findings", [])],
                },
                schema=AgentResult,
            )
            return {
                "agent_outputs": [*state.get("agent_outputs", []), result],
                "findings": [*state.get("findings", []), *result.findings],
            }

        return node

    async def _summary_node(self, state: ReviewState) -> dict[str, Any]:
        summary = await self.model.structured(
            system_prompt=load_prompt("summary"),
            user_payload={
                "pull_request": state["context"].model_dump(mode="json"),
                "agent_outputs": [a.model_dump(mode="json") for a in state.get("agent_outputs", [])],
                "findings": [f.model_dump(mode="json") for f in state.get("findings", [])],
            },
            schema=ReviewSummary,
        )
        return {"summary": summary}

    async def _run_sequential(self, context: PullRequestContext) -> tuple[ReviewSummary, list[ReviewFinding], list[AgentResult]]:
        state: ReviewState = {"context": context, "agent_outputs": [], "findings": []}
        for prompt_name, agent_name in [
            ("pr_analysis", "PR Analysis Agent"),
            ("security", "Security Review Agent"),
            ("performance", "Performance Review Agent"),
            ("maintainability", "Maintainability Agent"),
        ]:
            state.update(await self._agent_node(prompt_name, agent_name)(state))
        state.update(await self._summary_node(state))
        return state["summary"], state["findings"], state["agent_outputs"]
