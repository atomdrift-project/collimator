# Confirm PASS — 916bc3e8d8215694 on `filetypes/csharp`

Cycle `20260527T003405-confirm-916bc3e8d8215694` — 2026-05-27T00:34:05Z

PR_AUC held across 3 seeds (orig 0.9869)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `916bc3e8d8215694` | `a9da60b80efd5bfa` | `a9da60b80efd5bfa` | `a9da60b80efd5bfa` |
| PR AUC | 0.9869 | 0.9842 | 0.9828 | 0.9860 |
| ROC AUC | 0.9927 | 0.9910 | 0.9899 | 0.9923 |
| Recall@3FPM | — | 0.8028 | 0.8592 | 0.9155 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=916bc3e8d8215694
```
