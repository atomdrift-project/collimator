# Promote REJECTED — `1f286aed59b5942e` on `filetypes/vbs`

Generated 2026-06-08T16:10:23Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-07-05_20260608T160704-promote-1f286aed59b5942e_azoth-validate.log; tail: azoth bundle ok: /tmp/tmp.d9qOcNKWs5
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

29 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +16.64pp above LWM (13.53% → 30.17%)
  + c: L50 hostile ensemble recall +1.45pp above LWM (8.53% → 9.98%)
  + cab: L50 hostile ensemble recall +1.04pp above LWM (0.00% → 1.04%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + chrome-manifest: L50 hostile ensemble recall +19.64pp above LWM (42.86% → 62.50%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +2.21pp above LWM (91.77% → 93.97%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + java_class: L50 hostile ensemble recall +39.53pp above LWM (23.08% → 62.61%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +5.55pp above LWM (46.48% → 52.03%)
  + lnk: L50 hostile ensemble recall +3.94pp above LWM (66.73% → 70.66%)
  + lua: L50 hostile ensemble recall +15.38pp above LWM (53.85% → 69.23%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +30.62pp above LWM (38.34% → 68.95%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +18.88pp above LWM (37.61% → 56.49%)
  + pkg-info: L50 hostile ensemble recall +29.29pp above LWM (65.47% → 94.75%)
  + plist: L50 hostile ensemble recall +3.82pp above LWM (1.52% → 5.33%)
  + png: L50 hostile ensemble recall +5.40pp above LWM (0.12% → 5.52%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + tar: L50 hostile ensemble recall +4.77pp above LWM (81.54% → 86.30%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 15.46pp (56.69% → 41.23%; tolerance 1.70pp; deployed 95% CI lower = 54.08%)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -222 TPs across 75 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 15.46pp on 'vbs' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9976)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1f286aed59b5942e` | `6f86087bbbadb07e` | `38506957043a7dbe` |
| PR AUC | 0.9976 | 0.9975 | 0.9976 |
| ROC AUC | 0.9920 | 0.9916 | 0.9919 |
| F1 | 0.9598 | 0.9758 | 0.9782 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-07-05_20260608T160704-promote-1f286aed59b5942e_azoth-validate.log; tail: azoth bundle ok: /tmp/tmp.d9qOcNKWs5
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  vbs :: filetypes/vbs recall@1FP-on-slice dropped 34.54pp (69.71% → 35.17%)

29 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + 7z: L50 hostile ensemble recall +16.64pp above LWM (13.53% → 30.17%)
  + c: L50 hostile ensemble recall +1.45pp above LWM (8.53% → 9.98%)
  + cab: L50 hostile ensemble recall +1.04pp above LWM (0.00% → 1.04%)
  + cargo.toml: L50 hostile ensemble recall +22.22pp above LWM (0.00% → 22.22%)
  + chrome-manifest: L50 hostile ensemble recall +19.64pp above LWM (42.86% → 62.50%)
  + crx: L50 hostile ensemble recall +30.51pp above LWM (37.98% → 68.49%)
  + docx: L50 hostile ensemble recall +34.91pp above LWM (44.66% → 79.57%)
  + elf: L50 hostile ensemble recall +2.21pp above LWM (91.77% → 93.97%)
  + jar: L50 hostile ensemble recall +7.42pp above LWM (48.09% → 55.51%)
  + java_class: L50 hostile ensemble recall +39.53pp above LWM (23.08% → 62.61%)
  + javascript: L50 hostile ensemble recall +24.16pp above LWM (39.17% → 63.33%)
  + kotlin: L50 hostile ensemble recall +5.55pp above LWM (46.48% → 52.03%)
  + lnk: L50 hostile ensemble recall +3.94pp above LWM (66.73% → 70.66%)
  + lua: L50 hostile ensemble recall +15.38pp above LWM (53.85% → 69.23%)
  + macho: L50 hostile ensemble recall +9.65pp above LWM (68.26% → 77.91%)
  + msi: L50 hostile ensemble recall +30.62pp above LWM (38.34% → 68.95%)
  + ole: L50 hostile ensemble recall +30.02pp above LWM (50.88% → 80.90%)
  + package.json: L50 hostile ensemble recall +7.50pp above LWM (78.39% → 85.89%)
  + pe: L50 hostile ensemble recall +18.88pp above LWM (37.61% → 56.49%)
  + pkg-info: L50 hostile ensemble recall +29.29pp above LWM (65.47% → 94.75%)
  + plist: L50 hostile ensemble recall +3.82pp above LWM (1.52% → 5.33%)
  + png: L50 hostile ensemble recall +5.40pp above LWM (0.12% → 5.52%)
  + powershell: L50 hostile ensemble recall +9.37pp above LWM (43.71% → 53.08%)
  + shell: L50 hostile ensemble recall +28.14pp above LWM (43.91% → 72.05%)
  + tar: L50 hostile ensemble recall +4.77pp above LWM (81.54% → 86.30%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - vbs: L50 hostile ENSEMBLE recall dropped 15.46pp (56.69% → 41.23%; tolerance 1.70pp; deployed 95% CI lower = 54.08%)

net-improvement-fallback DID NOT rescue: net malware-caught delta = -222 TPs across 75 compared filetypes; worst high-volume drop (>=1500 mal) = 0.00pp on 'none' (cap = 5.00pp); worst drop overall = 15.46pp on 'vbs' (small-route, not gated)
  reason: aggregate TP delta is not positive

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1317: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
