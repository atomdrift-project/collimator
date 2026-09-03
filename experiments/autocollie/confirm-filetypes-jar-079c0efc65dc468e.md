# Confirm PASS — 079c0efc65dc468e on `filetypes/jar`

Cycle `20260821T134343-confirm-079c0efc65dc468e` — 2026-08-21T13:43:43Z

PR_AUC held across 3 seeds (orig 0.9651)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `079c0efc65dc468e` | `6dd6ed53acbd6f73` | `6dd6ed53acbd6f73` | `6dd6ed53acbd6f73` |
| PR AUC | 0.9651 | 0.9718 | 0.9709 | 0.9725 |
| ROC AUC | 0.9893 | 0.9910 | 0.9901 | 0.9904 |
| Recall@L50 | — | 0.7659 | 0.7718 | 0.7837 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=079c0efc65dc468e
```
