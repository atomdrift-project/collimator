# Confirm PASS — c95c5baf607561f8 on `filetypes/tar.gz`

Cycle `20260524T125652-confirm-c95c5baf607561f8` — 2026-05-24T12:56:52Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c95c5baf607561f8` | `679a6e6720691894` | `679a6e6720691894` | `679a6e6720691894` |
| PR AUC | 0.9994 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9987 | 0.9987 | 0.9987 | 0.9988 |
| Recall@3FPM | — | 0.6644 | 0.7025 | 0.7484 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c95c5baf607561f8
```
