# Confirm PASS — 2d12df1fc1c87c02 on `filetypes/text`

Cycle `20260527T015247-confirm-2d12df1fc1c87c02` — 2026-05-27T01:52:47Z

PR_AUC held across 3 seeds (orig 0.9679)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2d12df1fc1c87c02` | `79b47489495f6ba7` | `79b47489495f6ba7` | `79b47489495f6ba7` |
| PR AUC | 0.9679 | 0.9488 | 0.9740 | 0.9672 |
| ROC AUC | 0.9843 | 0.9789 | 0.9881 | 0.9826 |
| Recall@3FPM | — | 0.5714 | 0.8095 | 0.8571 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2d12df1fc1c87c02
```
