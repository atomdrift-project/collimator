# Confirm PASS — 63f5609454081e18 on `filegroups/config`

Cycle `20260713T055018-confirm-63f5609454081e18` — 2026-07-13T05:50:18Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `63f5609454081e18` | `60d364f3f06c11cc` | `60d364f3f06c11cc` | `60d364f3f06c11cc` |
| PR AUC | 0.9977 | 0.9977 | 0.9977 | 0.9975 |
| ROC AUC | 0.9981 | 0.9979 | 0.9980 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63f5609454081e18
```
