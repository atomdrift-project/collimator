# Confirm PASS — a0fca704de2f4c30 on `filetypes/c`

Cycle `20260601T150318-confirm-a0fca704de2f4c30` — 2026-06-01T15:03:18Z

PR_AUC held across 3 seeds (orig 0.9915)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a0fca704de2f4c30` | `739a14fe4458383a` | `739a14fe4458383a` | `739a14fe4458383a` |
| PR AUC | 0.9915 | 0.9885 | 0.9892 | 0.9882 |
| ROC AUC | 0.9955 | 0.9946 | 0.9949 | 0.9942 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a0fca704de2f4c30
```
