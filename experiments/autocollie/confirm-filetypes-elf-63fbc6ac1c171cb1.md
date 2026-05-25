# Confirm PASS — 63fbc6ac1c171cb1 on `filetypes/elf`

Cycle `20260524T190753-confirm-63fbc6ac1c171cb1` — 2026-05-24T19:07:53Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `63fbc6ac1c171cb1` | `531ad1e23850fad6` | `531ad1e23850fad6` | `531ad1e23850fad6` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9683 | 0.9723 | 0.9705 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63fbc6ac1c171cb1
```
