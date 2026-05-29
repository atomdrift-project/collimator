# Confirm PASS — bf2bf9c3898c628c on `filetypes/go`

Cycle `20260526T061017-confirm-bf2bf9c3898c628c` — 2026-05-26T06:10:17Z

PR_AUC held across 3 seeds (orig 0.9580)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bf2bf9c3898c628c` | `5fbe880affc0f2c2` | `5fbe880affc0f2c2` | `5fbe880affc0f2c2` |
| PR AUC | 0.9580 | 0.9593 | 0.9575 | 0.9588 |
| ROC AUC | 0.9857 | 0.9860 | 0.9860 | 0.9860 |
| Recall@3FPM | — | 0.5181 | 0.4880 | 0.4699 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bf2bf9c3898c628c
```
