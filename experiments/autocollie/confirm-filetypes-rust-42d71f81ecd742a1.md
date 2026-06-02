# Confirm PASS — 42d71f81ecd742a1 on `filetypes/rust`

Cycle `20260602T013748-confirm-42d71f81ecd742a1` — 2026-06-02T01:37:48Z

PR_AUC held across 3 seeds (orig 0.9279)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `42d71f81ecd742a1` | `516845e985d1a6ec` | `516845e985d1a6ec` | `516845e985d1a6ec` |
| PR AUC | 0.9279 | 0.9317 | 0.9368 | 0.9448 |
| ROC AUC | 0.9909 | 0.9922 | 0.9936 | 0.9945 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=42d71f81ecd742a1
```
