# Confirm PASS — 446d38a6c7fc1502 on `filetypes/package.json`

Cycle `20260616T054352-confirm-446d38a6c7fc1502` — 2026-06-16T05:43:52Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `446d38a6c7fc1502` | `bf4cf47bfe4cf487` | `bf4cf47bfe4cf487` | `bf4cf47bfe4cf487` |
| PR AUC | 0.9988 | 0.9989 | 0.9989 | 0.9988 |
| ROC AUC | 0.9983 | 0.9983 | 0.9985 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=446d38a6c7fc1502
```
