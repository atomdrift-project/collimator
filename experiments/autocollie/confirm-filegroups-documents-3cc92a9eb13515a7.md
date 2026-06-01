# Confirm PASS — 3cc92a9eb13515a7 on `filegroups/documents`

Cycle `20260601T132912-confirm-3cc92a9eb13515a7` — 2026-06-01T13:29:12Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3cc92a9eb13515a7` | `d3d62a38e1f456ec` | `d3d62a38e1f456ec` | `d3d62a38e1f456ec` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9993 | 0.9993 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3cc92a9eb13515a7
```
