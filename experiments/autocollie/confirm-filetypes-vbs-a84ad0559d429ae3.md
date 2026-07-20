# Confirm PASS — a84ad0559d429ae3 on `filetypes/vbs`

Cycle `20260715T030231-confirm-a84ad0559d429ae3` — 2026-07-15T03:02:31Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a84ad0559d429ae3` | `065232825c2e8478` | `065232825c2e8478` | `065232825c2e8478` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9982 |
| ROC AUC | 0.9975 | 0.9970 | 0.9967 | 0.9722 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a84ad0559d429ae3
```
