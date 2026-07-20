# Confirm PASS — 9444720bdc753036 on `filetypes/jpeg`

Cycle `20260718T134915-confirm-9444720bdc753036` — 2026-07-18T13:49:15Z

PR_AUC held across 3 seeds (orig 0.9800)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9444720bdc753036` | `286e432b15ffe3a0` | `286e432b15ffe3a0` | `286e432b15ffe3a0` |
| PR AUC | 0.9800 | 0.9788 | 0.9764 | 0.9815 |
| ROC AUC | 0.9776 | 0.9820 | 0.9767 | 0.9798 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9444720bdc753036
```
