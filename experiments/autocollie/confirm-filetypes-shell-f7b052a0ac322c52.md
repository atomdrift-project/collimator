# Confirm PASS — f7b052a0ac322c52 on `filetypes/shell`

Cycle `20260522T192524-confirm-f7b052a0ac322c52` — 2026-05-22T19:25:24Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f7b052a0ac322c52` | `5882e274d2581d97` | `5882e274d2581d97` | `5882e274d2581d97` |
| PR AUC | 0.9966 | 0.9960 | 0.9968 | 0.9967 |
| ROC AUC | 0.9980 | 0.9976 | 0.9981 | 0.9980 |
| Recall@3FPM | — | 0.8379 | 0.8651 | 0.8342 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f7b052a0ac322c52
```
