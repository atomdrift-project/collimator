# Confirm PASS — 96772bac6c4e10cc on `filegroups/config`

Cycle `20260613T013419-confirm-96772bac6c4e10cc` — 2026-06-13T01:34:19Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `96772bac6c4e10cc` | `b65004afdd6782ff` | `b65004afdd6782ff` | `b65004afdd6782ff` |
| PR AUC | 0.9989 | 0.9988 | 0.9989 | 0.9989 |
| ROC AUC | 0.9986 | 0.9984 | 0.9984 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=96772bac6c4e10cc
```
