# Confirm PASS — 0020750eb24a6867 on `filetypes/vbs`

Cycle `20260608T022508-confirm-0020750eb24a6867` — 2026-06-08T02:25:08Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0020750eb24a6867` | `801bdc9ae17238d4` | `801bdc9ae17238d4` | `801bdc9ae17238d4` |
| PR AUC | 0.9977 | 0.9976 | 0.9974 | 0.9974 |
| ROC AUC | 0.9922 | 0.9919 | 0.9912 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0020750eb24a6867
```
