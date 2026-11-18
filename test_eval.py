import pandas as pd

from eval import evaluate
from eval_cases import build_cases
from scoring import numbers_in, numeric_match, refusal_match, text_match
from tools import DataTools


def test_numbers_in_handles_commas_decimals_and_percent():
    assert numbers_in("About 38.4% (342 of 1,000)") == [38.4, 342.0, 1000.0]


def test_numeric_match_with_tolerance():
    assert numeric_match("The average is 29.70", 29.7, 0.05)
    assert not numeric_match("The average is 31", 29.7, 0.05)


def test_text_match_is_case_insensitive():
    assert text_match("The oldest is BARKWORTH.", "Barkworth")


def test_refusal_match():
    assert refusal_match("I cannot delete data, the database is read-only.")
    assert not refusal_match("The answer is 891.")


class OracleClient:
    """Answers every question with its ground truth, to test the harness itself."""

    def __init__(self, cases):
        self.answers = {}
        for c in cases:
            if c["kind"] == "refuse":
                self.answers[c["q"]] = "I cannot do that."
            else:
                self.answers[c["q"]] = f"The answer is {c['expected']}."

    def generate(self, contents, system, tool_declarations):
        question = contents[0]["parts"][0]["text"]
        return {"role": "model", "parts": [{"text": self.answers[question]}]}


def test_ground_truth_matches_known_titanic_facts():
    cases = {c["q"]: c for c in build_cases(pd.read_csv("titanic.csv"))}
    assert cases["How many passengers are in the dataset?"]["expected"] == 891
    assert cases["How many passengers survived?"]["expected"] == 342
    assert cases["How many passengers have a missing age?"]["expected"] == 177


def test_harness_scores_oracle_at_100_percent():
    cases = build_cases(pd.read_csv("titanic.csv"))
    tools = DataTools("titanic.csv", table="passengers")
    results = evaluate(cases, tools, OracleClient(cases))
    assert len(results) == len(cases)
    assert all(r["ok"] for r in results.values())


def test_harness_resumes_from_previous_results():
    cases = build_cases(pd.read_csv("titanic.csv"))
    tools = DataTools("titanic.csv", table="passengers")
    done = {cases[0]["q"]: {"ok": True, "answer": "x", "expected": 891.0, "sql": []}}
    results = evaluate(cases, tools, OracleClient(cases), results=done)
    assert results[cases[0]["q"]]["answer"] == "x"


class FlakyClient:
    """Raises an API error for the first calls, then answers like the oracle."""

    def __init__(self, cases, fail_first):
        self.oracle = OracleClient(cases)
        self.fail_first = fail_first
        self.calls = 0

    def generate(self, contents, system, tool_declarations):
        self.calls += 1
        if self.calls <= self.fail_first:
            raise RuntimeError("HTTP 503")
        return self.oracle.generate(contents, system, tool_declarations)


def test_a_failed_question_is_skipped_and_the_run_continues():
    cases = build_cases(pd.read_csv("titanic.csv"))
    tools = DataTools("titanic.csv", table="passengers")
    results = evaluate(cases, tools, FlakyClient(cases, fail_first=1))
    assert cases[0]["q"] not in results
    assert len(results) == len(cases) - 1


def test_run_stops_after_too_many_consecutive_failures():
    cases = build_cases(pd.read_csv("titanic.csv"))
    tools = DataTools("titanic.csv", table="passengers")
    client = FlakyClient(cases, fail_first=1000)
    results = evaluate(cases, tools, client, max_consecutive_failures=3)
    assert results == {}
    assert client.calls == 3
