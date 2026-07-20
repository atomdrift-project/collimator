# Confirm PASS — 58ebe8fe02f40ebb on `filetypes/rtf`

Cycle `20260718T153505-confirm-58ebe8fe02f40ebb` — 2026-07-18T15:35:05Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58ebe8fe02f40ebb` | `dc1709c92c294b82` | `dc1709c92c294b82` | `dc1709c92c294b82` |
| PR AUC | 0.9995 | 0.9997 | 0.9994 | 0.9994 |
| ROC AUC | 0.9977 | 0.9985 | 0.9977 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58ebe8fe02f40ebb
```
