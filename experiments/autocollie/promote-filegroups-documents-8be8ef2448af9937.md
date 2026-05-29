# Promote REJECTED — `8be8ef2448af9937` on `filegroups/documents`

Generated 2026-05-26T22:08:35Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T22-05-19_20260526T220503-promote-8be8ef2448af9937_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937
staged runtime azoth bundle: /tmp/tmp.0iNvRCHEb9
azoth bundle ok: /tmp/tmp.0iNvRCHEb9
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  docx: L3 hostile ensemble recall +9.09pp (71.59% → 80.68%)
  html: L3 hostile ensemble recall +83.33pp (16.67% → 100.00%)
  xlsx: L3 hostile ensemble recall +4.60pp (29.01% → 33.62%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  ole :: filegroups/documents recall@3FP/M +5.17pp (91.70% → 96.88%)
  pdf :: filegroups/documents recall@3FP/M +64.90pp (8.41% → 73.31%)
  rtf :: filegroups/documents recall@3FP/M +1.40pp (96.74% → 98.14%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + docx: L3 hostile ensemble recall +9.09pp above LWM (71.59% → 80.68%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.16pp above LWM (6.41% → 7.57%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.85pp above LWM (92.44% → 95.30%)
  + xlsx: L3 hostile ensemble recall +4.60pp above LWM (29.01% → 33.62%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.34pp BELOW LOW-WATER-MARK (90.99% → 72.65%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 1.0000)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `8be8ef2448af9937` | `a817ae4b9e792f16` | `5fc9a9a903f563f8` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9998 |
| F1 | 0.9934 | 0.9983 | 0.9985 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T22-05-19_20260526T220503-promote-8be8ef2448af9937_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-documents-8be8ef2448af9937
staged runtime azoth bundle: /tmp/tmp.0iNvRCHEb9
azoth bundle ok: /tmp/tmp.0iNvRCHEb9
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  docx: L3 hostile ensemble recall +9.09pp (71.59% → 80.68%)
  html: L3 hostile ensemble recall +83.33pp (16.67% → 100.00%)
  xlsx: L3 hostile ensemble recall +4.60pp (29.01% → 33.62%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  ole :: filegroups/documents recall@3FP/M +5.17pp (91.70% → 96.88%)
  pdf :: filegroups/documents recall@3FP/M +64.90pp (8.41% → 73.31%)
  rtf :: filegroups/documents recall@3FP/M +1.40pp (96.74% → 98.14%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

17 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + docx: L3 hostile ensemble recall +9.09pp above LWM (71.59% → 80.68%)
  + html: L3 hostile ensemble recall +83.33pp above LWM (16.67% → 100.00%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.16pp above LWM (6.41% → 7.57%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.85pp above LWM (92.44% → 95.30%)
  + xlsx: L3 hostile ensemble recall +4.60pp above LWM (29.01% → 33.62%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.34pp BELOW LOW-WATER-MARK (90.99% → 72.65%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
