# Confirm PASS — 217e1001d048a8bf on `filetypes/xls`

Cycle `20260704T145223-confirm-217e1001d048a8bf` — 2026-07-04T14:52:23Z

PR_AUC held across 3 seeds (orig 0.9972)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `217e1001d048a8bf` | `d78db7171af65ecc` | `d78db7171af65ecc` | `d78db7171af65ecc` |
| PR AUC | 0.9972 | 0.9975 | 0.9976 | 0.9976 |
| ROC AUC | 0.9912 | 0.9919 | 0.9922 | 0.9921 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=217e1001d048a8bf
```
