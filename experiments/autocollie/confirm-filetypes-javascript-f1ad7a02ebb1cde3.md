# Confirm PASS — f1ad7a02ebb1cde3 on `filetypes/javascript`

Cycle `20260716T041610-confirm-f1ad7a02ebb1cde3` — 2026-07-16T04:16:10Z

PR_AUC held across 3 seeds (orig 0.9948)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f1ad7a02ebb1cde3` | `8a0e5b8f45dc74ca` | `8a0e5b8f45dc74ca` | `8a0e5b8f45dc74ca` |
| PR AUC | 0.9948 | 0.9963 | 0.9963 | 0.9962 |
| ROC AUC | 0.9937 | 0.9969 | 0.9969 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f1ad7a02ebb1cde3
```
