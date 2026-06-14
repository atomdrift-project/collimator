# Confirm PASS — 48ae66e380562440 on `filegroups/documents`

Cycle `20260613T013926-confirm-48ae66e380562440` — 2026-06-13T01:39:26Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `48ae66e380562440` | `9bd8441c86251310` | `9bd8441c86251310` | `9bd8441c86251310` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9986 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=48ae66e380562440
```
