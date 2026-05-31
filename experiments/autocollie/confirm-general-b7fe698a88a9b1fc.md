# Confirm PASS — b7fe698a88a9b1fc on `general`

Cycle `20260530T154629-confirm-b7fe698a88a9b1fc` — 2026-05-30T15:46:29Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b7fe698a88a9b1fc` | `b5019c7c6d26e981` | `b5019c7c6d26e981` | `b5019c7c6d26e981` |
| PR AUC | 0.9988 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9988 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.6588 | 0.6175 | 0.6775 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b7fe698a88a9b1fc
```
