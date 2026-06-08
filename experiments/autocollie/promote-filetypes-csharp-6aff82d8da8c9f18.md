# Promote REJECTED — `6aff82d8da8c9f18` on `filetypes/csharp`

Generated 2026-06-08T16:07:02Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-03-26_20260608T160324-promote-6aff82d8da8c9f18_azoth-validate.log; tail: converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.ss6XkaScP0
azoth bundle ok: /tmp/tmp.ss6XkaScP0
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@1FP-on-slice +1.58pp (21.20% → 22.78%)

30 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + vbs: L50 hostile ensemble recall +14.60pp above LWM (42.09% → 56.69%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 8.53pp BELOW LOW-WATER-MARK (25.62% → 17.09%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1312: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.4832)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6aff82d8da8c9f18` | `950eb2255ef83354` | `12ea876d4a0965b8` |
| PR AUC | 0.4832 | 0.5314 | 0.5426 |
| ROC AUC | 0.9139 | 0.9297 | 0.9258 |
| F1 | 0.3971 | 0.4336 | 0.4346 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-08T16-03-26_20260608T160324-promote-6aff82d8da8c9f18_azoth-validate.log; tail: converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.ss6XkaScP0
azoth bundle ok: /tmp/tmp.ss6XkaScP0
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 77 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  csharp :: filetypes/csharp recall@1FP-on-slice +1.58pp (21.20% → 22.78%)

30 low-water-mark improvement(s) (>0.90pp above LWM, informational):
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
  + vbs: L50 hostile ensemble recall +14.60pp above LWM (42.09% → 56.69%)
  + xls: L50 hostile ensemble recall +3.44pp above LWM (90.97% → 94.40%)
  + xlsx: L50 hostile ensemble recall +1.37pp above LWM (29.09% → 30.46%)
  + zip: L50 hostile ensemble recall +2.12pp above LWM (31.98% → 34.10%)
  + zst: L50 hostile ensemble recall +28.22pp above LWM (8.42% → 36.63%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - csharp: L50 hostile ENSEMBLE recall dropped 8.53pp BELOW LOW-WATER-MARK (25.62% → 17.09%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run, or pass --net-improvement-fallback to ship a net-positive deploy whose only regressions are on small routes (below --catastrophe-min-mal). A high-volume filetype cratering past --max-net-route-regression blocks regardless; AZOTH_ALLOW_REGRESSION is the only override for that.
make[1]: *** [Makefile:1312: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
