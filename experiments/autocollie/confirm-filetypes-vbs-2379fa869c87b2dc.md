# Confirm PASS — 2379fa869c87b2dc on `filetypes/vbs`

Cycle `20260804T221935-confirm-2379fa869c87b2dc` — 2026-08-04T22:19:35Z

PR_AUC held across 3 seeds (orig 0.9980)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2379fa869c87b2dc` | `1d9354f1f8205ac9` | `1d9354f1f8205ac9` | `1d9354f1f8205ac9` |
| PR AUC | 0.9980 | 0.9981 | 0.9989 | 0.9987 |
| ROC AUC | 0.9924 | 0.9930 | 0.9961 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2379fa869c87b2dc
```
