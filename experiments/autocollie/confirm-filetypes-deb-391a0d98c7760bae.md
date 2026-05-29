# Confirm PASS — 391a0d98c7760bae on `filetypes/deb`

Cycle `20260526T203422-confirm-391a0d98c7760bae` — 2026-05-26T20:34:22Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `391a0d98c7760bae` | `8b4e28deb17b12dd` | `8b4e28deb17b12dd` | `8b4e28deb17b12dd` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=391a0d98c7760bae
```
