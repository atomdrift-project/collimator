# Confirm PASS — c77ef0fd228cda8e on `filetypes/jpeg`

Cycle `20260720T113741-confirm-c77ef0fd228cda8e` — 2026-07-20T11:37:41Z

PR_AUC held across 3 seeds (orig 0.9786)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c77ef0fd228cda8e` | `9e139c4af0d7102d` | `9e139c4af0d7102d` | `9e139c4af0d7102d` |
| PR AUC | 0.9786 | 0.9783 | 0.9773 | 0.9797 |
| ROC AUC | 0.9769 | 0.9773 | 0.9758 | 0.9767 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c77ef0fd228cda8e
```
