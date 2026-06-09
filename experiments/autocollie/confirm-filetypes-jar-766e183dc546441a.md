# Confirm PASS — 766e183dc546441a on `filetypes/jar`

Cycle `20260609T105907-confirm-766e183dc546441a` — 2026-06-09T10:59:07Z

PR_AUC held across 3 seeds (orig 0.9942)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `766e183dc546441a` | `faa6e2db72506f18` | `faa6e2db72506f18` | `faa6e2db72506f18` |
| PR AUC | 0.9942 | 0.9934 | 0.9921 | 0.9923 |
| ROC AUC | 0.9871 | 0.9854 | 0.9826 | 0.9831 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=766e183dc546441a
```
