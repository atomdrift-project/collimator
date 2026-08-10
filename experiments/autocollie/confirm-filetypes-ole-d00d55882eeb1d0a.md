# Confirm PASS — d00d55882eeb1d0a on `filetypes/ole`

Cycle `20260805T020910-confirm-d00d55882eeb1d0a` — 2026-08-05T02:09:10Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d00d55882eeb1d0a` | `344417be3986a630` | `344417be3986a630` | `344417be3986a630` |
| PR AUC | 0.9977 | 0.9981 | 0.9974 | 0.9978 |
| ROC AUC | 0.9932 | 0.9936 | 0.9915 | 0.9928 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d00d55882eeb1d0a
```
