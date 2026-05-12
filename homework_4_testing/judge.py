"""Simple LLM judge helpers for evaluating agent output."""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_ai import Agent


class JudgeResult(BaseModel):
    """Structured result from the LLM judge."""

    passes: bool = Field(description="Whether the response satisfies all criteria")
    reasoning: str = Field(description="Brief explanation of the judgment")


judge_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=JudgeResult,
    instructions="""
You are evaluating whether a SQL agent answer satisfies specific criteria.
Be strict but fair. The answer must satisfy every criterion to pass.
""".strip(),
)


async def evaluate_agent_performance(question: str, answer: object, criteria: list[str]) -> JudgeResult:
    """Use an LLM judge to evaluate an agent answer against natural language criteria."""
    prompt = f"""
Question:
{question}

Agent answer:
{answer}

Criteria:
{chr(10).join(f'- {item}' for item in criteria)}

Does the answer satisfy all criteria?
""".strip()

    result = await judge_agent.run(prompt)
    return result.output


async def assert_criteria(question: str, answer: object, criteria: list[str]) -> None:
    """Assert that the LLM judge says the answer passes all criteria."""
    judgment = await evaluate_agent_performance(question, answer, criteria)
    assert judgment.passes, judgment.reasoning
