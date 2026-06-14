# Confirm PASS — cf3c27ff19cfd4f1 on `filetypes/php`

Cycle `20260614T221800-confirm-cf3c27ff19cfd4f1` — 2026-06-14T22:18:00Z

PR_AUC held across 3 seeds (orig 0.9943)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cf3c27ff19cfd4f1` | `91f134960e5812c5` | `91f134960e5812c5` | `91f134960e5812c5` |
| PR AUC | 0.9943 | 0.9950 | 0.9940 | 0.9941 |
| ROC AUC | 0.9973 | 0.9974 | 0.9969 | 0.9967 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cf3c27ff19cfd4f1
```
