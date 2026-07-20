# Confirm PASS — 4d4ea6d82192a933 on `filetypes/batch`

Cycle `20260712T131608-confirm-4d4ea6d82192a933` — 2026-07-12T13:16:08Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4d4ea6d82192a933` | `e055026e6509d7d6` | `e055026e6509d7d6` | `e055026e6509d7d6` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9977 | 0.9987 | 0.9989 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4d4ea6d82192a933
```
