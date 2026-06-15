# Confirm PASS — 35d28c48fcf9b403 on `filetypes/macho`

Cycle `20260614T234455-confirm-35d28c48fcf9b403` — 2026-06-14T23:44:55Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `35d28c48fcf9b403` | `ec1a5cdb366a4509` | `ec1a5cdb366a4509` | `ec1a5cdb366a4509` |
| PR AUC | 0.9966 | 0.9971 | 0.9974 | 0.9958 |
| ROC AUC | 0.9993 | 0.9994 | 0.9994 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=35d28c48fcf9b403
```
