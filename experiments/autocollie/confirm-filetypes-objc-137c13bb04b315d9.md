# Confirm PASS — 137c13bb04b315d9 on `filetypes/objc`

Cycle `20260527T072147-confirm-137c13bb04b315d9` — 2026-05-27T07:21:47Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `137c13bb04b315d9` | `89a023b41c672e9b` | `89a023b41c672e9b` | `89a023b41c672e9b` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=137c13bb04b315d9
```
