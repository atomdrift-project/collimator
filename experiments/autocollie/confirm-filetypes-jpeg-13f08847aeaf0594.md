# Confirm PASS — 13f08847aeaf0594 on `filetypes/jpeg`

Cycle `20260706T035516-confirm-13f08847aeaf0594` — 2026-07-06T03:55:16Z

PR_AUC held across 3 seeds (orig 0.9684)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `13f08847aeaf0594` | `1aedfe3255060081` | `1aedfe3255060081` | `1aedfe3255060081` |
| PR AUC | 0.9684 | 0.9772 | 0.9803 | 0.9678 |
| ROC AUC | 0.9690 | 0.9780 | 0.9847 | 0.9755 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=13f08847aeaf0594
```
