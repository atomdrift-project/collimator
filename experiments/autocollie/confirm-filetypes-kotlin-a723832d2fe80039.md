# Confirm PASS — a723832d2fe80039 on `filetypes/kotlin`

Cycle `20260804T230513-confirm-a723832d2fe80039` — 2026-08-04T23:05:13Z

PR_AUC held across 3 seeds (orig 0.9764)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a723832d2fe80039` | `67a37b083eb06646` | `67a37b083eb06646` | `67a37b083eb06646` |
| PR AUC | 0.9764 | 0.9759 | 0.9699 | 0.9730 |
| ROC AUC | 0.9836 | 0.9834 | 0.9796 | 0.9822 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a723832d2fe80039
```
