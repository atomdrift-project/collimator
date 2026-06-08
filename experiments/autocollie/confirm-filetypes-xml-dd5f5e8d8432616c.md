# Confirm PASS — dd5f5e8d8432616c on `filetypes/xml`

Cycle `20260608T120001-confirm-dd5f5e8d8432616c` — 2026-06-08T12:00:01Z

PR_AUC held across 3 seeds (orig 0.9948)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `dd5f5e8d8432616c` | `6c8bddc8f56e792d` | `6c8bddc8f56e792d` | `6c8bddc8f56e792d` |
| PR AUC | 0.9948 | 0.9978 | 0.9964 | 0.9978 |
| ROC AUC | 0.9983 | 0.9993 | 0.9988 | 0.9993 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=dd5f5e8d8432616c
```
