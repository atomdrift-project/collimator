# Confirm PASS — cea25fee1d916b0b on `filetypes/package.json`

Cycle `20260525T181841-confirm-cea25fee1d916b0b` — 2026-05-25T18:18:41Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cea25fee1d916b0b` | `f03bdb386f32aee5` | `f03bdb386f32aee5` | `f03bdb386f32aee5` |
| PR AUC | 0.9998 | 0.9998 | 0.9997 | 0.9996 |
| ROC AUC | 0.9996 | 0.9996 | 0.9994 | 0.9991 |
| Recall@3FPM | — | 0.9590 | 0.9695 | 0.9660 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cea25fee1d916b0b
```
