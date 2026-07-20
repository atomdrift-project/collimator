# Confirm PASS — 9ffb481f93a4149b on `filegroups/native`

Cycle `20260713T104242-confirm-9ffb481f93a4149b` — 2026-07-13T10:42:42Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9ffb481f93a4149b` | `b2c1ded8ebe044e6` | `b2c1ded8ebe044e6` | `b2c1ded8ebe044e6` |
| PR AUC | 0.9992 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9998 | 0.9998 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9ffb481f93a4149b
```
