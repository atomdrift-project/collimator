# Confirm PASS — 00439e4bd5a51614 on `filetypes/tar.gz`

Cycle `20260527T021739-confirm-00439e4bd5a51614` — 2026-05-27T02:17:39Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `00439e4bd5a51614` | `5d558cb23137124a` | `5d558cb23137124a` | `5d558cb23137124a` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9988 | 0.9988 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.6739 | 0.7007 | 0.7080 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=00439e4bd5a51614
```
