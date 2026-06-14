# Confirm PASS — f1a86ac2e2b98d7c on `filegroups/source`

Cycle `20260614T011347-confirm-f1a86ac2e2b98d7c` — 2026-06-14T01:13:47Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f1a86ac2e2b98d7c` | `cc4ff294540b726f` | `cc4ff294540b726f` | `cc4ff294540b726f` |
| PR AUC | 0.9990 | 0.9974 | 0.9973 | 0.9974 |
| ROC AUC | 0.9982 | 0.9970 | 0.9969 | 0.9971 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f1a86ac2e2b98d7c
```
