# Confirm PASS — 8246c6d1fb9f1fe4 on `filetypes/vbs`

Cycle `20260609T045038-confirm-8246c6d1fb9f1fe4` — 2026-06-09T04:50:38Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8246c6d1fb9f1fe4` | `beef86f69a70a488` | `beef86f69a70a488` | `beef86f69a70a488` |
| PR AUC | 0.9968 | 0.9970 | 0.9977 | 0.9973 |
| ROC AUC | 0.9887 | 0.9897 | 0.9923 | 0.9905 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8246c6d1fb9f1fe4
```
