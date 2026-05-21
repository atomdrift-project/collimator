# Confirm PASS — 589b9b4aec45069c on `filegroups/documents`

Cycle `20260520T193032-confirm-589b9b4aec45069c` — 2026-05-20T19:30:32Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `589b9b4aec45069c` | `bb6124eb5d3ce754` | `bb6124eb5d3ce754` | `bb6124eb5d3ce754` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9985 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.9850 | 0.9842 | 0.9826 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=589b9b4aec45069c
```
