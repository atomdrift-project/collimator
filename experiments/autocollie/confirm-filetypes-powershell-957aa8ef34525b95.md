# Confirm PASS — 957aa8ef34525b95 on `filetypes/powershell`

Cycle `20260609T094918-confirm-957aa8ef34525b95` — 2026-06-09T09:49:18Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `957aa8ef34525b95` | `e43dd677b2121f05` | `e43dd677b2121f05` | `e43dd677b2121f05` |
| PR AUC | 0.9994 | 0.9989 | 0.9993 | 0.9993 |
| ROC AUC | 0.9968 | 0.9940 | 0.9961 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=957aa8ef34525b95
```
