# Confirm PASS — a2fb16fca5e1b4c8 on `filetypes/pkg-info`

Cycle `20260527T064000-confirm-a2fb16fca5e1b4c8` — 2026-05-27T06:40:00Z

PR_AUC held across 3 seeds (orig 0.9767)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2fb16fca5e1b4c8` | `249ea962d81d2934` | `249ea962d81d2934` | `249ea962d81d2934` |
| PR AUC | 0.9767 | 0.9941 | 0.9941 | 0.9941 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a2fb16fca5e1b4c8
```
