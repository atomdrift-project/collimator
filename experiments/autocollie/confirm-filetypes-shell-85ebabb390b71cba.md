# Confirm PASS — 85ebabb390b71cba on `filetypes/shell`

Cycle `20260706T060856-confirm-85ebabb390b71cba` — 2026-07-06T06:08:56Z

PR_AUC held across 3 seeds (orig 0.9902)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `85ebabb390b71cba` | `5528fe457b0ba1f1` | `5528fe457b0ba1f1` | `5528fe457b0ba1f1` |
| PR AUC | 0.9902 | 0.9909 | 0.9911 | 0.9907 |
| ROC AUC | 0.9937 | 0.9940 | 0.9944 | 0.9942 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=85ebabb390b71cba
```
