# Confirm PASS — 0f5ed5ab2debefc9 on `filetypes/json`

Cycle `20260606T022510-confirm-0f5ed5ab2debefc9` — 2026-06-06T02:25:10Z

PR_AUC held across 3 seeds (orig 0.0247)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0f5ed5ab2debefc9` | `7cac181ef55a0ba6` | `7cac181ef55a0ba6` | `7cac181ef55a0ba6` |
| PR AUC | 0.0247 | 0.0247 | 0.0247 | 0.0247 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0f5ed5ab2debefc9
```
