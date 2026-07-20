# Confirm PASS — b703dab6e8f81514 on `filetypes/batch`

Cycle `20260710T195006-confirm-b703dab6e8f81514` — 2026-07-10T19:50:06Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b703dab6e8f81514` | `5806cfcb59cdcc89` | `5806cfcb59cdcc89` | `5806cfcb59cdcc89` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9988 | 0.9987 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b703dab6e8f81514
```
