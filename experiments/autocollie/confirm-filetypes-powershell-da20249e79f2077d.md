# Confirm PASS — da20249e79f2077d on `filetypes/powershell`

Cycle `20260527T005313-confirm-da20249e79f2077d` — 2026-05-27T00:53:13Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `da20249e79f2077d` | `4a07be7346569775` | `4a07be7346569775` | `4a07be7346569775` |
| PR AUC | 0.9987 | 0.9987 | 0.9992 | 0.9981 |
| ROC AUC | 0.9967 | 0.9954 | 0.9973 | 0.9938 |
| Recall@3FPM | — | 0.8319 | 0.8348 | 0.7265 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=da20249e79f2077d
```
