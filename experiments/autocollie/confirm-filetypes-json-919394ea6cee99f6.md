# Confirm PASS — 919394ea6cee99f6 on `filetypes/json`

Cycle `20260723T061939-confirm-919394ea6cee99f6` — 2026-07-23T06:19:39Z

PR_AUC held across 3 seeds (orig 0.9682)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `919394ea6cee99f6` | `2ad0f4e4acd7d6e3` | `2ad0f4e4acd7d6e3` | `2ad0f4e4acd7d6e3` |
| PR AUC | 0.9682 | 0.9623 | 0.9649 | 0.9684 |
| ROC AUC | 0.9746 | 0.9643 | 0.9675 | 0.9754 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=919394ea6cee99f6
```
