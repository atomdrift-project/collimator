# Confirm PASS — 64dcbeb2387eaabf on `filegroups/documents`

Cycle `20260723T072257-confirm-64dcbeb2387eaabf` — 2026-07-23T07:22:57Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `64dcbeb2387eaabf` | `30ee12637364b16c` | `30ee12637364b16c` | `30ee12637364b16c` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=64dcbeb2387eaabf
```
