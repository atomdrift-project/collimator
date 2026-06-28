# Confirm PASS — 19b2e0952c1b0dc3 on `filetypes/crx`

Cycle `20260628T035728-confirm-19b2e0952c1b0dc3` — 2026-06-28T03:57:28Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `19b2e0952c1b0dc3` | `df7aa4151ba6535e` | `df7aa4151ba6535e` | `df7aa4151ba6535e` |
| PR AUC | 0.9966 | 0.9943 | 0.9944 | 0.9952 |
| ROC AUC | 0.9966 | 0.9943 | 0.9942 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=19b2e0952c1b0dc3
```
