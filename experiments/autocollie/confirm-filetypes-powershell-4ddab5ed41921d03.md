# Confirm PASS — 4ddab5ed41921d03 on `filetypes/powershell`

Cycle `20260614T013416-confirm-4ddab5ed41921d03` — 2026-06-14T01:34:16Z

PR_AUC held across 3 seeds (orig 0.9937)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4ddab5ed41921d03` | `0d29bffe2aacf680` | `0d29bffe2aacf680` | `0d29bffe2aacf680` |
| PR AUC | 0.9937 | 0.9931 | 0.9924 | 0.9928 |
| ROC AUC | 0.9847 | 0.9829 | 0.9812 | 0.9825 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4ddab5ed41921d03
```
