# Confirm PASS — 5d9c9f691b94f6a0 on `filetypes/powershell`

Cycle `20260602T013118-confirm-5d9c9f691b94f6a0` — 2026-06-02T01:31:18Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5d9c9f691b94f6a0` | `7ff7147885849778` | `7ff7147885849778` | `7ff7147885849778` |
| PR AUC | 0.9989 | 0.9989 | 0.9994 | 0.9993 |
| ROC AUC | 0.9961 | 0.9944 | 0.9969 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5d9c9f691b94f6a0
```
