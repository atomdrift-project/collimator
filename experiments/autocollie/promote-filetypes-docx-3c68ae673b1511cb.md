# Promote REJECTED — `3c68ae673b1511cb` on `filetypes/docx`

Generated 2026-05-26T21:22:01Z

AUC regressed at full-train: 1.0000 -> 0.9951

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3c68ae673b1511cb` | `e7d40b2f18aa1072` | `80cf7b0a77e930bb` |
| PR AUC | 1.0000 | 0.9995 | 0.9993 |
| ROC AUC | 1.0000 | 0.9964 | 0.9951 |
| F1 | 0.9280 | 0.9912 | 0.9912 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 1.0000 -> 0.9951
