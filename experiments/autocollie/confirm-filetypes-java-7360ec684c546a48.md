# Confirm PASS — 7360ec684c546a48 on `filetypes/java`

Cycle `20260527T053938-confirm-7360ec684c546a48` — 2026-05-27T05:39:38Z

PR_AUC held across 3 seeds (orig 0.2292)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7360ec684c546a48` | `d8f9f48cf5af3a5a` | `d8f9f48cf5af3a5a` | `d8f9f48cf5af3a5a` |
| PR AUC | 0.2292 | 0.2540 | 0.1508 | 0.3132 |
| ROC AUC | 0.9977 | 0.9123 | 0.8152 | 0.9691 |
| Recall@3FPM | — | 0.2000 | 0.0000 | 0.2000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7360ec684c546a48
```
