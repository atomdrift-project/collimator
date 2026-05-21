# Confirm PASS — 7ce144367af156b0 on `filetypes/powershell`

Cycle `20260521T054721-confirm-7ce144367af156b0` — 2026-05-21T05:47:21Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7ce144367af156b0` | `c47039f0a0ac3cac` | `c47039f0a0ac3cac` | `c47039f0a0ac3cac` |
| PR AUC | 0.9979 | 0.9966 | 0.9985 | 0.9967 |
| ROC AUC | 0.9950 | 0.9920 | 0.9964 | 0.9926 |
| Recall@3FPM | — | 0.7379 | 0.8185 | 0.6532 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7ce144367af156b0
```
