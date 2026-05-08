# Confirm PASS — f8cbfb3bb6b5a1ac on `filetypes/perl`

Cycle `20260508T193801-confirm-f8cbfb3bb6b5a1ac` — 2026-05-08T19:38:01Z

F1 held across 3 seeds (orig 0.9714)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8cbfb3bb6b5a1ac` | `02d18db91a7ecd88` | `02d18db91a7ecd88` | `02d18db91a7ecd88` |
| F1 | 0.9714 | 1.0000 | 0.7857 | 0.9032 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f8cbfb3bb6b5a1ac
```
