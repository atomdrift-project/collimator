# Confirm FAIL — caee54152b079267 on `filetypes/java`

Cycle `20260527T060733-confirm-caee54152b079267` — 2026-05-27T06:07:33Z

averaged ensemble PR_AUC regressed: 0.4389 -> 0.3860 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `caee54152b079267` | `e1a0b6bf9ae38e96` | `e1a0b6bf9ae38e96` | `e1a0b6bf9ae38e96` |
| PR AUC | 0.4389 | 0.3889 | 0.3860 | 0.3860 |
| ROC AUC | 0.8021 | 0.8125 | 0.8021 | 0.8021 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
