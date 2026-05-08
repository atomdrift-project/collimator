# Confirm FAIL — 6ef5dcf119d8e87c on `filegroups/portable`

Cycle `20260508T203529-confirm-6ef5dcf119d8e87c` — 2026-05-08T20:35:29Z

averaged ensemble F1 regressed: 0.9852 -> 0.9728 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6ef5dcf119d8e87c` | `acae07e2f8b688d9` | `acae07e2f8b688d9` | `acae07e2f8b688d9` |
| F1 | 0.9852 | 0.9666 | 0.9911 | 0.9728 |
| ROC AUC | 0.9954 | 0.9964 | 0.9946 | 0.9947 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.3593 | 0.4551 | 0.4551 | 0.4551 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
