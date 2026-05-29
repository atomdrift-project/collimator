# Confirm PASS — 74e05df8520419b9 on `filetypes/groovy`

Cycle `20260525T213201-confirm-74e05df8520419b9` — 2026-05-25T21:32:01Z

PR_AUC held across 3 seeds (orig 0.0016)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `74e05df8520419b9` | `d4e099b7fb22938b` | `d4e099b7fb22938b` | `d4e099b7fb22938b` |
| PR AUC | 0.0016 | 0.9205 | 0.9210 | 0.9156 |
| ROC AUC | 0.5000 | 0.9549 | 0.9532 | 0.9580 |
| Recall@3FPM | — | 0.7778 | 0.7778 | 0.7778 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=74e05df8520419b9
```
