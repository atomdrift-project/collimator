# Confirm PASS — 45b17bb8d7a30625 on `filetypes/kotlin`

Cycle `20260715T192338-confirm-45b17bb8d7a30625` — 2026-07-15T19:23:38Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `45b17bb8d7a30625` | `abd03ef619f892a6` | `abd03ef619f892a6` | `abd03ef619f892a6` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9988 | 0.9993 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=45b17bb8d7a30625
```
