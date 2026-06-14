# Confirm PASS — 6fb02662c97f7452 on `filetypes/powershell`

Cycle `20260614T212602-confirm-6fb02662c97f7452` — 2026-06-14T21:26:02Z

PR_AUC held across 3 seeds (orig 0.9933)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6fb02662c97f7452` | `d8088b365f9dff13` | `d8088b365f9dff13` | `d8088b365f9dff13` |
| PR AUC | 0.9933 | 0.9937 | 0.9932 | 0.9927 |
| ROC AUC | 0.9836 | 0.9846 | 0.9834 | 0.9818 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6fb02662c97f7452
```
