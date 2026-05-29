# Confirm PASS — eb2b35d751d379d2 on `filetypes/zst`

Cycle `20260526T185437-confirm-eb2b35d751d379d2` — 2026-05-26T18:54:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eb2b35d751d379d2` | `b657b24e857dc0c5` | `b657b24e857dc0c5` | `b657b24e857dc0c5` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eb2b35d751d379d2
```
