# Confirm PASS — 81ce7bf814cc33e4 on `filetypes/javascript`

Cycle `20260601T203944-confirm-81ce7bf814cc33e4` — 2026-06-01T20:39:44Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `81ce7bf814cc33e4` | `9288ec9c2b514f64` | `9288ec9c2b514f64` | `9288ec9c2b514f64` |
| PR AUC | 0.9988 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9984 | 0.9990 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=81ce7bf814cc33e4
```
