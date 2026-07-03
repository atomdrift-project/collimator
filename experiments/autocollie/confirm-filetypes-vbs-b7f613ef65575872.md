# Confirm PASS — b7f613ef65575872 on `filetypes/vbs`

Cycle `20260628T163637-confirm-b7f613ef65575872` — 2026-06-28T16:36:37Z

PR_AUC held across 3 seeds (orig 0.9963)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b7f613ef65575872` | `3c87f672707de363` | `3c87f672707de363` | `3c87f672707de363` |
| PR AUC | 0.9963 | 0.9966 | 0.9968 | 0.9966 |
| ROC AUC | 0.9864 | 0.9877 | 0.9882 | 0.9876 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b7f613ef65575872
```
