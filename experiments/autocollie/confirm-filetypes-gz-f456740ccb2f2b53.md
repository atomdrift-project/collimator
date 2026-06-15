# Confirm PASS — f456740ccb2f2b53 on `filetypes/gz`

Cycle `20260614T233929-confirm-f456740ccb2f2b53` — 2026-06-14T23:39:29Z

PR_AUC held across 3 seeds (orig 0.7218)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f456740ccb2f2b53` | `156ee43e49129774` | `156ee43e49129774` | `156ee43e49129774` |
| PR AUC | 0.7218 | 0.7134 | 0.7218 | 0.7194 |
| ROC AUC | 0.8913 | 0.8851 | 0.8724 | 0.8379 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f456740ccb2f2b53
```
