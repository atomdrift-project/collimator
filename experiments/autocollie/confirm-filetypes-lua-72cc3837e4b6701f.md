# Confirm PASS — 72cc3837e4b6701f on `filetypes/lua`

Cycle `20260527T052501-confirm-72cc3837e4b6701f` — 2026-05-27T05:25:01Z

PR_AUC held across 3 seeds (orig 0.5741)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72cc3837e4b6701f` | `1f02ca3220e6802b` | `1f02ca3220e6802b` | `1f02ca3220e6802b` |
| PR AUC | 0.5741 | 0.7183 | 0.6442 | 0.5995 |
| ROC AUC | 0.7065 | 0.9076 | 0.8315 | 0.7772 |
| Recall@3FPM | — | 0.5000 | 0.5000 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72cc3837e4b6701f
```
