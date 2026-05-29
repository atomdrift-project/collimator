# Confirm PASS — 1db5975dd22d3071 on `filetypes/pkg-info`

Cycle `20260527T063235-confirm-1db5975dd22d3071` — 2026-05-27T06:32:35Z

PR_AUC held across 3 seeds (orig 0.9767)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1db5975dd22d3071` | `e966a856d186d8ff` | `e966a856d186d8ff` | `e966a856d186d8ff` |
| PR AUC | 0.9767 | 0.9941 | 0.9941 | 0.9941 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1db5975dd22d3071
```
