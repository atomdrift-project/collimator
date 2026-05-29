# Confirm PASS — 7873dc9044396d28 on `filetypes/plist`

Cycle `20260527T015943-confirm-7873dc9044396d28` — 2026-05-27T01:59:43Z

PR_AUC held across 3 seeds (orig 0.9250)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7873dc9044396d28` | `378e3fb93c174bb9` | `378e3fb93c174bb9` | `378e3fb93c174bb9` |
| PR AUC | 0.9250 | 0.9250 | 0.9429 | 0.9429 |
| ROC AUC | 0.9700 | 0.9700 | 0.9800 | 0.9800 |
| Recall@3FPM | — | 0.8000 | 0.8000 | 0.8000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7873dc9044396d28
```
