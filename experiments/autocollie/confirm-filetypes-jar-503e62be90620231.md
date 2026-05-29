# Confirm PASS — 503e62be90620231 on `filetypes/jar`

Cycle `20260526T232651-confirm-503e62be90620231` — 2026-05-26T23:26:51Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `503e62be90620231` | `5f1d5dbe3b1e5ddc` | `5f1d5dbe3b1e5ddc` | `5f1d5dbe3b1e5ddc` |
| PR AUC | 0.9986 | 0.9971 | 0.9973 | 0.9982 |
| ROC AUC | 0.9973 | 0.9939 | 0.9948 | 0.9965 |
| Recall@3FPM | — | 0.8466 | 0.7955 | 0.8864 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=503e62be90620231
```
