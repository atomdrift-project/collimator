# Confirm PASS — 7ec3046994023321 on `filetypes/zip`

Cycle `20260715T113450-confirm-7ec3046994023321` — 2026-07-15T11:34:50Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7ec3046994023321` | `5a289bc4eddc7e4c` | `5a289bc4eddc7e4c` | `5a289bc4eddc7e4c` |
| PR AUC | 0.9987 | 0.9989 | 0.9989 | 0.9989 |
| ROC AUC | 0.9944 | 0.9953 | 0.9954 | 0.9952 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7ec3046994023321
```
