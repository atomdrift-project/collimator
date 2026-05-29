# Confirm PASS — cd289d40b3f45d1f on `filetypes/zip`

Cycle `20260525T205534-confirm-cd289d40b3f45d1f` — 2026-05-25T20:55:34Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cd289d40b3f45d1f` | `35d7c92845e9f21d` | `35d7c92845e9f21d` | `35d7c92845e9f21d` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9984 | 0.9961 | 0.9962 | 0.9961 |
| Recall@3FPM | — | 0.6603 | 0.7133 | 0.6868 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cd289d40b3f45d1f
```
