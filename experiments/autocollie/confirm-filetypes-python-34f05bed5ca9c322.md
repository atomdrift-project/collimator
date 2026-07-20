# Confirm PASS — 34f05bed5ca9c322 on `filetypes/python`

Cycle `20260711T093444-confirm-34f05bed5ca9c322` — 2026-07-11T09:34:44Z

PR_AUC held across 3 seeds (orig 0.9750)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `34f05bed5ca9c322` | `6ba0202f84604188` | `6ba0202f84604188` | `6ba0202f84604188` |
| PR AUC | 0.9750 | 0.9781 | 0.9779 | 0.9780 |
| ROC AUC | 0.9883 | 0.9894 | 0.9895 | 0.9895 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=34f05bed5ca9c322
```
