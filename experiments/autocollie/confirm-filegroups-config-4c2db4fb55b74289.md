# Confirm PASS — 4c2db4fb55b74289 on `filegroups/config`

Cycle `20260617T182712-confirm-4c2db4fb55b74289` — 2026-06-17T18:27:12Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4c2db4fb55b74289` | `4b5fef256d1f0f76` | `4b5fef256d1f0f76` | `4b5fef256d1f0f76` |
| PR AUC | 0.9986 | 0.9986 | 0.9989 | 0.9989 |
| ROC AUC | 0.9980 | 0.9981 | 0.9985 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4c2db4fb55b74289
```
