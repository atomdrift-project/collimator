# Promote REJECTED — `589b9b4aec45069c` on `filegroups/documents`

Generated 2026-05-26T22:12:07Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T22-08-52_20260526T220842-promote-589b9b4aec45069c_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c
staged runtime azoth bundle: /tmp/tmp.nq0wdNUzv8
azoth bundle ok: /tmp/tmp.nq0wdNUzv8
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  pdf: L3 hostile ensemble recall +13.75pp (7.50% → 21.25%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)
  xlsx: L3 hostile ensemble recall +4.47pp (29.01% → 33.48%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  ole :: filegroups/documents recall@3FP/M +5.62pp (91.70% → 97.32%)
  pdf :: filegroups/documents recall@3FP/M +66.81pp (8.41% → 75.22%)
  rtf :: filegroups/documents recall@3FP/M +1.40pp (96.74% → 98.14%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

16 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +14.84pp above LWM (6.41% → 21.25%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +4.55pp above LWM (9.09% → 13.64%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.26pp BELOW LOW-WATER-MARK (90.99% → 72.73%; LWM tolerance 0.90pp)
  - html: L3 hostile ENSEMBLE recall dropped 16.67pp BELOW LOW-WATER-MARK (16.67% → 0.00%; LWM tolerance 0.90pp)

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
| key | `589b9b4aec45069c` | `6049956f792caeca` | `a6b9dec6045e92dd` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9997 | 0.9997 |
| F1 | 0.9949 | 0.9979 | 0.9980 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T22-08-52_20260526T220842-promote-589b9b4aec45069c_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-documents-589b9b4aec45069c
staged runtime azoth bundle: /tmp/tmp.nq0wdNUzv8
azoth bundle ok: /tmp/tmp.nq0wdNUzv8
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 57 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  pdf: L3 hostile ensemble recall +13.75pp (7.50% → 21.25%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)
  xlsx: L3 hostile ensemble recall +4.47pp (29.01% → 33.48%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  ole :: filegroups/documents recall@3FP/M +5.62pp (91.70% → 97.32%)
  pdf :: filegroups/documents recall@3FP/M +66.81pp (8.41% → 75.22%)
  rtf :: filegroups/documents recall@3FP/M +1.40pp (96.74% → 98.14%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

16 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +14.84pp above LWM (6.41% → 21.25%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +4.55pp above LWM (9.09% → 13.64%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xlsx: L3 hostile ensemble recall +4.47pp above LWM (29.01% → 33.48%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - doc: L3 hostile ENSEMBLE recall dropped 18.26pp BELOW LOW-WATER-MARK (90.99% → 72.73%; LWM tolerance 0.90pp)
  - html: L3 hostile ENSEMBLE recall dropped 16.67pp BELOW LOW-WATER-MARK (16.67% → 0.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
