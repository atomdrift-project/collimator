# Confirm PASS — cc7f6a3db60edfb5 on `filetypes/c`

Cycle `20260602T002828-confirm-cc7f6a3db60edfb5` — 2026-06-02T00:28:28Z

PR_AUC held across 3 seeds (orig 0.9898)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc7f6a3db60edfb5` | `6861905247893340` | `6861905247893340` | `6861905247893340` |
| PR AUC | 0.9898 | 0.9872 | 0.9868 | 0.9876 |
| ROC AUC | 0.9944 | 0.9938 | 0.9935 | 0.9940 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cc7f6a3db60edfb5
```
