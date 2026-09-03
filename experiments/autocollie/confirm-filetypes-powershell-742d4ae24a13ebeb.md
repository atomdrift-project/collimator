# Confirm PASS — 742d4ae24a13ebeb on `filetypes/powershell`

Cycle `20260824T212423-confirm-742d4ae24a13ebeb` — 2026-08-24T21:24:23Z

PR_AUC held across 3 seeds (orig 0.9931)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `742d4ae24a13ebeb` | `f3c0ff44dd571e15` | `f3c0ff44dd571e15` | `f3c0ff44dd571e15` |
| PR AUC | 0.9931 | 0.9938 | 0.9925 | 0.9941 |
| ROC AUC | 0.9901 | 0.9913 | 0.9896 | 0.9917 |
| Recall@L50 | — | 0.7560 | 0.7573 | 0.7838 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=742d4ae24a13ebeb
```
