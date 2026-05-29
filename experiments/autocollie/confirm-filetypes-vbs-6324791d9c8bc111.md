# Confirm PASS — 6324791d9c8bc111 on `filetypes/vbs`

Cycle `20260525T203306-confirm-6324791d9c8bc111` — 2026-05-25T20:33:06Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6324791d9c8bc111` | `ef97db65071dbdc2` | `ef97db65071dbdc2` | `ef97db65071dbdc2` |
| PR AUC | 0.9993 | 0.9959 | 0.9947 | 0.9961 |
| ROC AUC | 0.9989 | 0.9774 | 0.9765 | 0.9789 |
| Recall@3FPM | — | 0.2084 | 0.1175 | 0.2106 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6324791d9c8bc111
```
