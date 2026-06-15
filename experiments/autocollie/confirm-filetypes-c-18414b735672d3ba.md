# Confirm FAIL — 18414b735672d3ba on `filetypes/c`

Cycle `20260614T233237-confirm-18414b735672d3ba` — 2026-06-14T23:32:37Z

averaged ensemble PR_AUC regressed: 0.9913 -> 0.9837 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `18414b735672d3ba` | `b7d06b91956152f1` | `b7d06b91956152f1` | `b7d06b91956152f1` |
| PR AUC | 0.9913 | 0.9830 | 0.9829 | 0.9832 |
| ROC AUC | 0.9956 | 0.9922 | 0.9927 | 0.9926 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
