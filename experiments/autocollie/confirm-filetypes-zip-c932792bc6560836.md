# Confirm PASS — c932792bc6560836 on `filetypes/zip`

Cycle `20260527T014002-confirm-c932792bc6560836` — 2026-05-27T01:40:02Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c932792bc6560836` | `615bc550ba60ece6` | `615bc550ba60ece6` | `615bc550ba60ece6` |
| PR AUC | 0.9999 | 0.9997 | 0.9998 | 0.9997 |
| ROC AUC | 0.9971 | 0.9958 | 0.9960 | 0.9956 |
| Recall@3FPM | — | 0.6552 | 0.6880 | 0.6253 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c932792bc6560836
```
