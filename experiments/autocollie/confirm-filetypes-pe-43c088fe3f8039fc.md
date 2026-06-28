# Confirm PASS — 43c088fe3f8039fc on `filetypes/pe`

Cycle `20260628T155720-confirm-43c088fe3f8039fc` — 2026-06-28T15:57:20Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `43c088fe3f8039fc` | `008f4727b6e1152c` | `008f4727b6e1152c` | `008f4727b6e1152c` |
| PR AUC | 0.9988 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=43c088fe3f8039fc
```
