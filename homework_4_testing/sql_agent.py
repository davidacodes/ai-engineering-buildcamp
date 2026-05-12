"""PydanticAI SQL agent for querying the NYC taxi DuckDB database."""

from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from sql_tools import SQLTools, setup_database


class SQLResult(BaseModel):
    """Structured output returned by the SQL agent."""

    sql_query: str = Field(description="The SQL query used to answer the question")
    result_text: str = Field(description="A clear text summary of the SQL result")
    row_count: int = Field(description="The number of result rows returned or summarized")


sql_tools = SQLTools()

agent = Agent(
    "openai:gpt-4o-mini",
    output_type=SQLResult,
    tools=[sql_tools.get_schema, sql_tools.run_sql],
    instructions="""
You are a careful SQL assistant that answers questions about the DuckDB table named trips.

Rules:
1. Always call get_schema first before writing SQL.
2. After reading the schema, write a DuckDB-compatible SQL query.
3. Call run_sql with the query.
4. Return the exact SQL query you used in sql_query.
5. Return a concise answer in result_text, including the important numeric result.
6. Return row_count as the number of rows in the final result, usually 1 for aggregate questions.
""".strip(),
)


async def ask_agent(question: str) -> SQLResult:
    """Ask the agent a question and return its structured output."""
    result = await agent.run(question)
    return result.output


async def main() -> None:
    setup_database()
    question = "What's the average trip distance for rides with 2 passengers?"
    answer = await ask_agent(question)
    print(answer.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
