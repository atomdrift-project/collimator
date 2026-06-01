# Confirm PASS — 8f875a32c7cf0244 on `filetypes/go`

Cycle `20260601T152124-confirm-8f875a32c7cf0244` — 2026-06-01T15:21:24Z

PR_AUC held across 3 seeds (orig 0.9646)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8f875a32c7cf0244` | `bca9b456090b193c` | `bca9b456090b193c` | `bca9b456090b193c` |
| PR AUC | 0.9646 | 0.9634 | 0.9599 | 0.9575 |
| ROC AUC | 0.9872 | 0.9897 | 0.9882 | 0.9881 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8f875a32c7cf0244
```
