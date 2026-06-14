# Confirm FAIL — 18414b735672d3ba on `filetypes/c`

Cycle `20260614T031500-confirm-18414b735672d3ba` — 2026-06-14T03:15:00Z

averaged ensemble PR_AUC regressed: 0.9913 -> 0.9840 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `18414b735672d3ba` | `b4d2a46ae2adcfcb` | `b4d2a46ae2adcfcb` | `b4d2a46ae2adcfcb` |
| PR AUC | 0.9913 | 0.9824 | 0.9845 | 0.9835 |
| ROC AUC | 0.9956 | 0.9919 | 0.9932 | 0.9930 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
