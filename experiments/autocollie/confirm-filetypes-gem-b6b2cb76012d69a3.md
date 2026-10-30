# Confirm FAIL — b6b2cb76012d69a3 on `filetypes/gem`

Cycle `20261029T154252-confirm-b6b2cb76012d69a3` — 2026-10-29T15:42:52Z

confirmation measured L25 recall regressed: 0.88158 -> 0.86842

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b6b2cb76012d69a3` | `c0c2fe885aba1850` | `c0c2fe885aba1850` | `c0c2fe885aba1850` |
| PR AUC | 0.9094 | 0.9138 | 0.9167 | 0.9156 |
| ROC AUC | 0.9929 | 0.9933 | 0.9899 | 0.9917 |
| Recall@L50 | — | 0.8684 | 0.8684 | 0.8553 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
