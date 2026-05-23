# Confirm PASS — 963342a82ee48369 on `filegroups/documents`

Cycle `20260523T174937-confirm-963342a82ee48369` — 2026-05-23T17:49:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `963342a82ee48369` | `d3120a4dd6bc9f6b` | `d3120a4dd6bc9f6b` | `d3120a4dd6bc9f6b` |
| PR AUC | 1.0000 | 0.9986 | 0.9986 | 0.9986 |
| ROC AUC | 0.9986 | 0.8989 | 0.8989 | 0.8989 |
| Recall@3FPM | — | 0.5075 | 0.5075 | 0.5075 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=963342a82ee48369
```
