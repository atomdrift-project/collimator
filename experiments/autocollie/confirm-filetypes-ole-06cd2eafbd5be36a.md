# Confirm PASS — 06cd2eafbd5be36a on `filetypes/ole`

Cycle `20260713T101526-confirm-06cd2eafbd5be36a` — 2026-07-13T10:15:26Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `06cd2eafbd5be36a` | `d0d83cccbec8f2aa` | `d0d83cccbec8f2aa` | `d0d83cccbec8f2aa` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9989 | 0.9990 | 0.9990 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=06cd2eafbd5be36a
```
