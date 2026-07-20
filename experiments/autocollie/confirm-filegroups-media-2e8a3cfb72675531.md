# Confirm PASS — 2e8a3cfb72675531 on `filegroups/media`

Cycle `20260710T202627-confirm-2e8a3cfb72675531` — 2026-07-10T20:26:27Z

PR_AUC held across 3 seeds (orig 0.9857)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2e8a3cfb72675531` | `a25e32cbdf6fb876` | `a25e32cbdf6fb876` | `a25e32cbdf6fb876` |
| PR AUC | 0.9857 | 0.9890 | 0.9870 | 0.9873 |
| ROC AUC | 0.9782 | 0.9832 | 0.9806 | 0.9811 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2e8a3cfb72675531
```
