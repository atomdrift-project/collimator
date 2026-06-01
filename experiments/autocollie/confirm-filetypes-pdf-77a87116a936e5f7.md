# Confirm PASS — 77a87116a936e5f7 on `filetypes/pdf`

Cycle `20260601T125837-confirm-77a87116a936e5f7` — 2026-06-01T12:58:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `77a87116a936e5f7` | `0749eed6b506f721` | `0749eed6b506f721` | `0749eed6b506f721` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9990 | 0.9983 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=77a87116a936e5f7
```
