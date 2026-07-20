# Confirm PASS — bb0ec5f339803388 on `filetypes/elf`

Cycle `20260713T091902-confirm-bb0ec5f339803388` — 2026-07-13T09:19:02Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb0ec5f339803388` | `1f1cada91ba58e34` | `1f1cada91ba58e34` | `1f1cada91ba58e34` |
| PR AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bb0ec5f339803388
```
