# Confirm PASS — 3cc86c5236b144f3 on `filetypes/ole`

Cycle `20260718T135438-confirm-3cc86c5236b144f3` — 2026-07-18T13:54:38Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3cc86c5236b144f3` | `23cf973f85e03eb4` | `23cf973f85e03eb4` | `23cf973f85e03eb4` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9990 | 0.9989 | 0.9989 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3cc86c5236b144f3
```
