# Confirm PASS — 62dfa163eeed37e2 on `filetypes/go`

Cycle `20260616T094740-confirm-62dfa163eeed37e2` — 2026-06-16T09:47:40Z

PR_AUC held across 3 seeds (orig 0.9404)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `62dfa163eeed37e2` | `6c24c776d26e937d` | `6c24c776d26e937d` | `6c24c776d26e937d` |
| PR AUC | 0.9404 | 0.9324 | 0.9405 | 0.9376 |
| ROC AUC | 0.9872 | 0.9840 | 0.9863 | 0.9864 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=62dfa163eeed37e2
```
