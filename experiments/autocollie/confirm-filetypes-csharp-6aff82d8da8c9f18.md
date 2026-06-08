# Confirm PASS — 6aff82d8da8c9f18 on `filetypes/csharp`

Cycle `20260608T160322-confirm-6aff82d8da8c9f18` — 2026-06-08T16:03:22Z

PR_AUC held across 3 seeds (orig 0.4832)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6aff82d8da8c9f18` | `950eb2255ef83354` | `950eb2255ef83354` | `950eb2255ef83354` |
| PR AUC | 0.4832 | 0.5338 | 0.4957 | 0.5355 |
| ROC AUC | 0.9139 | 0.9246 | 0.9156 | 0.9273 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6aff82d8da8c9f18
```
