# Confirm PASS — 3bc85353e94c764d on `filetypes/csharp`

Cycle `20260710T175815-confirm-3bc85353e94c764d` — 2026-07-10T17:58:15Z

PR_AUC held across 3 seeds (orig 0.9908)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3bc85353e94c764d` | `d80a6213bd447b34` | `d80a6213bd447b34` | `d80a6213bd447b34` |
| PR AUC | 0.9908 | 0.9895 | 0.9897 | 0.9896 |
| ROC AUC | 0.9973 | 0.9966 | 0.9969 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3bc85353e94c764d
```
