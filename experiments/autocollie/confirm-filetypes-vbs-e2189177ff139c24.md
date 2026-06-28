# Confirm PASS — e2189177ff139c24 on `filetypes/vbs`

Cycle `20260628T061633-confirm-e2189177ff139c24` — 2026-06-28T06:16:33Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e2189177ff139c24` | `d02bef8331ddc1e7` | `d02bef8331ddc1e7` | `d02bef8331ddc1e7` |
| PR AUC | 0.9964 | 0.9964 | 0.9966 | 0.9965 |
| ROC AUC | 0.9865 | 0.9868 | 0.9877 | 0.9873 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e2189177ff139c24
```
