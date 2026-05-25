# Confirm PASS — b7fe698a88a9b1fc on `general`

Cycle `20260524T032935-confirm-b7fe698a88a9b1fc` — 2026-05-24T03:29:35Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b7fe698a88a9b1fc` | `3167587689286a69` | `3167587689286a69` | `3167587689286a69` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9988 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.6622 | 0.6418 | 0.6761 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b7fe698a88a9b1fc
```
