# Confirm PASS — 70579bd4e24be195 on `filetypes/groovy`

Cycle `20260527T080415-confirm-70579bd4e24be195` — 2026-05-27T08:04:15Z

PR_AUC held across 3 seeds (orig 0.6667)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `70579bd4e24be195` | `d1fe4a6e7b08cbdc` | `d1fe4a6e7b08cbdc` | `d1fe4a6e7b08cbdc` |
| PR AUC | 0.6667 | 0.6667 | 0.6667 | 0.6667 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=70579bd4e24be195
```
