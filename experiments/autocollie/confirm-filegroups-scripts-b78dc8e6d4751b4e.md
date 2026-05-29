# Confirm PASS — b78dc8e6d4751b4e on `filegroups/scripts`

Cycle `20260528T100602-confirm-b78dc8e6d4751b4e` — 2026-05-28T10:06:02Z

PR_AUC held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b78dc8e6d4751b4e` | `b4d89319f564efea` | `b4d89319f564efea` | `b4d89319f564efea` |
| PR AUC | 0.9974 | 0.9987 | 0.9987 | 0.9987 |
| ROC AUC | 0.9972 | 0.9985 | 0.9986 | 0.9985 |
| Recall@3FPM | — | 0.5369 | 0.5897 | 0.6288 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b78dc8e6d4751b4e
```
