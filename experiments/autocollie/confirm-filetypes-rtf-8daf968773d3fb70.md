# Confirm PASS — 8daf968773d3fb70 on `filetypes/rtf`

Cycle `20260527T071444-confirm-8daf968773d3fb70` — 2026-05-27T07:14:44Z

PR_AUC held across 3 seeds (orig 0.9784)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8daf968773d3fb70` | `99c4f0b9554f2fa9` | `99c4f0b9554f2fa9` | `99c4f0b9554f2fa9` |
| PR AUC | 0.9784 | 0.9784 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8daf968773d3fb70
```
