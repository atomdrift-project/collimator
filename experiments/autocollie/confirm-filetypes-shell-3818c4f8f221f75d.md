# Confirm PASS — 3818c4f8f221f75d on `filetypes/shell`

Cycle `20260613T185023-confirm-3818c4f8f221f75d` — 2026-06-13T18:50:23Z

PR_AUC held across 3 seeds (orig 0.9963)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3818c4f8f221f75d` | `0597f9f531653ef9` | `0597f9f531653ef9` | `0597f9f531653ef9` |
| PR AUC | 0.9963 | 0.9969 | 0.9969 | 0.9971 |
| ROC AUC | 0.9976 | 0.9971 | 0.9971 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3818c4f8f221f75d
```
