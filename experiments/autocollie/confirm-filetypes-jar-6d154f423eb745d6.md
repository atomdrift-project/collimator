# Confirm PASS — 6d154f423eb745d6 on `filetypes/jar`

Cycle `20260525T204045-confirm-6d154f423eb745d6` — 2026-05-25T20:40:45Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6d154f423eb745d6` | `443a32a3ad6ff508` | `443a32a3ad6ff508` | `443a32a3ad6ff508` |
| PR AUC | 0.9985 | 0.9979 | 0.9988 | 0.9983 |
| ROC AUC | 0.9971 | 0.9960 | 0.9979 | 0.9970 |
| Recall@3FPM | — | 0.8693 | 0.8920 | 0.8523 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6d154f423eb745d6
```
