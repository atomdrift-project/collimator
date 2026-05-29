# Confirm PASS — d05c3167eac23e8c on `filetypes/docx`

Cycle `20260526T212147-confirm-d05c3167eac23e8c` — 2026-05-26T21:21:47Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d05c3167eac23e8c` | `d82f004a925af5fa` | `d82f004a925af5fa` | `d82f004a925af5fa` |
| PR AUC | 1.0000 | 0.9966 | 0.9963 | 0.9963 |
| ROC AUC | 1.0000 | 0.9817 | 0.9798 | 0.9808 |
| Recall@3FPM | — | 0.4602 | 0.4469 | 0.4292 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d05c3167eac23e8c
```
