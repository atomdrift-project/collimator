# Confirm PASS — 630aeb17283e935a on `filetypes/java`

Cycle `20260606T180851-confirm-630aeb17283e935a` — 2026-06-06T18:08:51Z

PR_AUC held across 3 seeds (orig 0.5067)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `630aeb17283e935a` | `a892dbb7345f82de` | `a892dbb7345f82de` | `a892dbb7345f82de` |
| PR AUC | 0.5067 | 0.9173 | 0.8752 | 0.8959 |
| ROC AUC | 0.7396 | 0.9545 | 0.9159 | 0.9455 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=630aeb17283e935a
```
