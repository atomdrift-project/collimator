# Promote REJECTED — `71855dc03e7d07cc` on `filetypes/shell`

Generated 2026-05-27T01:05:00Z

AUC regressed at full-train: 0.9996 -> 0.9981

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `71855dc03e7d07cc` | `d11ea99b934ebb12` | `ab56e0c6b2f5cd83` |
| PR AUC | 0.9986 | 0.9972 | 0.9972 |
| ROC AUC | 0.9996 | 0.9981 | 0.9981 |
| F1 | 0.0000 | 0.9256 | 0.9318 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9996 -> 0.9981
