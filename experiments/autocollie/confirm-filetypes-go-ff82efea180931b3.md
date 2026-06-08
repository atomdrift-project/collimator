# Confirm PASS — ff82efea180931b3 on `filetypes/go`

Cycle `20260608T101404-confirm-ff82efea180931b3` — 2026-06-08T10:14:04Z

PR_AUC held across 3 seeds (orig 0.9442)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ff82efea180931b3` | `61d266cb31970e9a` | `61d266cb31970e9a` | `61d266cb31970e9a` |
| PR AUC | 0.9442 | 0.9487 | 0.9460 | 0.9452 |
| ROC AUC | 0.9858 | 0.9869 | 0.9852 | 0.9853 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ff82efea180931b3
```
