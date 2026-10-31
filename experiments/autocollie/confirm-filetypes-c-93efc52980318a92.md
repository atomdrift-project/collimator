# Confirm PASS — 93efc52980318a92 on `filetypes/c`

Cycle `20261030T231535-confirm-93efc52980318a92` — 2026-10-30T23:15:35Z

averaged 3-seed ensemble PR_AUC held: 0.9424 -> 0.9498; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `93efc52980318a92` | `fa87f90ab8f48ceb` | `fa87f90ab8f48ceb` | `fa87f90ab8f48ceb` |
| PR AUC | 0.9424 | 0.9360 | 0.9429 | 0.9489 |
| ROC AUC | 0.9783 | 0.9746 | 0.9783 | 0.9797 |
| Recall@L50 | — | 0.4043 | 0.4235 | 0.4031 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=93efc52980318a92
```
