# Confirm PASS — fb254c34f1cd2196 on `filegroups/source`

Cycle `20260514T181221-confirm-fb254c34f1cd2196` — 2026-05-14T18:12:21Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fb254c34f1cd2196` | `55b2baf7a6e21f45` | `55b2baf7a6e21f45` | `55b2baf7a6e21f45` |
| PR AUC | 0.9983 | 0.9982 | 0.9981 | 0.9982 |
| ROC AUC | 0.9981 | 0.9981 | 0.9979 | 0.9981 |
| Recall@3FPM | — | 0.8504 | 0.8704 | 0.8669 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fb254c34f1cd2196
```
