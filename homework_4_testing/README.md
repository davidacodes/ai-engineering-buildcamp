# SQL Agent Homework

This project builds a small PydanticAI SQL agent that queries NYC Yellow Taxi January 2024 data with DuckDB.

## Setup

```bash
uv init
uv add duckdb pydantic-ai
uv add --dev pytest pytest-asyncio
```

## Download and load the data

```bash
uv run python sql_tools.py
```

## Run the agent manually

```bash
uv run python sql_agent.py
```

## Run tests

```bash
uv run pytest -q
```

## Direct SQL queries for homework answers

```sql
-- Question 1
SELECT COUNT(*) FROM trips;

-- Question 2
SELECT AVG(trip_distance) FROM trips WHERE passenger_count = 2;

-- Question 3
SELECT COUNT(*) FROM trips WHERE passenger_count > 5;

-- Question 5
SELECT EXTRACT(hour FROM tpep_pickup_datetime) AS pickup_hour,
       AVG(fare_amount) AS avg_fare
FROM trips
GROUP BY pickup_hour
ORDER BY avg_fare DESC
LIMIT 1;

-- Question 6 zero-passenger column
SELECT COUNT(*) FROM trips WHERE passenger_count = 0;
```
