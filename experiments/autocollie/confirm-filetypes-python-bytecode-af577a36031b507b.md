# Confirm PASS — af577a36031b507b on `filetypes/python-bytecode`

Cycle `20260716T021538-confirm-af577a36031b507b` — 2026-07-16T02:15:38Z

PR_AUC held across 3 seeds (orig 0.9945)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `af577a36031b507b` | `4fc5b8616762982c` | `4fc5b8616762982c` | `4fc5b8616762982c` |
| PR AUC | 0.9945 | 0.9946 | 0.9940 | 0.9953 |
| ROC AUC | 0.9979 | 0.9981 | 0.9975 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=af577a36031b507b
```
