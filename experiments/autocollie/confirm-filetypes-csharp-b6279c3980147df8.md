# Confirm PASS — b6279c3980147df8 on `filetypes/csharp`

Cycle `20260703T061219-confirm-b6279c3980147df8` — 2026-07-03T06:12:19Z

PR_AUC held across 3 seeds (orig 0.4921)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b6279c3980147df8` | `a8a846a94a59ff1e` | `a8a846a94a59ff1e` | `a8a846a94a59ff1e` |
| PR AUC | 0.4921 | 0.4809 | 0.4709 | 0.5163 |
| ROC AUC | 0.8597 | 0.8473 | 0.8737 | 0.8814 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b6279c3980147df8
```
