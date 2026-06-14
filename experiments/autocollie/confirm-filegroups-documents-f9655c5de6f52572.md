# Confirm PASS — f9655c5de6f52572 on `filegroups/documents`

Cycle `20260613T181050-confirm-f9655c5de6f52572` — 2026-06-13T18:10:50Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f9655c5de6f52572` | `858f2993de0d8add` | `858f2993de0d8add` | `858f2993de0d8add` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f9655c5de6f52572
```
