# Promote REJECTED — `311f7616d6c8dfe0` on `filetypes/batch`

Generated 2026-07-05T16:26:06Z

AUC regressed at full-train: 0.9139 -> 0.8747

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9890)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `311f7616d6c8dfe0` | `51df3f066420fab1` | `a0da3ff115b575b8` |
| PR AUC | 0.9890 | 0.9912 | 0.9907 |
| ROC AUC | 0.9139 | 0.8728 | 0.8747 |
| F1 | 0.2953 | 0.9947 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9139 -> 0.8747
