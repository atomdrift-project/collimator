# Confirm PASS — cc8f4eda27819b65 on `filetypes/php`

Cycle `20260522T172820-confirm-cc8f4eda27819b65` — 2026-05-22T17:28:20Z

PR_AUC held across 3 seeds (orig 0.9945)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc8f4eda27819b65` | `6878437e86f19818` | `6878437e86f19818` | `6878437e86f19818` |
| PR AUC | 0.9945 | 0.9939 | 0.9933 | 0.9937 |
| ROC AUC | 0.9973 | 0.9970 | 0.9971 | 0.9967 |
| Recall@3FPM | — | 0.2449 | 0.1693 | 0.2700 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cc8f4eda27819b65
```
