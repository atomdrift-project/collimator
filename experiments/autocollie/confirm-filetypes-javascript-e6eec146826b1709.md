# Confirm PASS — e6eec146826b1709 on `filetypes/javascript`

Cycle `20260608T103041-confirm-e6eec146826b1709` — 2026-06-08T10:30:41Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e6eec146826b1709` | `808a8770961d4023` | `808a8770961d4023` | `808a8770961d4023` |
| PR AUC | 0.9976 | 0.9992 | 0.9992 | 0.9992 |
| ROC AUC | 0.9971 | 0.9988 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e6eec146826b1709
```
