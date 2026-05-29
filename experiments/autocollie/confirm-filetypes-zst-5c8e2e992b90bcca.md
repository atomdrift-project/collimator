# Confirm PASS — 5c8e2e992b90bcca on `filetypes/zst`

Cycle `20260526T185930-confirm-5c8e2e992b90bcca` — 2026-05-26T18:59:30Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5c8e2e992b90bcca` | `cf1fb4fc8b10016c` | `cf1fb4fc8b10016c` | `cf1fb4fc8b10016c` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5c8e2e992b90bcca
```
