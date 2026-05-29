# Confirm PASS — c447cb1a7df034c9 on `filegroups/media`

Cycle `20260527T004544-confirm-c447cb1a7df034c9` — 2026-05-27T00:45:44Z

PR_AUC held across 3 seeds (orig 0.9952)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c447cb1a7df034c9` | `07126685e449636f` | `07126685e449636f` | `07126685e449636f` |
| PR AUC | 0.9952 | 0.9952 | 0.9957 | 0.9961 |
| ROC AUC | 0.9942 | 0.9941 | 0.9948 | 0.9952 |
| Recall@3FPM | — | 0.9111 | 0.8889 | 0.9222 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c447cb1a7df034c9
```
