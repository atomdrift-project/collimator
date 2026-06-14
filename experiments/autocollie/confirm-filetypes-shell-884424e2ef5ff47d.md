# Confirm PASS — 884424e2ef5ff47d on `filetypes/shell`

Cycle `20260613T020342-confirm-884424e2ef5ff47d` — 2026-06-13T02:03:42Z

PR_AUC held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `884424e2ef5ff47d` | `c4fa834aef6770a0` | `c4fa834aef6770a0` | `c4fa834aef6770a0` |
| PR AUC | 0.9974 | 0.9974 | 0.9974 | 0.9973 |
| ROC AUC | 0.9975 | 0.9975 | 0.9976 | 0.9975 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=884424e2ef5ff47d
```
