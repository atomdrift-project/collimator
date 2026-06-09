# Confirm PASS — 3c7437d2f296c568 on `filetypes/ole`

Cycle `20260609T051451-confirm-3c7437d2f296c568` — 2026-06-09T05:14:51Z

PR_AUC held across 3 seeds (orig 0.9969)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3c7437d2f296c568` | `b45dbb9068c8d12d` | `b45dbb9068c8d12d` | `b45dbb9068c8d12d` |
| PR AUC | 0.9969 | 0.9949 | 0.9972 | 0.9955 |
| ROC AUC | 0.9963 | 0.9938 | 0.9967 | 0.9944 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3c7437d2f296c568
```
