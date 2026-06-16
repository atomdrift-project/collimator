# Confirm PASS — c17e151ab758b601 on `filetypes/xls`

Cycle `20260616T051705-confirm-c17e151ab758b601` — 2026-06-16T05:17:05Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c17e151ab758b601` | `d9318ff027bd3599` | `d9318ff027bd3599` | `d9318ff027bd3599` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9994 |
| ROC AUC | 0.9979 | 0.9984 | 0.9983 | 0.9955 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c17e151ab758b601
```
