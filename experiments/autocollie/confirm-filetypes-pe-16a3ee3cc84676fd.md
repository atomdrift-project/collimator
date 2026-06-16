# Confirm PASS — 16a3ee3cc84676fd on `filetypes/pe`

Cycle `20260616T015452-confirm-16a3ee3cc84676fd` — 2026-06-16T01:54:52Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `16a3ee3cc84676fd` | `adc50f6e3d05d34c` | `adc50f6e3d05d34c` | `adc50f6e3d05d34c` |
| PR AUC | 0.9990 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9998 | 0.9997 | 0.9998 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=16a3ee3cc84676fd
```
