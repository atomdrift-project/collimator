# Confirm PASS — 769f9afc9d79cf2b on `filetypes/javascript`

Cycle `20260712T160203-confirm-769f9afc9d79cf2b` — 2026-07-12T16:02:03Z

PR_AUC held across 3 seeds (orig 0.9944)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `769f9afc9d79cf2b` | `49ab46ad106b994f` | `49ab46ad106b994f` | `49ab46ad106b994f` |
| PR AUC | 0.9944 | 0.9964 | 0.9964 | 0.9964 |
| ROC AUC | 0.9931 | 0.9970 | 0.9971 | 0.9970 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=769f9afc9d79cf2b
```
