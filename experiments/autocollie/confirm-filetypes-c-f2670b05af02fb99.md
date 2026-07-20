# Confirm PASS — f2670b05af02fb99 on `filetypes/c`

Cycle `20260718T140822-confirm-f2670b05af02fb99` — 2026-07-18T14:08:22Z

PR_AUC held across 3 seeds (orig 0.9769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f2670b05af02fb99` | `4c6f61626369400e` | `4c6f61626369400e` | `4c6f61626369400e` |
| PR AUC | 0.9769 | 0.9782 | 0.9777 | 0.9788 |
| ROC AUC | 0.9924 | 0.9928 | 0.9930 | 0.9931 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f2670b05af02fb99
```
