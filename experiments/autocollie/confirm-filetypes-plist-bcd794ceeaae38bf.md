# Confirm PASS — bcd794ceeaae38bf on `filetypes/plist`

Cycle `20260527T020315-confirm-bcd794ceeaae38bf` — 2026-05-27T02:03:15Z

PR_AUC held across 3 seeds (orig 0.8909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bcd794ceeaae38bf` | `f10b4ca8b01f77cb` | `f10b4ca8b01f77cb` | `f10b4ca8b01f77cb` |
| PR AUC | 0.8909 | 0.9429 | 0.9429 | 0.9111 |
| ROC AUC | 0.9400 | 0.9800 | 0.9800 | 0.9600 |
| Recall@3FPM | — | 0.8000 | 0.8000 | 0.8000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bcd794ceeaae38bf
```
