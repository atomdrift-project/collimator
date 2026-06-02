# Confirm PASS — 6c4dde7b2d8d237f on `filetypes/powershell`

Cycle `20260602T013126-confirm-6c4dde7b2d8d237f` — 2026-06-02T01:31:26Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6c4dde7b2d8d237f` | `a0429bd07a361caa` | `a0429bd07a361caa` | `a0429bd07a361caa` |
| PR AUC | 0.9993 | 0.9993 | 0.9995 | 0.9995 |
| ROC AUC | 0.9977 | 0.9964 | 0.9976 | 0.9972 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6c4dde7b2d8d237f
```
