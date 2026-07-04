# Confirm PASS — 6a3094941f9958c7 on `filegroups/source`

Cycle `20260704T080957-confirm-6a3094941f9958c7` — 2026-07-04T08:09:57Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6a3094941f9958c7` | `7a6605a340aef97f` | `7a6605a340aef97f` | `7a6605a340aef97f` |
| PR AUC | 0.9990 | 0.9960 | 0.9960 | 0.9960 |
| ROC AUC | 0.9982 | 0.9964 | 0.9965 | 0.9964 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6a3094941f9958c7
```
