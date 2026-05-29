# Confirm PASS — 539e726b0ffdefc7 on `filetypes/lnk`

Cycle `20260525T203649-confirm-539e726b0ffdefc7` — 2026-05-25T20:36:49Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `539e726b0ffdefc7` | `275171dc78633755` | `275171dc78633755` | `275171dc78633755` |
| PR AUC | 0.9990 | 0.9994 | 0.9992 | 0.9990 |
| ROC AUC | 0.9869 | 0.9925 | 0.9891 | 0.9867 |
| Recall@3FPM | — | 0.9590 | 0.9590 | 0.9692 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=539e726b0ffdefc7
```
