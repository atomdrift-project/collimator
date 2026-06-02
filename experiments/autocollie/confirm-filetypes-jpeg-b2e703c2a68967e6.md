# Confirm PASS — b2e703c2a68967e6 on `filetypes/jpeg`

Cycle `20260602T031606-confirm-b2e703c2a68967e6` — 2026-06-02T03:16:06Z

PR_AUC held across 3 seeds (orig 0.9460)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2e703c2a68967e6` | `561e114edbec5220` | `561e114edbec5220` | `561e114edbec5220` |
| PR AUC | 0.9460 | 0.9744 | 0.9797 | 0.9757 |
| ROC AUC | 0.9687 | 0.9871 | 0.9894 | 0.9855 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2e703c2a68967e6
```
