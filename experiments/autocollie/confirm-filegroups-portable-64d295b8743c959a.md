# Confirm PASS — 64d295b8743c959a on `filegroups/portable`

Cycle `20260527T013520-confirm-64d295b8743c959a` — 2026-05-27T01:35:20Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `64d295b8743c959a` | `fb8a80965c79ad5c` | `fb8a80965c79ad5c` | `fb8a80965c79ad5c` |
| PR AUC | 0.9967 | 0.9960 | 0.9948 | 0.9957 |
| ROC AUC | 0.9992 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.8200 | 0.7000 | 0.8667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=64d295b8743c959a
```
