# Confirm PASS — 391e52008deb2505 on `filetypes/xlsx`

Cycle `20260824T234645-confirm-391e52008deb2505` — 2026-08-24T23:46:45Z

PR_AUC held across 3 seeds (orig 0.9926)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `391e52008deb2505` | `80c0853569b84578` | `80c0853569b84578` | `80c0853569b84578` |
| PR AUC | 0.9926 | 0.9918 | 0.9854 | 0.9926 |
| ROC AUC | 0.8659 | 0.8533 | 0.7374 | 0.8690 |
| Recall@L50 | — | 0.3175 | 0.3168 | 0.3234 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=391e52008deb2505
```
