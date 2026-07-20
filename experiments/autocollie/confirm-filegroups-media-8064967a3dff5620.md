# Confirm PASS — 8064967a3dff5620 on `filegroups/media`

Cycle `20260715T200131-confirm-8064967a3dff5620` — 2026-07-15T20:01:31Z

PR_AUC held across 3 seeds (orig 0.9864)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8064967a3dff5620` | `35e67ee73db82ca5` | `35e67ee73db82ca5` | `35e67ee73db82ca5` |
| PR AUC | 0.9864 | 0.9867 | 0.9891 | 0.9877 |
| ROC AUC | 0.9780 | 0.9789 | 0.9840 | 0.9805 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8064967a3dff5620
```
