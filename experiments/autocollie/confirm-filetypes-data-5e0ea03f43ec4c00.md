# Confirm PASS — 5e0ea03f43ec4c00 on `filetypes/data`

Cycle `20260514T185746-confirm-5e0ea03f43ec4c00` — 2026-05-14T18:57:46Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5e0ea03f43ec4c00` | `d3e4f26d925f18c9` | `d3e4f26d925f18c9` | `d3e4f26d925f18c9` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5e0ea03f43ec4c00
```
