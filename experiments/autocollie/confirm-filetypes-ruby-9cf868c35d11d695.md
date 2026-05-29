# Confirm FAIL — 9cf868c35d11d695 on `filetypes/ruby`

Cycle `20260527T012811-confirm-9cf868c35d11d695` — 2026-05-27T01:28:11Z

averaged ensemble PR_AUC regressed: 0.9821 -> 0.8830 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9cf868c35d11d695` | `abcbde9077cb36d8` | `abcbde9077cb36d8` | `abcbde9077cb36d8` |
| PR AUC | 0.9821 | 0.9237 | 0.8616 | 0.8408 |
| ROC AUC | 0.9993 | 0.9968 | 0.9958 | 0.9940 |
| Recall@3FPM | — | 0.5556 | 0.2222 | 0.2222 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
