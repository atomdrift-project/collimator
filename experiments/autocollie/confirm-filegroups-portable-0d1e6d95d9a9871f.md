# Confirm PASS — 0d1e6d95d9a9871f on `filegroups/portable`

Cycle `20260527T012426-confirm-0d1e6d95d9a9871f` — 2026-05-27T01:24:26Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0d1e6d95d9a9871f` | `a12f4ac8b071d378` | `a12f4ac8b071d378` | `a12f4ac8b071d378` |
| PR AUC | 0.9968 | 0.9960 | 0.9948 | 0.9957 |
| ROC AUC | 0.9992 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.8200 | 0.7000 | 0.8667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0d1e6d95d9a9871f
```
