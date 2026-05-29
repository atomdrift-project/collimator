# Confirm PASS — 06d781a562bc7f81 on `filetypes/lnk`

Cycle `20260526T232320-confirm-06d781a562bc7f81` — 2026-05-26T23:23:20Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06d781a562bc7f81` | `0dd4d9bb34b145b3` | `0dd4d9bb34b145b3` | `0dd4d9bb34b145b3` |
| PR AUC | 0.9989 | 0.9987 | 0.9991 | 0.9992 |
| ROC AUC | 0.9858 | 0.9829 | 0.9887 | 0.9897 |
| Recall@3FPM | — | 0.9282 | 0.9590 | 0.9641 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06d781a562bc7f81
```
