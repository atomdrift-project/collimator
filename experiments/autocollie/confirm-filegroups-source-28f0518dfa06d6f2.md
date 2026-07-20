# Confirm PASS — 28f0518dfa06d6f2 on `filegroups/source`

Cycle `20260718T142117-confirm-28f0518dfa06d6f2` — 2026-07-18T14:21:17Z

PR_AUC held across 3 seeds (orig 0.9938)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `28f0518dfa06d6f2` | `f5ffb41fa55adfda` | `f5ffb41fa55adfda` | `f5ffb41fa55adfda` |
| PR AUC | 0.9938 | 0.9950 | 0.9952 | 0.9951 |
| ROC AUC | 0.9958 | 0.9964 | 0.9965 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=28f0518dfa06d6f2
```
