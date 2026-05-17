# Confirm PASS — 57324b04f5b60821 on `filegroups/config`

Cycle `20260514T193410-confirm-57324b04f5b60821` — 2026-05-14T19:34:10Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `57324b04f5b60821` | `eb7772afb1dd01b4` | `eb7772afb1dd01b4` | `eb7772afb1dd01b4` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9999 |
| ROC AUC | 0.9998 | 0.9996 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.8819 | 0.8721 | 0.9580 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=57324b04f5b60821
```
