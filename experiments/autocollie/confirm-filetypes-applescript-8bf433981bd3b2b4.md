# Confirm PASS — 8bf433981bd3b2b4 on `filetypes/applescript`

Cycle `20260526T214649-confirm-8bf433981bd3b2b4` — 2026-05-26T21:46:49Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8bf433981bd3b2b4` | `839a7e4c27ac4b33` | `839a7e4c27ac4b33` | `839a7e4c27ac4b33` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8bf433981bd3b2b4
```
