# Confirm PASS — 95ec7191ecdb7dfe on `filetypes/powershell`

Cycle `20260602T012552-confirm-95ec7191ecdb7dfe` — 2026-06-02T01:25:52Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `95ec7191ecdb7dfe` | `9e2e35367b84277f` | `9e2e35367b84277f` | `9e2e35367b84277f` |
| PR AUC | 0.9992 | 0.9990 | 0.9995 | 0.9995 |
| ROC AUC | 0.9971 | 0.9948 | 0.9975 | 0.9972 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=95ec7191ecdb7dfe
```
