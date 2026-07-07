# Confirm PASS — 428f9ae28383bad9 on `filetypes/kotlin`

Cycle `20260705T160206-confirm-428f9ae28383bad9` — 2026-07-05T16:02:06Z

PR_AUC held across 3 seeds (orig 0.9714)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `428f9ae28383bad9` | `1da88a5d02e345a9` | `1da88a5d02e345a9` | `1da88a5d02e345a9` |
| PR AUC | 0.9714 | 0.9773 | 0.9751 | 0.9692 |
| ROC AUC | 0.9815 | 0.9854 | 0.9862 | 0.9812 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=428f9ae28383bad9
```
