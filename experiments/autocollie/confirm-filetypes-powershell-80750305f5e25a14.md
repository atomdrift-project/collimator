# Confirm PASS — 80750305f5e25a14 on `filetypes/powershell`

Cycle `20260608T105614-confirm-80750305f5e25a14` — 2026-06-08T10:56:14Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `80750305f5e25a14` | `aa504544e3ab88df` | `aa504544e3ab88df` | `aa504544e3ab88df` |
| PR AUC | 0.9993 | 0.9989 | 0.9994 | 0.9995 |
| ROC AUC | 0.9964 | 0.9948 | 0.9969 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=80750305f5e25a14
```
