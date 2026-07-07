# Confirm PASS — 022858952583fcf3 on `filegroups/media`

Cycle `20260706T042720-confirm-022858952583fcf3` — 2026-07-06T04:27:20Z

PR_AUC held across 3 seeds (orig 0.9863)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `022858952583fcf3` | `fbf8ae7ec2623857` | `fbf8ae7ec2623857` | `fbf8ae7ec2623857` |
| PR AUC | 0.9863 | 0.9890 | 0.9866 | 0.9890 |
| ROC AUC | 0.9803 | 0.9845 | 0.9817 | 0.9854 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=022858952583fcf3
```
