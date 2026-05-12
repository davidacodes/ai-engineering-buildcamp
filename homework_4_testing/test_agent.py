"""Tests for the SQL agent homework."""

from __future__ import annotations

import duckdb
import pytest

from judge import assert_criteria
from sql_agent import agent
from sql_tools import setup_database
from utils import collect_tools


@pytest.fixture(scope="session", autouse=True)
def database_ready() -> None:
    """Create taxi.db once before the test suite runs."""
    setup_database()


def scalar(sql: str):
    """Run a direct DuckDB query to get a reliable expected answer."""
    with duckdb.connect("taxi.db") as conn:
        return conn.execute(sql).fetchone()[0]


@pytest.mark.asyncio
async def test_agent_counts_trips_with_more_than_five_passengers():
    expected = scalar("SELECT COUNT(*) FROM trips WHERE passenger_count > 5")

    result = await agent.run("How many trips had more than 5 passengers?")
    output = result.output

    assert isinstance(output.sql_query, str)
    assert output.sql_query.strip() != ""
    assert str(expected) in output.result_text.replace(",", "")


@pytest.mark.asyncio
async def test_agent_gets_schema_before_running_sql():
    result = await agent.run("What is the most common payment type?")
    tool_names = collect_tools(result.all_messages())

    assert tool_names[0] == "get_schema"
    assert "run_sql" in tool_names


@pytest.mark.asyncio
async def test_llm_judge_highest_average_fare_hour():
    question = "Which hour of the day has the highest average fare amount?"
    result = await agent.run(question)

    await assert_criteria(
        question=question,
        answer=result.output,
        criteria=[
            "the SQL query correctly calculates average fare by hour of day",
            "the result identifies a specific hour as having the highest average fare",
            "the result includes the actual average fare amount",
        ],
    )


@pytest.mark.asyncio
async def test_average_tip_for_credit_card_payments():
    expected = scalar("SELECT AVG(tip_amount) FROM trips WHERE payment_type = 1")

    result = await agent.run("What is the average tip amount for credit card payments?")
    output = result.output
    tool_names = collect_tools(result.all_messages())

    assert tool_names[0] == "get_schema"
    assert "run_sql" in tool_names
    assert "tip_amount" in output.sql_query
    assert "payment_type" in output.sql_query
    assert f"{expected:.2f}" in output.result_text or str(round(expected, 2)) in output.result_text


@pytest.mark.asyncio
async def test_pickup_location_with_most_trips():
    expected = scalar(
        """
        SELECT PULocationID
        FROM trips
        GROUP BY PULocationID
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """
    )

    result = await agent.run("Which pickup location (PULocationID) has the most trips?")
    output = result.output

    assert "PULocationID" in output.sql_query or "pulocationid" in output.sql_query.lower()
    assert "COUNT" in output.sql_query.upper()
    assert str(expected) in output.result_text


@pytest.mark.asyncio
async def test_average_fare_for_trips_longer_than_ten_miles():
    expected = scalar("SELECT AVG(fare_amount) FROM trips WHERE trip_distance > 10")

    result = await agent.run("What is the average fare for trips longer than 10 miles?")
    output = result.output

    assert "fare_amount" in output.sql_query
    assert "trip_distance" in output.sql_query
    assert f"{expected:.2f}" in output.result_text or str(round(expected, 2)) in output.result_text


@pytest.mark.asyncio
async def test_zero_passenger_trips_filters_on_passenger_count():
    expected = scalar("SELECT COUNT(*) FROM trips WHERE passenger_count = 0")

    result = await agent.run("How many trips had zero passengers recorded?")
    output = result.output

    assert "passenger_count" in output.sql_query
    assert str(expected) in output.result_text.replace(",", "")


@pytest.mark.asyncio
async def test_busiest_day_of_week_for_taxi_trips():
    expected = scalar(
        """
        SELECT strftime(tpep_pickup_datetime, '%A') AS day_name
        FROM trips
        GROUP BY day_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """
    )

    result = await agent.run("What is the busiest day of the week for taxi trips?")
    output = result.output

    assert "tpep_pickup_datetime" in output.sql_query
    assert "COUNT" in output.sql_query.upper()
    assert str(expected) in output.result_text
