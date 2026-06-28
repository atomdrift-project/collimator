# Confirm PASS — 3cca4bf16e9b6957 on `filetypes/crx`

Cycle `20260628T101637-confirm-3cca4bf16e9b6957` — 2026-06-28T10:16:37Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3cca4bf16e9b6957` | `e582e373204dcd1f` | `e582e373204dcd1f` | `e582e373204dcd1f` |
| PR AUC | 0.9966 | 0.9947 | 0.9944 | 0.9952 |
| ROC AUC | 0.9966 | 0.9947 | 0.9942 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3cca4bf16e9b6957
```
