# Confirm PASS — cad3a137090e6b9f on `filetypes/shell`

Cycle `20260601T145234-confirm-cad3a137090e6b9f` — 2026-06-01T14:52:34Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cad3a137090e6b9f` | `863ec3caf3fc86ae` | `863ec3caf3fc86ae` | `863ec3caf3fc86ae` |
| PR AUC | 0.9960 | 0.9985 | 0.9985 | 0.9985 |
| ROC AUC | 0.9974 | 0.9986 | 0.9987 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cad3a137090e6b9f
```
