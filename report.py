import json

import pandas as pd

from eval_cases import build_cases

cases = build_cases(pd.read_csv("titanic.csv"))
with open("eval_results.json", encoding="utf-8") as f:
    results = json.load(f)

done = [c for c in cases if c["q"] in results]
correct = sum(results[c["q"]]["ok"] for c in done)

lines = [
    "# Evaluation results",
    "",
    f"Accuracy: **{correct}/{len(done)}** questions answered correctly "
    f"({len(cases) - len(done)} not run yet).",
    "",
    "| # | Question | Expected | Result |",
    "|---|---|---|---|",
]
for i, c in enumerate(done, start=1):
    r = results[c["q"]]
    expected = c.get("expected", "refuse")
    lines.append(f"| {i} | {c['q']} | {expected} | {'PASS' if r['ok'] else 'FAIL'} |")

failed = [c for c in done if not results[c["q"]]["ok"]]
if failed:
    lines += ["", "## Failures", ""]
    for c in failed:
        r = results[c["q"]]
        lines.append(f"- **{c['q']}**: expected {c.get('expected', 'refusal')}; got: {r['answer'][:200]!r}")

lines += [
    "",
    "Ground truth is computed with pandas from the same CSV. "
    "Scoring checks whether any number in the answer matches (within a tolerance), so it is approximate.",
]

with open("EVAL.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
