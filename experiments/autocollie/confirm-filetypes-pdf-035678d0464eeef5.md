# Confirm PASS — 035678d0464eeef5 on `filetypes/pdf`

Cycle `20260525T194223-confirm-035678d0464eeef5` — 2026-05-25T19:42:23Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `035678d0464eeef5` | `243ef4e7f888dff1` | `243ef4e7f888dff1` | `243ef4e7f888dff1` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9877 | 0.9877 | 0.9881 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=035678d0464eeef5
```
