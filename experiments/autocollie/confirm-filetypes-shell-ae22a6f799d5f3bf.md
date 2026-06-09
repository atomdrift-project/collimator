# Confirm PASS — ae22a6f799d5f3bf on `filetypes/shell`

Cycle `20260609T075800-confirm-ae22a6f799d5f3bf` — 2026-06-09T07:58:00Z

PR_AUC held across 3 seeds (orig 0.9980)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ae22a6f799d5f3bf` | `487ffb8536b848fc` | `487ffb8536b848fc` | `487ffb8536b848fc` |
| PR AUC | 0.9980 | 0.9979 | 0.9978 | 0.9980 |
| ROC AUC | 0.9981 | 0.9980 | 0.9979 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ae22a6f799d5f3bf
```
