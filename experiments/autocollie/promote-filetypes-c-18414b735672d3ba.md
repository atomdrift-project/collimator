# Promote REJECTED — `18414b735672d3ba` on `filetypes/c`

Generated 2026-06-02T00:46:33Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T00-41-08_20260602T004040-promote-18414b735672d3ba_azoth-validate.log; tail: 2026-06-01 20:46:28,206 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=9.37e-08 on 200 rows, 1079 ms)
2026-06-01 20:46:28,452 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-18414b735672d3ba/filetypes/c/models/seed_44.onnx
2026-06-01 20:46:28,502 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 20:46:29,251 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=9.68e-08 on 200 rows, 1045 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.ddrkiKIU8i
azoth bundle ok: /tmp/tmp.ddrkiKIU8i
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 76 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L4 hostile ensemble recall +1.85pp (5.28% → 7.13%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@1FP-on-slice +0.45pp (12.98% → 13.43%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + bz2: L4 hostile ensemble recall +66.67pp above LWM (0.00% → 66.67%)
  + crx: L4 hostile ensemble recall +76.92pp above LWM (0.00% → 76.92%)
  + doc: L4 hostile ensemble recall +7.33pp above LWM (90.99% → 98.32%)
  + docx: L4 hostile ensemble recall +9.85pp above LWM (71.59% → 81.44%)
  + go: L4 hostile ensemble recall +2.62pp above LWM (1.78% → 4.40%)
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
  + tar: L4 hostile ensemble recall +27.31pp above LWM (62.00% → 89.31%)
  + vbs: L4 hostile ensemble recall +39.13pp above LWM (25.70% → 64.84%)
  + xls: L4 hostile ensemble recall +0.98pp above LWM (92.44% → 93.42%)
  + xlsx: L4 hostile ensemble recall +15.90pp above LWM (29.01% → 44.91%)
  + xml: L4 hostile ensemble recall +1.98pp above LWM (2.74% → 4.72%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L4 hostile ENSEMBLE recall dropped 3.17pp BELOW LOW-WATER-MARK (10.31% → 7.13%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1169: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9913)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `18414b735672d3ba` | `23a48790b1fe7101` | `fd6ad9ae00756c82` |
| PR AUC | 0.9913 | 0.9904 | 0.9905 |
| ROC AUC | 0.9956 | 0.9955 | 0.9955 |
| F1 | 0.9511 | 0.9342 | 0.9340 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T00-41-08_20260602T004040-promote-18414b735672d3ba_azoth-validate.log; tail: 2026-06-01 20:46:28,206 INFO filetypes/c/models/seed_43.txt -> seed_43.onnx OK (delta=9.37e-08 on 200 rows, 1079 ms)
2026-06-01 20:46:28,452 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-c-18414b735672d3ba/filetypes/c/models/seed_44.onnx
2026-06-01 20:46:28,502 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-06-01 20:46:29,251 INFO filetypes/c/models/seed_44.txt -> seed_44.onnx OK (delta=9.68e-08 on 200 rows, 1045 ms)

converted 3/3 files (0 intentionally skipped, 0 failed)
staged runtime azoth bundle: /tmp/tmp.ddrkiKIU8i
azoth bundle ok: /tmp/tmp.ddrkiKIU8i
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 76 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L4 hostile ensemble recall +1.85pp (5.28% → 7.13%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@1FP-on-slice +0.45pp (12.98% → 13.43%)

23 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + bz2: L4 hostile ensemble recall +66.67pp above LWM (0.00% → 66.67%)
  + crx: L4 hostile ensemble recall +76.92pp above LWM (0.00% → 76.92%)
  + doc: L4 hostile ensemble recall +7.33pp above LWM (90.99% → 98.32%)
  + docx: L4 hostile ensemble recall +9.85pp above LWM (71.59% → 81.44%)
  + go: L4 hostile ensemble recall +2.62pp above LWM (1.78% → 4.40%)
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
  + tar: L4 hostile ensemble recall +27.31pp above LWM (62.00% → 89.31%)
  + vbs: L4 hostile ensemble recall +39.13pp above LWM (25.70% → 64.84%)
  + xls: L4 hostile ensemble recall +0.98pp above LWM (92.44% → 93.42%)
  + xlsx: L4 hostile ensemble recall +15.90pp above LWM (29.01% → 44.91%)
  + xml: L4 hostile ensemble recall +1.98pp above LWM (2.74% → 4.72%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - c: L4 hostile ENSEMBLE recall dropped 3.17pp BELOW LOW-WATER-MARK (10.31% → 7.13%; LWM tolerance 0.90pp)

compared 75 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (1 filetype(s) below LWM beyond the 0.90pp tolerance vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1169: azoth-validate] Error 1)
