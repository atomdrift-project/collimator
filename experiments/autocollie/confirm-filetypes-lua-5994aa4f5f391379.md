# Confirm PASS — 5994aa4f5f391379 on `filetypes/lua`

Cycle `20260527T052126-confirm-5994aa4f5f391379` — 2026-05-27T05:21:26Z

PR_AUC held across 3 seeds (orig 0.5995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5994aa4f5f391379` | `bac69f628347be77` | `bac69f628347be77` | `bac69f628347be77` |
| PR AUC | 0.5995 | 0.7183 | 0.6442 | 0.7056 |
| ROC AUC | 0.7772 | 0.9076 | 0.8315 | 0.8641 |
| Recall@3FPM | — | 0.5000 | 0.5000 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5994aa4f5f391379
```
