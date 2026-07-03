# Confirm PASS — 5f43252a3ea79247 on `filetypes/python-bytecode`

Cycle `20260703T002022-confirm-5f43252a3ea79247` — 2026-07-03T00:20:22Z

PR_AUC held across 3 seeds (orig 0.9961)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5f43252a3ea79247` | `e79bed7631f86927` | `e79bed7631f86927` | `e79bed7631f86927` |
| PR AUC | 0.9961 | 0.9953 | 0.9960 | 0.9959 |
| ROC AUC | 0.9977 | 0.9979 | 0.9984 | 0.9983 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5f43252a3ea79247
```
