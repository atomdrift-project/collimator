# Confirm PASS — 8e48ff88d2da2618 on `filetypes/jpeg`

Cycle `20260613T012205-confirm-8e48ff88d2da2618` — 2026-06-13T01:22:05Z

PR_AUC held across 3 seeds (orig 0.9507)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8e48ff88d2da2618` | `2441c4a2ff3a1d98` | `2441c4a2ff3a1d98` | `2441c4a2ff3a1d98` |
| PR AUC | 0.9507 | 0.9562 | 0.9546 | 0.9555 |
| ROC AUC | 0.9743 | 0.9764 | 0.9750 | 0.9777 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8e48ff88d2da2618
```
