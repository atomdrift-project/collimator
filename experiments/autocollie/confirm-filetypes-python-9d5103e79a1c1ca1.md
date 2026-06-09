# Confirm PASS — 9d5103e79a1c1ca1 on `filetypes/python`

Cycle `20260609T155916-confirm-9d5103e79a1c1ca1` — 2026-06-09T15:59:16Z

PR_AUC held across 3 seeds (orig 0.9927)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9d5103e79a1c1ca1` | `e54e06327c9dc8a8` | `e54e06327c9dc8a8` | `e54e06327c9dc8a8` |
| PR AUC | 0.9927 | 0.9931 | 0.9936 | 0.9936 |
| ROC AUC | 0.9945 | 0.9948 | 0.9951 | 0.9952 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9d5103e79a1c1ca1
```
