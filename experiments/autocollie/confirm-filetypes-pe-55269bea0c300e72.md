# Confirm PASS — 55269bea0c300e72 on `filetypes/pe`

Cycle `20260825T231645-confirm-55269bea0c300e72` — 2026-08-25T23:16:45Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `55269bea0c300e72` | `b874ce78af95e59f` | `b874ce78af95e59f` | `b874ce78af95e59f` |
| PR AUC | 0.9991 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9997 | 0.9997 | 0.9997 |
| Recall@L50 | — | 0.6691 | 0.6492 | 0.5900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=55269bea0c300e72
```
