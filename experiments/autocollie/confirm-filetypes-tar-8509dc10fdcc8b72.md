# Confirm PASS — 8509dc10fdcc8b72 on `filetypes/tar`

Cycle `20260526T212225-confirm-8509dc10fdcc8b72` — 2026-05-26T21:22:25Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8509dc10fdcc8b72` | `6536f4c61ea1474f` | `6536f4c61ea1474f` | `6536f4c61ea1474f` |
| PR AUC | 1.0000 | 0.9996 | 0.9990 | 0.9997 |
| ROC AUC | 1.0000 | 0.9967 | 0.9905 | 0.9974 |
| Recall@3FPM | — | 0.9605 | 0.9868 | 0.9737 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8509dc10fdcc8b72
```
