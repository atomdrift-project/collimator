# Confirm PASS — af749053f5d464ff on `filetypes/tar.gz`

Cycle `20260527T020642-confirm-af749053f5d464ff` — 2026-05-27T02:06:42Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `af749053f5d464ff` | `5d558cb23137124a` | `5d558cb23137124a` | `5d558cb23137124a` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9988 | 0.9988 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.6739 | 0.7007 | 0.7080 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=af749053f5d464ff
```
