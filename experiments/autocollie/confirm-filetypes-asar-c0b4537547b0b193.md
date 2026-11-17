# Confirm PASS — c0b4537547b0b193 on `filetypes/asar`

Cycle `20261112T203943-confirm-c0b4537547b0b193` — 2026-11-12T20:39:43Z

averaged 3-seed ensemble PR_AUC held: 1.0000 -> 1.0000; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c0b4537547b0b193` | `da48c181cd583e47` | `da48c181cd583e47` | `da48c181cd583e47` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@L50 | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c0b4537547b0b193
```
