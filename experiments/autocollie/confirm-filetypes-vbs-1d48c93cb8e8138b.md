# Confirm PASS — 1d48c93cb8e8138b on `filetypes/vbs`

Cycle `20260606T092243-confirm-1d48c93cb8e8138b` — 2026-06-06T09:22:43Z

PR_AUC held across 3 seeds (orig 0.9973)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1d48c93cb8e8138b` | `2c093ddd5aeb0bda` | `2c093ddd5aeb0bda` | `2c093ddd5aeb0bda` |
| PR AUC | 0.9973 | 0.9968 | 0.9976 | 0.9971 |
| ROC AUC | 0.9912 | 0.9896 | 0.9922 | 0.9905 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1d48c93cb8e8138b
```
