# Confirm PASS — 699643fbb39b79fd on `filetypes/c`

Cycle `20260526T040214-confirm-699643fbb39b79fd` — 2026-05-26T04:02:14Z

PR_AUC held across 3 seeds (orig 0.9918)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `699643fbb39b79fd` | `f648f66064d45745` | `f648f66064d45745` | `f648f66064d45745` |
| PR AUC | 0.9918 | 0.9928 | 0.9926 | 0.9921 |
| ROC AUC | 0.9957 | 0.9963 | 0.9961 | 0.9958 |
| Recall@3FPM | — | 0.8009 | 0.7847 | 0.8218 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=699643fbb39b79fd
```
