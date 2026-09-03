# Confirm PASS — 510acf10d215547b on `filetypes/jar`

Cycle `20260824T161447-confirm-510acf10d215547b` — 2026-08-24T16:14:47Z

PR_AUC held across 3 seeds (orig 0.9226)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `510acf10d215547b` | `238e1a72923cc666` | `238e1a72923cc666` | `238e1a72923cc666` |
| PR AUC | 0.9226 | 0.9317 | 0.9426 | 0.9398 |
| ROC AUC | 0.9664 | 0.9732 | 0.9778 | 0.9758 |
| Recall@L50 | — | 0.6825 | 0.6647 | 0.6845 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=510acf10d215547b
```
