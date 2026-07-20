# Confirm PASS — fb2901dc0f44ac09 on `filetypes/python-bytecode`

Cycle `20260712T214815-confirm-fb2901dc0f44ac09` — 2026-07-12T21:48:15Z

PR_AUC held across 3 seeds (orig 0.9937)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fb2901dc0f44ac09` | `50ec82aef74356ae` | `50ec82aef74356ae` | `50ec82aef74356ae` |
| PR AUC | 0.9937 | 0.9937 | 0.9948 | 0.9941 |
| ROC AUC | 0.9973 | 0.9974 | 0.9983 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fb2901dc0f44ac09
```
