# Confirm PASS — 678cc3f1890eb879 on `filetypes/jar`

Cycle `20260608T103919-confirm-678cc3f1890eb879` — 2026-06-08T10:39:19Z

PR_AUC held across 3 seeds (orig 0.9964)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `678cc3f1890eb879` | `a139ed9d01e7ddbf` | `a139ed9d01e7ddbf` | `a139ed9d01e7ddbf` |
| PR AUC | 0.9964 | 0.9956 | 0.9944 | 0.9930 |
| ROC AUC | 0.9916 | 0.9894 | 0.9873 | 0.9835 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=678cc3f1890eb879
```
