# Confirm PASS — 0e3f60c275a946e9 on `filetypes/shell`

Cycle `20260528T123737-confirm-0e3f60c275a946e9` — 2026-05-28T12:37:37Z

PR_AUC held across 3 seeds (orig 0.9962)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0e3f60c275a946e9` | `9ae91121fcc0438e` | `9ae91121fcc0438e` | `9ae91121fcc0438e` |
| PR AUC | 0.9962 | 0.9967 | 0.9969 | 0.9961 |
| ROC AUC | 0.9975 | 0.9979 | 0.9980 | 0.9975 |
| Recall@3FPM | — | 0.8608 | 0.8919 | 0.8555 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0e3f60c275a946e9
```
