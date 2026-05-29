# Confirm PASS — 3deb9da849287e99 on `filegroups/portable`

Cycle `20260527T012039-confirm-3deb9da849287e99` — 2026-05-27T01:20:39Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3deb9da849287e99` | `35b134d7010f1bad` | `35b134d7010f1bad` | `35b134d7010f1bad` |
| PR AUC | 0.9968 | 0.9964 | 0.9957 | 0.9968 |
| ROC AUC | 0.9992 | 0.9991 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.8533 | 0.7667 | 0.8600 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3deb9da849287e99
```
