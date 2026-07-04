# Confirm PASS — 3818c4f8f221f75d on `filetypes/shell`

Cycle `20260704T081005-confirm-3818c4f8f221f75d` — 2026-07-04T08:10:05Z

PR_AUC held across 3 seeds (orig 0.9963)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3818c4f8f221f75d` | `5fab59648f0cc4c3` | `5fab59648f0cc4c3` | `5fab59648f0cc4c3` |
| PR AUC | 0.9963 | 0.9943 | 0.9938 | 0.9942 |
| ROC AUC | 0.9976 | 0.9956 | 0.9953 | 0.9955 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3818c4f8f221f75d
```
