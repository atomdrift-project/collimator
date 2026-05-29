# Confirm PASS — 86cea72521c473ae on `filetypes/html`

Cycle `20260527T071116-confirm-86cea72521c473ae` — 2026-05-27T07:11:16Z

PR_AUC held across 3 seeds (orig 0.6154)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `86cea72521c473ae` | `e13623a354d68171` | `e13623a354d68171` | `e13623a354d68171` |
| PR AUC | 0.6154 | 0.6154 | 0.6154 | 0.6154 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=86cea72521c473ae
```
