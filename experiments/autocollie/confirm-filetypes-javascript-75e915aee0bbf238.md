# Confirm PASS — 75e915aee0bbf238 on `filetypes/javascript`

Cycle `20260613T020819-confirm-75e915aee0bbf238` — 2026-06-13T02:08:19Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `75e915aee0bbf238` | `44716a7fb30adba4` | `44716a7fb30adba4` | `44716a7fb30adba4` |
| PR AUC | 0.9968 | 0.9987 | 0.9987 | 0.9987 |
| ROC AUC | 0.9961 | 0.9982 | 0.9983 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=75e915aee0bbf238
```
