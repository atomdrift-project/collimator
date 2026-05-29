# Confirm PASS — 2b3513af25211b76 on `filetypes/elf`

Cycle `20260528T022224-confirm-2b3513af25211b76` — 2026-05-28T02:22:24Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2b3513af25211b76` | `2fded7d449ab0085` | `2fded7d449ab0085` | `2fded7d449ab0085` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9650 | 0.9703 | 0.9612 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2b3513af25211b76
```
