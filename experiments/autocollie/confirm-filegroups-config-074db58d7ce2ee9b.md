# Confirm PASS — 074db58d7ce2ee9b on `filegroups/config`

Cycle `20260608T111228-confirm-074db58d7ce2ee9b` — 2026-06-08T11:12:28Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `074db58d7ce2ee9b` | `8ac66087d18d9a9c` | `8ac66087d18d9a9c` | `8ac66087d18d9a9c` |
| PR AUC | 0.9987 | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9981 | 0.9983 | 0.9981 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=074db58d7ce2ee9b
```
