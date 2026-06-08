# Confirm PASS — 8f6871d453fc2eeb on `filetypes/shell`

Cycle `20260608T105206-confirm-8f6871d453fc2eeb` — 2026-06-08T10:52:06Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8f6871d453fc2eeb` | `98526bfce201bcaf` | `98526bfce201bcaf` | `98526bfce201bcaf` |
| PR AUC | 0.9983 | 0.9983 | 0.9983 | 0.9983 |
| ROC AUC | 0.9983 | 0.9983 | 0.9983 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8f6871d453fc2eeb
```
