# Confirm PASS — 8304c75900f902c0 on `filetypes/pe`

Cycle `20260607T010819-confirm-8304c75900f902c0` — 2026-06-07T01:08:19Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8304c75900f902c0` | `1f71bf544d788800` | `1f71bf544d788800` | `1f71bf544d788800` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8304c75900f902c0
```
