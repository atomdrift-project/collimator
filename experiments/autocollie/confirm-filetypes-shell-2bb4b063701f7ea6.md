# Confirm PASS — 2bb4b063701f7ea6 on `filetypes/shell`

Cycle `20260606T150856-confirm-2bb4b063701f7ea6` — 2026-06-06T15:08:56Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2bb4b063701f7ea6` | `912e7dbcbcd0171e` | `912e7dbcbcd0171e` | `912e7dbcbcd0171e` |
| PR AUC | 0.9968 | 0.9987 | 0.9986 | 0.9986 |
| ROC AUC | 0.9980 | 0.9987 | 0.9987 | 0.9987 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2bb4b063701f7ea6
```
