# Confirm PASS — b738d7937eacec6b on `filetypes/pptx`

Cycle `20260527T080857-confirm-b738d7937eacec6b` — 2026-05-27T08:08:57Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b738d7937eacec6b` | `1ef7ee38a7218fa0` | `1ef7ee38a7218fa0` | `1ef7ee38a7218fa0` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b738d7937eacec6b
```
