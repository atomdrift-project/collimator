# Confirm PASS — ce5daf311bf0b09a on `filetypes/powershell`

Cycle `20260715T185219-confirm-ce5daf311bf0b09a` — 2026-07-15T18:52:19Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ce5daf311bf0b09a` | `10f8821394ee0f9d` | `10f8821394ee0f9d` | `10f8821394ee0f9d` |
| PR AUC | 0.9985 | 0.9986 | 0.9987 | 0.9985 |
| ROC AUC | 0.9947 | 0.9950 | 0.9952 | 0.9947 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ce5daf311bf0b09a
```
