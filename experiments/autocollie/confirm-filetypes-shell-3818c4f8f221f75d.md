# Confirm PASS — 3818c4f8f221f75d on `filetypes/shell`

Cycle `20260601T145233-confirm-3818c4f8f221f75d` — 2026-06-01T14:52:33Z

PR_AUC held across 3 seeds (orig 0.9963)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3818c4f8f221f75d` | `4b17289988f59346` | `4b17289988f59346` | `4b17289988f59346` |
| PR AUC | 0.9963 | 0.9986 | 0.9985 | 0.9985 |
| ROC AUC | 0.9976 | 0.9987 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3818c4f8f221f75d
```
