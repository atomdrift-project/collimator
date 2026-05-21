# Confirm PASS — f5b18208c9a6b978 on `filegroups/source`

Cycle `20260521T024250-confirm-f5b18208c9a6b978` — 2026-05-21T02:42:50Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f5b18208c9a6b978` | `48dc36df1cdc75a9` | `48dc36df1cdc75a9` | `48dc36df1cdc75a9` |
| PR AUC | 0.9988 | 0.9988 | 0.9988 | 0.9988 |
| ROC AUC | 0.9982 | 0.9982 | 0.9981 | 0.9981 |
| Recall@3FPM | — | 0.9086 | 0.9101 | 0.8955 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f5b18208c9a6b978
```
