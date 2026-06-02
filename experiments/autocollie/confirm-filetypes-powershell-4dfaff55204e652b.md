# Confirm PASS — 4dfaff55204e652b on `filetypes/powershell`

Cycle `20260602T013145-confirm-4dfaff55204e652b` — 2026-06-02T01:31:45Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4dfaff55204e652b` | `9d67b9e79c7723b9` | `9d67b9e79c7723b9` | `9d67b9e79c7723b9` |
| PR AUC | 0.9992 | 0.9996 | 0.9995 | 0.9987 |
| ROC AUC | 0.9988 | 0.9992 | 0.9991 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4dfaff55204e652b
```
