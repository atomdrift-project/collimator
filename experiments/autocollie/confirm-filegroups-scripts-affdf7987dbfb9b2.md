# Confirm PASS — affdf7987dbfb9b2 on `filegroups/scripts`

Cycle `20260526T050408-confirm-affdf7987dbfb9b2` — 2026-05-26T05:04:08Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `affdf7987dbfb9b2` | `7ac45566219f1064` | `7ac45566219f1064` | `7ac45566219f1064` |
| PR AUC | 0.9978 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9977 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.8023 | 0.7963 | 0.8013 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=affdf7987dbfb9b2
```
