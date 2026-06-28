# Confirm PASS — 20a0594822795f93 on `filetypes/ole`

Cycle `20260628T121416-confirm-20a0594822795f93` — 2026-06-28T12:14:16Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `20a0594822795f93` | `e2fab9071eeade7f` | `e2fab9071eeade7f` | `e2fab9071eeade7f` |
| PR AUC | 0.9964 | 0.9968 | 0.9968 | 0.9966 |
| ROC AUC | 0.9890 | 0.9899 | 0.9898 | 0.9891 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=20a0594822795f93
```
