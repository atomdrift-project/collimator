# Confirm PASS — 0cf4d619755db863 on `filetypes/registry`

Cycle `20261115T140602-confirm-0cf4d619755db863` — 2026-11-15T14:06:02Z

averaged 3-seed ensemble PR_AUC held: 0.9649 -> 0.9718; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0cf4d619755db863` | `51a4023fb13e6db9` | `51a4023fb13e6db9` | `51a4023fb13e6db9` |
| PR AUC | 0.9649 | 0.9726 | 0.9702 | 0.9677 |
| ROC AUC | 0.9997 | 0.9998 | 0.9998 | 0.9998 |
| Recall@L50 | — | 0.8364 | 0.8364 | 0.8364 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0cf4d619755db863
```
