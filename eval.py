import json
import os
import sys
import time

import pandas as pd

from agent import run_agent
from eval_cases import build_cases
from scoring import numeric_match, refusal_match, text_match
from tools import DataTools

RESULTS_FILE = "eval_results.json"


def score(case, answer):
    if case["kind"] == "num":
        return numeric_match(answer, case["expected"], case.get("tol", 0))
    if case["kind"] == "text":
        return text_match(answer, case["expected"])
    return refusal_match(answer)


def evaluate(cases, tools, client, results=None, sleep=0, save=None, max_consecutive_failures=3):
    results = {} if results is None else results
    failures = 0
    for case in cases:
        if case["q"] in results:
            continue  # already done in a previous run
        try:
            out = run_agent(case["q"], tools, client)
        except RuntimeError as e:
            failures += 1
            print(f"skipped (API error): {case['q']} -> {e}")
            if failures >= max_consecutive_failures:
                print("Too many consecutive API errors, stopping. Run again later to resume.")
                break
            if sleep:
                time.sleep(sleep)
            continue
        failures = 0
        results[case["q"]] = {
            "ok": bool(score(case, out["answer"])),
            "answer": out["answer"],
            "expected": case.get("expected"),
            "sql": [s["args"].get("query") for s in out["steps"] if s["tool"] == "run_sql"],
        }
        if save:
            save(results)
        if sleep:
            time.sleep(sleep)
    return results


def summarize(cases, results):
    done = [c for c in cases if c["q"] in results]
    correct = sum(results[c["q"]]["ok"] for c in done)
    print(f"\nAccuracy: {correct}/{len(done)}")
    for c in done:
        r = results[c["q"]]
        print(("PASS" if r["ok"] else "FAIL"), "|", c["q"])
        if not r["ok"]:
            print("     expected:", c.get("expected", "(refusal)"))
            print("     answer  :", r["answer"][:150].replace("\n", " "))
    if len(done) < len(cases):
        print(f"\n{len(cases) - len(done)} question(s) not run yet. Run again later to resume.")


if __name__ == "__main__":
    from llm import GeminiClient

    cases = build_cases(pd.read_csv("titanic.csv"))
    results = {}
    if os.path.exists(RESULTS_FILE) and "--fresh" not in sys.argv:
        with open(RESULTS_FILE, encoding="utf-8") as f:
            results = json.load(f)

    def save(data):
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    tools = DataTools("titanic.csv", table="passengers")
    try:
        evaluate(cases, tools, GeminiClient(), results, sleep=8, save=save)
    except RuntimeError as e:
        print("Stopped early:", e)
    summarize(cases, results)
