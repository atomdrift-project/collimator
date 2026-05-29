# Confirm PASS — 6777b1b51ea2dd4a on `filetypes/powershell`

Cycle `20260527T004924-confirm-6777b1b51ea2dd4a` — 2026-05-27T00:49:24Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6777b1b51ea2dd4a` | `5d9c9f691b94f6a0` | `5d9c9f691b94f6a0` | `5d9c9f691b94f6a0` |
| PR AUC | 0.9979 | 0.9988 | 0.9990 | 0.9984 |
| ROC AUC | 0.9945 | 0.9957 | 0.9965 | 0.9944 |
| Recall@3FPM | — | 0.9117 | 0.9231 | 0.8433 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6777b1b51ea2dd4a
```
