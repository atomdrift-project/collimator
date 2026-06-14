# Confirm PASS — 65f71553d88b8f51 on `filetypes/shell`

Cycle `20260614T221346-confirm-65f71553d88b8f51` — 2026-06-14T22:13:46Z

PR_AUC held across 3 seeds (orig 0.9949)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `65f71553d88b8f51` | `b69b99e827cbb668` | `b69b99e827cbb668` | `b69b99e827cbb668` |
| PR AUC | 0.9949 | 0.9962 | 0.9960 | 0.9967 |
| ROC AUC | 0.9966 | 0.9963 | 0.9962 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=65f71553d88b8f51
```
