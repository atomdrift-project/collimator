# Confirm PASS — b2adafb0d857f1de on `filetypes/elf`

Cycle `20260706T074302-confirm-b2adafb0d857f1de` — 2026-07-06T07:43:02Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2adafb0d857f1de` | `7318c19ac16a4a67` | `7318c19ac16a4a67` | `7318c19ac16a4a67` |
| PR AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2adafb0d857f1de
```
