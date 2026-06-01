# Promote REJECTED — `e788920478a0ad69` on `filetypes/macho`

Generated 2026-06-01T21:16:52Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T21-13-03_20260601T211238-promote-e788920478a0ad69_azoth-validate.log; tail: 2026-06-01 17:16:46,203 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-e788920478a0ad69/filetypes/macho/models/seed_44.onnx
2026-06-01 17:16:46,302 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 17:16:47,137 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=7.63e-08 on 200 rows, 1101 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.zUcEmIfLVw
azoth bundle ok: /tmp/tmp.zUcEmIfLVw
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  macho :: filetypes/macho recall@1FP-on-slice +0.92pp (82.26% → 83.18%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + bz2: L4 hostile ensemble recall +66.67pp above LWM (0.00% → 66.67%)
  + crx: L4 hostile ensemble recall +76.92pp above LWM (0.00% → 76.92%)
  + doc: L4 hostile ensemble recall +7.33pp above LWM (90.99% → 98.32%)
  + docx: L4 hostile ensemble recall +9.85pp above LWM (71.59% → 81.44%)
  + go: L4 hostile ensemble recall +3.04pp above LWM (1.78% → 4.82%)
  + html: L4 hostile ensemble recall +51.33pp above LWM (16.67% → 68.00%)
  + jpeg: L4 hostile ensemble recall +7.83pp above LWM (1.56% → 9.40%)
  + lnk: L4 hostile ensemble recall +8.14pp above LWM (48.66% → 56.80%)
  + lua: L4 hostile ensemble recall +53.85pp above LWM (0.00% → 53.85%)
  + objc: L4 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L4 hostile ensemble recall +3.51pp above LWM (86.78% → 90.28%)
  + pdf: L4 hostile ensemble recall +65.23pp above LWM (6.41% → 71.64%)
  + plist: L4 hostile ensemble recall +3.12pp above LWM (2.94% → 6.06%)
  + powershell: L4 hostile ensemble recall +19.35pp above LWM (29.62% → 48.97%)
  + pptx: L4 hostile ensemble recall +33.99pp above LWM (9.09% → 43.08%)
  + python-bytecode: L4 hostile ensemble recall +1.14pp above LWM (90.99% → 92.13%)
  + rtf: L4 hostile ensemble recall +1.02pp above LWM (97.67% → 98.70%)
  + shell: L4 hostile ensemble recall +4.09pp above LWM (82.78% → 86.88%)
  + tar: L4 hostile ensemble recall +33.05pp above LWM (62.00% → 95.05%)
  + tar.gz: L4 hostile ensemble recall +19.17pp above LWM (56.69% → 75.86%)
  + vbs: L4 hostile ensemble recall +39.13pp above LWM (25.70% → 64.84%)
  + xls: L4 hostile ensemble recall +0.98pp above LWM (92.44% → 93.42%)
  + xlsx: L4 hostile ensemble recall +15.90pp above LWM (29.01% → 44.91%)
  + xml: L4 hostile ensemble recall +1.98pp above LWM (2.74% → 4.72%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - macho: L4 hostile ENSEMBLE recall dropped 5.81pp (77.37% → 71.56%; tolerance 1.70pp; deployed 95% CI lower = 72.44%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L4 hostile ENSEMBLE recall dropped 15.08pp BELOW LOW-WATER-MARK (86.64% → 71.56%; LWM tolerance 0.90pp)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9992)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e788920478a0ad69` | `5f798cfa0d934d96` | `895a132833cc50d4` |
| PR AUC | 0.9992 | 0.9968 | 0.9967 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 |
| F1 | 0.9833 | 0.9744 | 0.9744 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T21-13-03_20260601T211238-promote-e788920478a0ad69_azoth-validate.log; tail: 2026-06-01 17:16:46,203 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-e788920478a0ad69/filetypes/macho/models/seed_44.onnx
2026-06-01 17:16:46,302 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 17:16:47,137 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=7.63e-08 on 200 rows, 1101 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.zUcEmIfLVw
azoth bundle ok: /tmp/tmp.zUcEmIfLVw
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route improvements (≥0.10pp, informational):
  macho :: filetypes/macho recall@1FP-on-slice +0.92pp (82.26% → 83.18%)

24 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + bz2: L4 hostile ensemble recall +66.67pp above LWM (0.00% → 66.67%)
  + crx: L4 hostile ensemble recall +76.92pp above LWM (0.00% → 76.92%)
  + doc: L4 hostile ensemble recall +7.33pp above LWM (90.99% → 98.32%)
  + docx: L4 hostile ensemble recall +9.85pp above LWM (71.59% → 81.44%)
  + go: L4 hostile ensemble recall +3.04pp above LWM (1.78% → 4.82%)
  + html: L4 hostile ensemble recall +51.33pp above LWM (16.67% → 68.00%)
  + jpeg: L4 hostile ensemble recall +7.83pp above LWM (1.56% → 9.40%)
  + lnk: L4 hostile ensemble recall +8.14pp above LWM (48.66% → 56.80%)
  + lua: L4 hostile ensemble recall +53.85pp above LWM (0.00% → 53.85%)
  + objc: L4 hostile ensemble recall +20.00pp above LWM (0.00% → 20.00%)
  + package.json: L4 hostile ensemble recall +3.51pp above LWM (86.78% → 90.28%)
  + pdf: L4 hostile ensemble recall +65.23pp above LWM (6.41% → 71.64%)
  + plist: L4 hostile ensemble recall +3.12pp above LWM (2.94% → 6.06%)
  + powershell: L4 hostile ensemble recall +19.35pp above LWM (29.62% → 48.97%)
  + pptx: L4 hostile ensemble recall +33.99pp above LWM (9.09% → 43.08%)
  + python-bytecode: L4 hostile ensemble recall +1.14pp above LWM (90.99% → 92.13%)
  + rtf: L4 hostile ensemble recall +1.02pp above LWM (97.67% → 98.70%)
  + shell: L4 hostile ensemble recall +4.09pp above LWM (82.78% → 86.88%)
  + tar: L4 hostile ensemble recall +33.05pp above LWM (62.00% → 95.05%)
  + tar.gz: L4 hostile ensemble recall +19.17pp above LWM (56.69% → 75.86%)
  + vbs: L4 hostile ensemble recall +39.13pp above LWM (25.70% → 64.84%)
  + xls: L4 hostile ensemble recall +0.98pp above LWM (92.44% → 93.42%)
  + xlsx: L4 hostile ensemble recall +15.90pp above LWM (29.01% → 44.91%)
  + xml: L4 hostile ensemble recall +1.98pp above LWM (2.74% → 4.72%)

1 DEPLOYED-TOLERANCE regression(s) (vs currently-deployed bundle /home/t/.local/share/litmus/models/azoth) — THIS IS WHAT BLOCKS THE DEPLOY:
  - macho: L4 hostile ENSEMBLE recall dropped 5.81pp (77.37% → 71.56%; tolerance 1.70pp; deployed 95% CI lower = 72.44%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L4 hostile ENSEMBLE recall dropped 15.08pp BELOW LOW-WATER-MARK (86.64% → 71.56%; LWM tolerance 0.90pp)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)
