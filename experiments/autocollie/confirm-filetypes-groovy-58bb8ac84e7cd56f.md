# Confirm PASS — 58bb8ac84e7cd56f on `filetypes/groovy`

Cycle `20260527T080041-confirm-58bb8ac84e7cd56f` — 2026-05-27T08:00:41Z

PR_AUC held across 3 seeds (orig 0.6667)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58bb8ac84e7cd56f` | `104cd70fb0f5e1d3` | `104cd70fb0f5e1d3` | `104cd70fb0f5e1d3` |
| PR AUC | 0.6667 | 0.6667 | 0.6667 | 0.6667 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58bb8ac84e7cd56f
```
