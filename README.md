# Data Analyst Agent

An LLM agent that answers natural-language questions about a CSV file by writing and running SQL.
It uses Gemini function calling, a read-only SQLite sandbox, automated tests, and an evaluation on
questions with known answers.

## How it works
```
question -> agent loop -> Gemini (function calling)
                 |               |
                 |      tool call: describe_table / run_sql
                 v
        DataTools: SQLite in memory, read-only
                 |
        tool result -> back to the model -> final answer
```
1. The CSV is loaded into an in-memory SQLite table.
2. The model can call `describe_table` (schema and sample rows) and `run_sql` (one SELECT query).
3. Tool results go back to the model until it gives a final answer, or the step limit is reached.

## Safety
- Only a single SELECT (or WITH) statement is accepted.
- The database runs with `PRAGMA query_only = ON`, so writes fail even if a query slips past the text checks.
- Results are capped at 50 rows.
- The agent has a maximum number of steps, and the API client retries with backoff on rate limits and timeouts.

## Run
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set GEMINI_API_KEY=your_key
set GEMINI_MODEL=gemini-3.6-flash
python ask.py "What percentage of passengers survived?"
```
Use `$env:GEMINI_API_KEY="your_key"` in PowerShell. Never commit the key.

## Tests and CI
```
python -m pytest -q
```
The tests cover the SQL tools (including blocked writes), the agent loop with a scripted fake model
(no network needed), and the evaluation harness itself. GitHub Actions runs them on every push.

## Evaluation
`python eval.py` asks 16 questions about the Titanic dataset. The expected answers are computed
with pandas from the same CSV, and two questions check that the agent refuses (no data to answer,
or a destructive request). Results are saved after every question so a run can resume after a rate limit.
`python report.py` writes the latest results to [EVAL.md](EVAL.md).

## Limitations
- Scoring is approximate: an answer counts as correct if any number in it matches the expected value.
- The question set is small (16) and uses one dataset.
- A `;` inside a string literal in a query is rejected.
- One table only; no charts.
- Free-tier API limits can interrupt long evaluation runs.

## Next steps
- A FastAPI endpoint, more datasets, and multi-table questions.
