# Confirm PASS — bd9de0197bbd15c5 on `filegroups/documents`

Cycle `20260825T204644-confirm-bd9de0197bbd15c5` — 2026-08-25T20:46:44Z

PR_AUC held across 3 seeds (orig 0.9822)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bd9de0197bbd15c5` | `29dafb698cb8ede2` | `29dafb698cb8ede2` | `29dafb698cb8ede2` |
| PR AUC | 0.9822 | 0.9967 | 0.9960 | 0.9964 |
| ROC AUC | 0.9795 | 0.9910 | 0.9892 | 0.9905 |
| Recall@L50 | — | 0.7043 | 0.7156 | 0.7188 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bd9de0197bbd15c5
```
