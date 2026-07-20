# Confirm PASS — 7d9df386865c9996 on `filetypes/powershell`

Cycle `20260718T154205-confirm-7d9df386865c9996` — 2026-07-18T15:42:05Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7d9df386865c9996` | `46bdc500fcc4aeac` | `46bdc500fcc4aeac` | `46bdc500fcc4aeac` |
| PR AUC | 0.9986 | 0.9985 | 0.9984 | 0.9985 |
| ROC AUC | 0.9947 | 0.9943 | 0.9939 | 0.9943 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7d9df386865c9996
```
