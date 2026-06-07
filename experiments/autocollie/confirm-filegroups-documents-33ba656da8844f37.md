# Confirm PASS — 33ba656da8844f37 on `filegroups/documents`

Cycle `20260606T133147-confirm-33ba656da8844f37` — 2026-06-06T13:31:47Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `33ba656da8844f37` | `0b0b8faa06a4d5ce` | `0b0b8faa06a4d5ce` | `0b0b8faa06a4d5ce` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=33ba656da8844f37
```
