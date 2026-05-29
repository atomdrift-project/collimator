# Confirm PASS — ece1580f81061a97 on `filetypes/csharp`

Cycle `20260527T003735-confirm-ece1580f81061a97` — 2026-05-27T00:37:35Z

PR_AUC held across 3 seeds (orig 0.9881)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ece1580f81061a97` | `dbff489ac44970b8` | `dbff489ac44970b8` | `dbff489ac44970b8` |
| PR AUC | 0.9881 | 0.9855 | 0.9860 | 0.9876 |
| ROC AUC | 0.9936 | 0.9919 | 0.9922 | 0.9931 |
| Recall@3FPM | — | 0.8169 | 0.8732 | 0.9014 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ece1580f81061a97
```
