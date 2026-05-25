# Confirm PASS — dd154a3b449a0f23 on `filetypes/xls`

Cycle `20260524T074245-confirm-dd154a3b449a0f23` — 2026-05-24T07:42:45Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `dd154a3b449a0f23` | `a7511a83e21cb6ab` | `a7511a83e21cb6ab` | `a7511a83e21cb6ab` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9992 | 0.9991 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.9735 | 0.9735 | 0.9720 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=dd154a3b449a0f23
```
