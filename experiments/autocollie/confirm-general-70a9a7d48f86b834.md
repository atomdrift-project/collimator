# Confirm PASS — 70a9a7d48f86b834 on `general`

Cycle `20260527T040543-confirm-70a9a7d48f86b834` — 2026-05-27T04:05:43Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `70a9a7d48f86b834` | `18f0296b553e94da` | `18f0296b553e94da` | `18f0296b553e94da` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9987 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.7036 | 0.6751 | 0.6817 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=70a9a7d48f86b834
```
