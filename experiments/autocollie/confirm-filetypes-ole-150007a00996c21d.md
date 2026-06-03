# Confirm PASS — 150007a00996c21d on `filetypes/ole`

Cycle `20260603T163408-confirm-150007a00996c21d` — 2026-06-03T16:34:08Z

PR_AUC held across 3 seeds (orig 0.9935)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `150007a00996c21d` | `a8ff612e51a38dea` | `a8ff612e51a38dea` | `a8ff612e51a38dea` |
| PR AUC | 0.9935 | 0.9935 | 0.9935 | 0.9935 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=150007a00996c21d
```
