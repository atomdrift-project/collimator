# Confirm PASS — 24c01185b8da8f63 on `filetypes/rust`

Cycle `20260609T162326-confirm-24c01185b8da8f63` — 2026-06-09T16:23:26Z

PR_AUC held across 3 seeds (orig 0.8673)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `24c01185b8da8f63` | `6e5cda18c947f00d` | `6e5cda18c947f00d` | `6e5cda18c947f00d` |
| PR AUC | 0.8673 | 0.8893 | 0.8941 | 0.8970 |
| ROC AUC | 0.9901 | 0.9915 | 0.9929 | 0.9921 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=24c01185b8da8f63
```
