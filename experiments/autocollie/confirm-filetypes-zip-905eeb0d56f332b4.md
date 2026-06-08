# Confirm PASS — 905eeb0d56f332b4 on `filetypes/zip`

Cycle `20260608T112609-confirm-905eeb0d56f332b4` — 2026-06-08T11:26:09Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `905eeb0d56f332b4` | `68763afdaedbff29` | `68763afdaedbff29` | `68763afdaedbff29` |
| PR AUC | 0.9996 | 0.9996 | 0.9996 | 0.9997 |
| ROC AUC | 0.9960 | 0.9959 | 0.9965 | 0.9970 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=905eeb0d56f332b4
```
