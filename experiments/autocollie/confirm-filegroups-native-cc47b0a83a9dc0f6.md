# Confirm PASS — cc47b0a83a9dc0f6 on `filegroups/native`

Cycle `20260524T111908-confirm-cc47b0a83a9dc0f6` — 2026-05-24T11:19:08Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc47b0a83a9dc0f6` | `dc440f277c41de84` | `dc440f277c41de84` | `dc440f277c41de84` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.8984 | 0.8888 | 0.8709 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cc47b0a83a9dc0f6
```
