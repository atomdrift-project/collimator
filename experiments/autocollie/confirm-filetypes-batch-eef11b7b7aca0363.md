# Confirm PASS — eef11b7b7aca0363 on `filetypes/batch`

Cycle `20260525T202848-confirm-eef11b7b7aca0363` — 2026-05-25T20:28:48Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eef11b7b7aca0363` | `b2ce54256769e342` | `b2ce54256769e342` | `b2ce54256769e342` |
| PR AUC | 0.9998 | 0.9995 | 0.9996 | 0.9995 |
| ROC AUC | 0.9983 | 0.9957 | 0.9961 | 0.9955 |
| Recall@3FPM | — | 0.9504 | 0.9739 | 0.9739 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eef11b7b7aca0363
```
