# Confirm PASS — afe8e45711262e8b on `filetypes/msi`

Cycle `20260526T215322-confirm-afe8e45711262e8b` — 2026-05-26T21:53:22Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `afe8e45711262e8b` | `f14635c1299c0a01` | `f14635c1299c0a01` | `f14635c1299c0a01` |
| PR AUC | 0.9999 | 0.9999 | 0.9998 | 0.9999 |
| ROC AUC | 0.9973 | 0.9980 | 0.9933 | 0.9973 |
| Recall@3FPM | — | 0.9967 | 0.9800 | 0.9900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=afe8e45711262e8b
```
