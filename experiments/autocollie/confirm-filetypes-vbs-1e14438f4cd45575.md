# Confirm PASS — 1e14438f4cd45575 on `filetypes/vbs`

Cycle `20260613T233151-confirm-1e14438f4cd45575` — 2026-06-13T23:31:51Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1e14438f4cd45575` | `d4113df60f302ce9` | `d4113df60f302ce9` | `d4113df60f302ce9` |
| PR AUC | 0.9964 | 0.9970 | 0.9969 | 0.9973 |
| ROC AUC | 0.9874 | 0.9889 | 0.9888 | 0.9903 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1e14438f4cd45575
```
