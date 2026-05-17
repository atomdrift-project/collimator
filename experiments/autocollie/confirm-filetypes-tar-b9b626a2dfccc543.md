# Confirm PASS — b9b626a2dfccc543 on `filetypes/tar`

Cycle `20260515T064000-confirm-b9b626a2dfccc543` — 2026-05-15T06:40:00Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b9b626a2dfccc543` | `9800d79fbe956d65` | `9800d79fbe956d65` | `9800d79fbe956d65` |
| PR AUC | 1.0000 | 0.9997 | 1.0000 | 0.9991 |
| ROC AUC | 1.0000 | 0.9968 | 1.0000 | 0.9899 |
| Recall@3FPM | — | 0.9793 | 1.0000 | 0.9793 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b9b626a2dfccc543
```
