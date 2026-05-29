# Confirm PASS — f72e5260424e8ac3 on `filegroups/native`

Cycle `20260525T190748-confirm-f72e5260424e8ac3` — 2026-05-25T19:07:48Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f72e5260424e8ac3` | `69649609446ec1bb` | `69649609446ec1bb` | `69649609446ec1bb` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.9158 | 0.8693 | 0.8315 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f72e5260424e8ac3
```
