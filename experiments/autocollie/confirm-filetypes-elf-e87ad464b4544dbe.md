# Confirm PASS — e87ad464b4544dbe on `filetypes/elf`

Cycle `20260526T172904-confirm-e87ad464b4544dbe` — 2026-05-26T17:29:04Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e87ad464b4544dbe` | `90b2a44731bb4cab` | `90b2a44731bb4cab` | `90b2a44731bb4cab` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9780 | 0.9819 | 0.9758 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e87ad464b4544dbe
```
