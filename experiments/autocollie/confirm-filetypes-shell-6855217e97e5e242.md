# Confirm FAIL — 6855217e97e5e242 on `filetypes/shell`

Cycle `20261106T112339-confirm-6855217e97e5e242` — 2026-11-06T11:23:39Z

confirmation measured L25 recall regressed: 0.86386 -> 0.85266

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6855217e97e5e242` | `f579661c29a8ffc6` | `f579661c29a8ffc6` | `f579661c29a8ffc6` |
| PR AUC | 0.9935 | 0.9952 | 0.9949 | 0.9952 |
| ROC AUC | 0.9977 | 0.9980 | 0.9980 | 0.9982 |
| Recall@L50 | — | 0.6847 | 0.7286 | 0.6798 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
