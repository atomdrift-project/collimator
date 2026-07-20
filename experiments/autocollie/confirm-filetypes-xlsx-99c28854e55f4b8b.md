# Confirm PASS — 99c28854e55f4b8b on `filetypes/xlsx`

Cycle `20260720T112945-confirm-99c28854e55f4b8b` — 2026-07-20T11:29:45Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `99c28854e55f4b8b` | `9770c8db23ec9109` | `9770c8db23ec9109` | `9770c8db23ec9109` |
| PR AUC | 0.9953 | 0.9953 | 0.9953 | 0.9953 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=99c28854e55f4b8b
```
