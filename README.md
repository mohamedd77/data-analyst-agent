# Data Analyst Agent (in progress)

An LLM agent that answers questions about a CSV file by writing and running SQL.

## Status
- Done: safe, read-only SQL tool layer over a CSV (`tools.py`) with tests (`test_tools.py`).
- Next: LLM agent loop with tool calling, FastAPI endpoint, evaluation on questions with known answers.

## Safety
- The query tool only accepts a single SELECT (or WITH) statement.
- The database is opened in read-only mode (`PRAGMA query_only = ON`), so writes fail even if a query slips through the text checks.
- Results are capped at 50 rows.
- Known limitation: a `;` inside a string literal is rejected.

## Run the tests'@ | Set-Content -Encoding utf8 README.md
