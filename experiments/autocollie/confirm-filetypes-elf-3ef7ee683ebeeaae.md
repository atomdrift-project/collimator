# Confirm PASS — 3ef7ee683ebeeaae on `filetypes/elf`

Cycle `20260526T165530-confirm-3ef7ee683ebeeaae` — 2026-05-26T16:55:30Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3ef7ee683ebeeaae` | `73b5ccdee4c8e73b` | `73b5ccdee4c8e73b` | `73b5ccdee4c8e73b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9654 | 0.9831 | 0.9738 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3ef7ee683ebeeaae
```
