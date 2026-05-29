# Promote REJECTED — `d05c3167eac23e8c` on `filetypes/docx`

Generated 2026-05-26T21:21:52Z

AUC regressed at full-train: 1.0000 -> 0.9807

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d05c3167eac23e8c` | `d82f004a925af5fa` | `c9d4c5ae82467add` |
| PR AUC | 1.0000 | 0.9962 | 0.9964 |
| ROC AUC | 1.0000 | 0.9801 | 0.9807 |
| F1 | 0.9771 | 0.9956 | 0.9956 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9807
