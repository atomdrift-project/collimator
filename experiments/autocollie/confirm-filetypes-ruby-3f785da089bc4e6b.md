# Confirm FAIL — 3f785da089bc4e6b on `filetypes/ruby`

Cycle `20260527T012806-confirm-3f785da089bc4e6b` — 2026-05-27T01:28:06Z

averaged ensemble PR_AUC regressed: 0.9821 -> 0.9396 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f785da089bc4e6b` | `2fd6849a890e6a15` | `2fd6849a890e6a15` | `2fd6849a890e6a15` |
| PR AUC | 0.9821 | 0.9192 | 0.9460 | 0.9093 |
| ROC AUC | 0.9993 | 0.9972 | 0.9977 | 0.9954 |
| Recall@3FPM | — | 0.4444 | 0.6667 | 0.5556 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
