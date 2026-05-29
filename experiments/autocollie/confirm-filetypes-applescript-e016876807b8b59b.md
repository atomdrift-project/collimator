# Confirm PASS — e016876807b8b59b on `filetypes/applescript`

Cycle `20260527T064701-confirm-e016876807b8b59b` — 2026-05-27T06:47:01Z

PR_AUC held across 3 seeds (orig 0.4000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e016876807b8b59b` | `a3cb74ea759c1ca6` | `a3cb74ea759c1ca6` | `a3cb74ea759c1ca6` |
| PR AUC | 0.4000 | 0.4000 | 0.4000 | 0.4000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e016876807b8b59b
```
