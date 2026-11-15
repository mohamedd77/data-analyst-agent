# Evaluation results

Accuracy: **3/3** questions answered correctly (13 not run yet).

| # | Question | Expected | Result |
|---|---|---|---|
| 1 | How many passengers are in the dataset? | 891.0 | PASS |
| 2 | How many passengers survived? | 342.0 | PASS |
| 3 | What is the average age of all passengers, rounded to 1 decimal? | 29.7 | PASS |

Ground truth is computed with pandas from the same CSV. Scoring checks whether any number in the answer matches (within a tolerance), so it is approximate.
