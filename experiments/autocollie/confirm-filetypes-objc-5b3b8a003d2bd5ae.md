# Confirm PASS — 5b3b8a003d2bd5ae on `filetypes/objc`

Cycle `20260525T212809-confirm-5b3b8a003d2bd5ae` — 2026-05-25T21:28:09Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5b3b8a003d2bd5ae` | `b8c11404f19fc7e6` | `b8c11404f19fc7e6` | `b8c11404f19fc7e6` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5b3b8a003d2bd5ae
```
