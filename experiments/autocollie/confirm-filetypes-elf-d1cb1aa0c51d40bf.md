# Confirm PASS — d1cb1aa0c51d40bf on `filetypes/elf`

Cycle `20260607T024541-confirm-d1cb1aa0c51d40bf` — 2026-06-07T02:45:41Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1cb1aa0c51d40bf` | `fcac0203cff3feb9` | `fcac0203cff3feb9` | `fcac0203cff3feb9` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1cb1aa0c51d40bf
```
