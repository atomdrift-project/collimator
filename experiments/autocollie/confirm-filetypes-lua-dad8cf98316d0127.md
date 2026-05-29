# Confirm PASS — dad8cf98316d0127 on `filetypes/lua`

Cycle `20260527T052452-confirm-dad8cf98316d0127` — 2026-05-27T05:24:52Z

PR_AUC held across 3 seeds (orig 0.6738)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `dad8cf98316d0127` | `97490397a42ee18e` | `97490397a42ee18e` | `97490397a42ee18e` |
| PR AUC | 0.6738 | 0.7056 | 0.7125 | 0.7056 |
| ROC AUC | 0.8370 | 0.8641 | 0.8587 | 0.8641 |
| Recall@3FPM | — | 0.5000 | 0.5000 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=dad8cf98316d0127
```
