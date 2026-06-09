# Confirm PASS — 4b743c29e16f4184 on `filetypes/go`

Cycle `20260609T163506-confirm-4b743c29e16f4184` — 2026-06-09T16:35:06Z

PR_AUC held across 3 seeds (orig 0.9431)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4b743c29e16f4184` | `b097a5fafd9a79cf` | `b097a5fafd9a79cf` | `b097a5fafd9a79cf` |
| PR AUC | 0.9431 | 0.9415 | 0.9433 | 0.9475 |
| ROC AUC | 0.9849 | 0.9843 | 0.9844 | 0.9860 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4b743c29e16f4184
```
