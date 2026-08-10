# Confirm PASS — b2636372e3f99c70 on `filetypes/registry`

Cycle `20260805T145740-confirm-b2636372e3f99c70` — 2026-08-05T14:57:40Z

PR_AUC held across 3 seeds (orig 0.8443)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b2636372e3f99c70` | `55996db527e38238` | `55996db527e38238` | `55996db527e38238` |
| PR AUC | 0.8443 | 0.8800 | 0.8869 | 0.8806 |
| ROC AUC | 0.9986 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b2636372e3f99c70
```
