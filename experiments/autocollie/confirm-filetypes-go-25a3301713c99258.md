# Confirm PASS — 25a3301713c99258 on `filetypes/go`

Cycle `20260526T075908-confirm-25a3301713c99258` — 2026-05-26T07:59:08Z

PR_AUC held across 3 seeds (orig 0.9601)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `25a3301713c99258` | `2223fd93c0e73dd4` | `2223fd93c0e73dd4` | `2223fd93c0e73dd4` |
| PR AUC | 0.9601 | 0.9713 | 0.9672 | 0.9713 |
| ROC AUC | 0.9871 | 0.9909 | 0.9898 | 0.9907 |
| Recall@3FPM | — | 0.5181 | 0.4157 | 0.5361 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=25a3301713c99258
```
