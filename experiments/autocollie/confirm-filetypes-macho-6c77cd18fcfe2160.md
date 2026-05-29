# Confirm PASS — 6c77cd18fcfe2160 on `filetypes/macho`

Cycle `20260526T224523-confirm-6c77cd18fcfe2160` — 2026-05-26T22:45:23Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6c77cd18fcfe2160` | `6c9c7715caba3ce9` | `6c9c7715caba3ce9` | `6c9c7715caba3ce9` |
| PR AUC | 0.9997 | 0.9974 | 0.9977 | 0.9971 |
| ROC AUC | 0.9999 | 0.9995 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.8496 | 0.9135 | 0.8797 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6c77cd18fcfe2160
```
