# Confirm PASS — bbc948dbbff26f17 on `filetypes/xml`

Cycle `20260521T031733-confirm-bbc948dbbff26f17` — 2026-05-21T03:17:33Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bbc948dbbff26f17` | `cd1c48c2bf689607` | `cd1c48c2bf689607` | `cd1c48c2bf689607` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bbc948dbbff26f17
```
