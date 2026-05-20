# Confirm PASS — e77c6bd1c31c65ea on `filetypes/text`

Cycle `20260519T204925-confirm-e77c6bd1c31c65ea` — 2026-05-19T20:49:25Z

PR_AUC held across 3 seeds (orig 0.9564)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e77c6bd1c31c65ea` | `2e3438bc669b3ab2` | `2e3438bc669b3ab2` | `2e3438bc669b3ab2` |
| PR AUC | 0.9564 | 0.9305 | 0.9525 | 0.9456 |
| ROC AUC | 0.9764 | 0.9672 | 0.9729 | 0.9694 |
| Recall@3FPM | — | 0.5909 | 0.7727 | 0.7273 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e77c6bd1c31c65ea
```
