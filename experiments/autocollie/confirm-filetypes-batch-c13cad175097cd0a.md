# Confirm PASS — c13cad175097cd0a on `filetypes/batch`

Cycle `20260526T222747-confirm-c13cad175097cd0a` — 2026-05-26T22:27:47Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c13cad175097cd0a` | `eae9ed681fde7886` | `eae9ed681fde7886` | `eae9ed681fde7886` |
| PR AUC | 0.9997 | 0.9995 | 0.9996 | 0.9995 |
| ROC AUC | 0.9980 | 0.9957 | 0.9961 | 0.9955 |
| Recall@3FPM | — | 0.9504 | 0.9739 | 0.9739 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c13cad175097cd0a
```
