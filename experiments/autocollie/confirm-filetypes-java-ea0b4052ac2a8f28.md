# Confirm PASS — ea0b4052ac2a8f28 on `filetypes/java`

Cycle `20260606T180840-confirm-ea0b4052ac2a8f28` — 2026-06-06T18:08:40Z

PR_AUC held across 3 seeds (orig 0.4766)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ea0b4052ac2a8f28` | `1449c81f11c6f67a` | `1449c81f11c6f67a` | `1449c81f11c6f67a` |
| PR AUC | 0.4766 | 0.7730 | 0.8226 | 0.7654 |
| ROC AUC | 0.8466 | 0.9183 | 0.9260 | 0.9255 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ea0b4052ac2a8f28
```
