# Confirm PASS — 9071b393c5cb8e3b on `filetypes/powershell`

Cycle `20260606T151236-confirm-9071b393c5cb8e3b` — 2026-06-06T15:12:36Z

PR_AUC held across 3 seeds (orig 0.9955)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9071b393c5cb8e3b` | `6f6354df0865d361` | `6f6354df0865d361` | `6f6354df0865d361` |
| PR AUC | 0.9955 | 0.9950 | 0.9950 | 0.9939 |
| ROC AUC | 0.9894 | 0.9882 | 0.9883 | 0.9864 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9071b393c5cb8e3b
```
