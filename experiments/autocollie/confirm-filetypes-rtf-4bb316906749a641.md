# Confirm PASS — 4bb316906749a641 on `filetypes/rtf`

Cycle `20260608T080155-confirm-4bb316906749a641` — 2026-06-08T08:01:55Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4bb316906749a641` | `18950a88fa7d58d0` | `18950a88fa7d58d0` | `18950a88fa7d58d0` |
| PR AUC | 0.9999 | 0.9997 | 0.9997 | 0.9999 |
| ROC AUC | 0.9987 | 0.9971 | 0.9978 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4bb316906749a641
```
