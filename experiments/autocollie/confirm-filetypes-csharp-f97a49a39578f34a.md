# Confirm PASS — f97a49a39578f34a on `filetypes/csharp`

Cycle `20260609T134212-confirm-f97a49a39578f34a` — 2026-06-09T13:42:12Z

PR_AUC held across 3 seeds (orig 0.4899)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f97a49a39578f34a` | `916a89c0cec1b69c` | `916a89c0cec1b69c` | `916a89c0cec1b69c` |
| PR AUC | 0.4899 | 0.4995 | 0.5528 | 0.5336 |
| ROC AUC | 0.9276 | 0.9263 | 0.9261 | 0.9242 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f97a49a39578f34a
```
