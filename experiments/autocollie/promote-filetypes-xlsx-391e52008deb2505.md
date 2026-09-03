# Promote REJECTED — `391e52008deb2505` on `filetypes/xlsx`

Generated 2026-08-24T23:47:03Z

PR_AUC regressed at full-train: 0.9926 -> 0.9873

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9926)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `391e52008deb2505` | `80c0853569b84578` | `01b9a61774b5eaa5` |
| PR AUC | 0.9926 | 0.9918 | 0.9873 |
| ROC AUC | 0.8659 | 0.8523 | 0.7752 |
| F1 | 0.5087 | 0.4843 | 0.4820 |

## Disposition

This spec did not survive the promotion ladder.

PR_AUC regressed at full-train: 0.9926 -> 0.9873
