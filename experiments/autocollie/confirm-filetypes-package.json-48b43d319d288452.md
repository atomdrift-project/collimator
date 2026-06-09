# Confirm PASS — 48b43d319d288452 on `filetypes/package.json`

Cycle `20260609T100812-confirm-48b43d319d288452` — 2026-06-09T10:08:12Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `48b43d319d288452` | `06f365ed02b06e4b` | `06f365ed02b06e4b` | `06f365ed02b06e4b` |
| PR AUC | 0.9988 | 0.9989 | 0.9987 | 0.9989 |
| ROC AUC | 0.9981 | 0.9984 | 0.9980 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=48b43d319d288452
```
