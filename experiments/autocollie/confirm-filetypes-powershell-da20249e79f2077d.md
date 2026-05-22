# Confirm PASS — da20249e79f2077d on `filetypes/powershell`

Cycle `20260522T172750-confirm-da20249e79f2077d` — 2026-05-22T17:27:50Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `da20249e79f2077d` | `9039d25b71f17135` | `9039d25b71f17135` | `9039d25b71f17135` |
| PR AUC | 0.9987 | 0.9973 | 0.9985 | 0.9962 |
| ROC AUC | 0.9967 | 0.9936 | 0.9963 | 0.9917 |
| Recall@3FPM | — | 0.7500 | 0.8387 | 0.6210 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=da20249e79f2077d
```
