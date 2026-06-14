# Confirm PASS — 19f0b2dd70564c54 on `filetypes/zip`

Cycle `20260614T211217-confirm-19f0b2dd70564c54` — 2026-06-14T21:12:17Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `19f0b2dd70564c54` | `8eee07be53f24512` | `8eee07be53f24512` | `8eee07be53f24512` |
| PR AUC | 0.9996 | 0.9997 | 0.9996 | 0.9996 |
| ROC AUC | 0.9973 | 0.9978 | 0.9973 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=19f0b2dd70564c54
```
