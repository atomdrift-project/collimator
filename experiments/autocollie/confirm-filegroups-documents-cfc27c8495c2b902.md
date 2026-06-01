# Confirm PASS — cfc27c8495c2b902 on `filegroups/documents`

Cycle `20260601T142435-confirm-cfc27c8495c2b902` — 2026-06-01T14:24:35Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cfc27c8495c2b902` | `116a84cacfd55fb0` | `116a84cacfd55fb0` | `116a84cacfd55fb0` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cfc27c8495c2b902
```
