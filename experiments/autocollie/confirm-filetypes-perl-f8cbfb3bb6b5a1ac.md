# Confirm FAIL — f8cbfb3bb6b5a1ac on `filetypes/perl`

Cycle `20260526T194018-confirm-f8cbfb3bb6b5a1ac` — 2026-05-26T19:40:18Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9908 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f8cbfb3bb6b5a1ac` | `48c273b59b33b288` | `48c273b59b33b288` | `48c273b59b33b288` |
| PR AUC | 1.0000 | 0.9924 | 0.9908 | 0.9881 |
| ROC AUC | 1.0000 | 0.9992 | 0.9989 | 0.9985 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
