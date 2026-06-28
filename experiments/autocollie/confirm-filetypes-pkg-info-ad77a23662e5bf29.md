# Confirm PASS — ad77a23662e5bf29 on `filetypes/pkg-info`

Cycle `20260628T022406-confirm-ad77a23662e5bf29` — 2026-06-28T02:24:06Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ad77a23662e5bf29` | `c31107f8d230818d` | `c31107f8d230818d` | `c31107f8d230818d` |
| PR AUC | 1.0000 | 0.9998 | 0.9999 | 1.0000 |
| ROC AUC | 0.9985 | 0.9962 | 0.9983 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ad77a23662e5bf29
```
