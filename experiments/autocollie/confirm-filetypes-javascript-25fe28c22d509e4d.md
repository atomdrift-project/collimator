# Confirm PASS — 25fe28c22d509e4d on `filetypes/javascript`

Cycle `20260525T161856-confirm-25fe28c22d509e4d` — 2026-05-25T16:18:56Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `25fe28c22d509e4d` | `a2c3d5a3977d36c7` | `a2c3d5a3977d36c7` | `a2c3d5a3977d36c7` |
| PR AUC | 0.9993 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.8439 | 0.8715 | 0.8914 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=25fe28c22d509e4d
```
