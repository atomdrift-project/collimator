# Confirm PASS — 5142712411855745 on `filetypes/python-bytecode`

Cycle `20260603T155422-confirm-5142712411855745` — 2026-06-03T15:54:22Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5142712411855745` | `190d312df14f6067` | `190d312df14f6067` | `190d312df14f6067` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9997 |
| ROC AUC | 0.9996 | 0.9995 | 0.9995 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5142712411855745
```
