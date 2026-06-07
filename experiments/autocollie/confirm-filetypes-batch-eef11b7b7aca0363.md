# Confirm PASS — eef11b7b7aca0363 on `filetypes/batch`

Cycle `20260606T203607-confirm-eef11b7b7aca0363` — 2026-06-06T20:36:07Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eef11b7b7aca0363` | `73ac840846a92651` | `73ac840846a92651` | `73ac840846a92651` |
| PR AUC | 0.9998 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9983 | 0.9954 | 0.9956 | 0.9955 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eef11b7b7aca0363
```
