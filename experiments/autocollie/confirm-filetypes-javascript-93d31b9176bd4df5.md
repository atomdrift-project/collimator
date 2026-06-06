# Confirm PASS — 93d31b9176bd4df5 on `filetypes/javascript`

Cycle `20260606T202019-confirm-93d31b9176bd4df5` — 2026-06-06T20:20:19Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `93d31b9176bd4df5` | `cb7f3f14ccb41166` | `cb7f3f14ccb41166` | `cb7f3f14ccb41166` |
| PR AUC | 0.9978 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9974 | 0.9989 | 0.9989 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=93d31b9176bd4df5
```
