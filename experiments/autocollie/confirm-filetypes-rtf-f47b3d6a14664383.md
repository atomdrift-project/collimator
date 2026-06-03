# Confirm PASS — f47b3d6a14664383 on `filetypes/rtf`

Cycle `20260603T155251-confirm-f47b3d6a14664383` — 2026-06-03T15:52:51Z

PR_AUC held across 3 seeds (orig 0.9946)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f47b3d6a14664383` | `67be8692da558f25` | `67be8692da558f25` | `67be8692da558f25` |
| PR AUC | 0.9946 | 0.9946 | 0.9946 | 0.9946 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f47b3d6a14664383
```
