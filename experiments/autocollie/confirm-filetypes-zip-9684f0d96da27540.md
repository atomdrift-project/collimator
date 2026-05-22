# Confirm PASS — 9684f0d96da27540 on `filetypes/zip`

Cycle `20260522T170407-confirm-9684f0d96da27540` — 2026-05-22T17:04:07Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9684f0d96da27540` | `06e2493c6559d096` | `06e2493c6559d096` | `06e2493c6559d096` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9963 | 0.9966 | 0.9963 | 0.9961 |
| Recall@3FPM | — | 0.6941 | 0.7374 | 0.6900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9684f0d96da27540
```
