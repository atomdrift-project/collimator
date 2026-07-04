# Confirm PASS — 6e55fdb4dfb4cbaf on `filetypes/powershell`

Cycle `20260704T143302-confirm-6e55fdb4dfb4cbaf` — 2026-07-04T14:33:02Z

PR_AUC held across 3 seeds (orig 0.9931)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6e55fdb4dfb4cbaf` | `4392b29d2460bd1b` | `4392b29d2460bd1b` | `4392b29d2460bd1b` |
| PR AUC | 0.9931 | 0.9916 | 0.9914 | 0.9913 |
| ROC AUC | 0.9834 | 0.9851 | 0.9850 | 0.9851 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6e55fdb4dfb4cbaf
```
