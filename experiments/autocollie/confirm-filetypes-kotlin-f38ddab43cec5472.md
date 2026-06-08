# Confirm PASS — f38ddab43cec5472 on `filetypes/kotlin`

Cycle `20260608T130756-confirm-f38ddab43cec5472` — 2026-06-08T13:07:56Z

PR_AUC held across 3 seeds (orig 0.9802)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f38ddab43cec5472` | `391bff0ddb9f997b` | `391bff0ddb9f997b` | `391bff0ddb9f997b` |
| PR AUC | 0.9802 | 0.9794 | 0.9804 | 0.9805 |
| ROC AUC | 0.9859 | 0.9853 | 0.9862 | 0.9865 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f38ddab43cec5472
```
