"""DuckDB setup and SQL tools for the NYC taxi SQL agent homework."""

from __future__ import annotations

import os
import urllib.request
from typing import Any

import duckdb

DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
PARQUET_FILE = "yellow_tripdata_2024-01.parquet"
DB_FILE = "taxi.db"

# Global connection used by setup_database().
con = duckdb.connect(DB_FILE)


def setup_database() -> int:
    """Download the parquet file and load it into DuckDB."""
    if not os.path.exists(PARQUET_FILE):
        print(f"Downloading {DATA_URL}...")
        urllib.request.urlretrieve(DATA_URL, PARQUET_FILE)

    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS trips AS
        SELECT * FROM '{PARQUET_FILE}'
        """
    )

    count = con.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
    print(f"Loaded {count} rows")
    return count


class SQLTools:
    """Tools the agent can use to inspect and query the taxi database."""

    def __init__(self, db_path: str = DB_FILE) -> None:
        self.db_path = db_path

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(self.db_path)

    def get_schema(self) -> str:
        """Return the trips table schema with column names and types."""
        with self._connect() as conn:
            rows = conn.execute("DESCRIBE trips").fetchall()

        lines = ["column_name | column_type"]
        lines.extend(f"{row[0]} | {row[1]}" for row in rows)
        return "\n".join(lines)

    def run_sql(self, query: str) -> str:
        """Execute SQL and return column headers plus up to 50 rows as text."""
        safe_query = query.strip().rstrip(";")
        limited_query = f"SELECT * FROM ({safe_query}) AS agent_query LIMIT 50"

        with self._connect() as conn:
            result = conn.execute(limited_query)
            columns = [desc[0] for desc in result.description]
            rows: list[tuple[Any, ...]] = result.fetchall()

        output = [" | ".join(columns)]
        output.extend(" | ".join(str(value) for value in row) for row in rows)
        return "\n".join(output)


if __name__ == "__main__":
    setup_database()
