# Confirm PASS — 115e7a1d7794dc29 on `filetypes/javascript`

Cycle `20260526T064211-confirm-115e7a1d7794dc29` — 2026-05-26T06:42:11Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `115e7a1d7794dc29` | `4253297a4ee5f040` | `4253297a4ee5f040` | `4253297a4ee5f040` |
| PR AUC | 0.9993 | 0.9996 | 0.9996 | 0.9996 |
| ROC AUC | 0.9989 | 0.9994 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8856 | 0.8642 | 0.8468 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=115e7a1d7794dc29
```
