# Confirm PASS — 4589b5a51166b072 on `filetypes/crx`

Cycle `20260628T110043-confirm-4589b5a51166b072` — 2026-06-28T11:00:43Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4589b5a51166b072` | `7b3024369657df7f` | `7b3024369657df7f` | `7b3024369657df7f` |
| PR AUC | 0.9966 | 0.9947 | 0.9944 | 0.9952 |
| ROC AUC | 0.9966 | 0.9947 | 0.9942 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4589b5a51166b072
```
