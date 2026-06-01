# Confirm PASS — 956e522f2c6a5ae2 on `filegroups/scripts`

Cycle `20260601T151228-confirm-956e522f2c6a5ae2` — 2026-06-01T15:12:28Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `956e522f2c6a5ae2` | `0ac614e99534eb16` | `0ac614e99534eb16` | `0ac614e99534eb16` |
| PR AUC | 0.9981 | 0.9988 | 0.9987 | 0.9987 |
| ROC AUC | 0.9979 | 0.9985 | 0.9985 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=956e522f2c6a5ae2
```
