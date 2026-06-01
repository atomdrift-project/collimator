# Promote REJECTED — `1ea4d0f57a20fde1` on `filetypes/macho`

Generated 2026-06-01T21:21:34Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T21-17-42_20260601T211715-promote-1ea4d0f57a20fde1_azoth-validate.log; tail: 2026-06-01 17:21:27,916 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-1ea4d0f57a20fde1/filetypes/macho/models/seed_44.onnx
2026-06-01 17:21:28,016 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 17:21:28,841 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=8.59e-08 on 200 rows, 1087 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.oQtZjcQaWS
azoth bundle ok: /tmp/tmp.oQtZjcQaWS
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  macho :: filetypes/macho recall@1FP-on-slice dropped 2.14pp (82.26% → 80.12%)

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
  - macho: L4 hostile ENSEMBLE recall dropped 9.79pp (77.37% → 67.58%; tolerance 1.70pp; deployed 95% CI lower = 72.44%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L4 hostile ENSEMBLE recall dropped 19.06pp BELOW LOW-WATER-MARK (86.64% → 67.58%; LWM tolerance 0.90pp)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9996)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `1ea4d0f57a20fde1` | `403527c9d5da874a` | `1c2ddcb4b755d7bf` |
| PR AUC | 0.9996 | 0.9964 | 0.9965 |
| ROC AUC | 0.9999 | 0.9991 | 0.9991 |
| F1 | 0.9868 | 0.9729 | 0.9742 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-01T21-17-42_20260601T211715-promote-1ea4d0f57a20fde1_azoth-validate.log; tail: 2026-06-01 17:21:27,916 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-macho-1ea4d0f57a20fde1/filetypes/macho/models/seed_44.onnx
2026-06-01 17:21:28,016 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 17:21:28,841 INFO filetypes/macho/models/seed_44.txt -> seed_44.onnx OK (delta=8.59e-08 on 200 rows, 1087 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.oQtZjcQaWS
azoth bundle ok: /tmp/tmp.oQtZjcQaWS
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 78 unimpacted (drift treated as pre-existing)

per-route regressions (informational; does not block deploy):
  macho :: filetypes/macho recall@1FP-on-slice dropped 2.14pp (82.26% → 80.12%)

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
  - macho: L4 hostile ENSEMBLE recall dropped 9.79pp (77.37% → 67.58%; tolerance 1.70pp; deployed 95% CI lower = 72.44%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - macho: L4 hostile ENSEMBLE recall dropped 19.06pp BELOW LOW-WATER-MARK (86.64% → 67.58%; LWM tolerance 0.90pp)

compared 77 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1 filetype(s) regressed vs deployed beyond the 1.70pp tolerance; see list above for the actual drops), low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1152: azoth-validate] Error 1)
