# Promote REJECTED — `d2173256fdf4cd40` on `filetypes/xpi`

Generated 2026-11-06T19:53:27Z

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-06T11-36-01_20261106T113502-promote-d2173256fdf4cd40_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.eCRZxSrNQf
azoth bundle ok: /tmp/tmp.eCRZxSrNQf
publish gate: staged /tmp/tmp.eCRZxSrNQf vs deployed /home/t/.local/share/atomdrift/scan/models/azoth
  test partition: 378,081 → 378,508 malware, 2,275,835 → 2,293,689 benign
  L0   recall  76.37% →  76.29% (-0.07pp)   FP 630 → 634 (allowed ≤ 685)
  L25  recall  84.14% →  84.10% (-0.04pp)   FP 890 → 895 (allowed ≤ 957)

largest per-filetype moves at L0 (informational):
  pe                   +35 caught   recall  74.08% →  74.04%
  npm                  +28 caught   recall  73.01% →  72.31%
  elf                  +20 caught   recall  96.16% →  96.14%
  apk_android          +10 caught   recall  93.80% →  93.92%
  macho                 +9 caught   recall  79.76% →  80.06%
  csharp               -67 caught   recall  35.84% →  20.50%
  7z                    -1 caught   recall  38.29% →  38.13%
  xpi                   -1 caught   recall 100.00% →  90.91%

largest per-filetype moves at L25 (informational):
  pe                   +53 caught   recall  83.13% →  83.09%
  npm                  +31 caught   recall  74.62% →  73.97%
  dos_com              +29 caught   recall  87.84% →  88.24%
  elf                  +22 caught   recall  98.24% →  98.23%
  apk_android          +10 caught   recall  98.00% →  98.04%
  csharp                -5 caught   recall  42.47% →  41.23%
  rust                  -2 caught   recall  49.15% →  45.76%
  xpi                   -1 caught   recall 100.00% →  90.91%

models that got better (PR-AUC moved ≥ 0.001, informational):
  filetypes/github_actions               PR-AUC 0.3902 → 0.5558 (+0.1656)   zero-FP recall +0.00pp   10 malware  unchanged model

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/nupkg                        PR-AUC 0.8333 → 0.6267 (-0.2066)   zero-FP recall -16.67pp   4 malware  unchanged model
  filetypes/gem                          PR-AUC 0.9115 → 0.8795 (-0.0320)   zero-FP recall -3.33pp   53 malware  unchanged model
  filegroups/rare_archive_recovery       PR-AUC 0.9900 → 0.9786 (-0.0113)   zero-FP recall -1.10pp   121 malware  unchanged model
  filetypes/text                         PR-AUC 0.8624 → 0.8587 (-0.0037)   zero-FP recall -0.12pp   806 malware  unchanged model
  filetypes/crx                          PR-AUC 0.9526 → 0.9492 (-0.0034)   zero-FP recall -0.03pp   298 malware  unchanged model
  filegroups/text_retained_hnm_recovery  PR-AUC 0.8661 → 0.8627 (-0.0034)   zero-FP recall -0.11pp   806 malware  unchanged model
  filegroups/crx_selected                PR-AUC 0.9573 → 0.9540 (-0.0033)   zero-FP recall -0.06pp   298 malware  unchanged model
  filegroups/filetypes_crx_oct26         PR-AUC 0.9591 → 0.9558 (-0.0033)   zero-FP recall -0.17pp   298 malware  unchanged model
  filegroups/data_recovery               PR-AUC 0.8848 → 0.8818 (-0.0030)   zero-FP recall +0.00pp   51 malware  unchanged model
  filegroups/filetypes_go_oct26          PR-AUC 0.8428 → 0.8414 (-0.0014)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filegroups/go_general_layout_recovery  PR-AUC 0.8922 → 0.8909 (-0.0013)   zero-FP recall -0.01pp   1,098 malware  unchanged model
  filetypes/apk_android                  PR-AUC 0.9784 → 0.9771 (-0.0012)   zero-FP recall -0.11pp   510 malware  unchanged model
  filetypes/crate                        PR-AUC 0.0845 → 0.0833 (-0.0012)   zero-FP recall +0.00pp   6 malware  unchanged model

FAIL: not better overall, not shipping —
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9192 -> 0.9283; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d2173256fdf4cd40` | `380524cfb3066eca` | `c163750326d1ecd2` |
| PR AUC | 0.9192 | 0.9283 | 0.9192 |
| ROC AUC | 0.9990 | 0.9991 | 0.9990 |
| F1 | 0.7500 | 0.9474 | 0.7500 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-06T11-36-01_20261106T113502-promote-d2173256fdf4cd40_azoth-validate.log; tail: staged runtime azoth bundle: /tmp/tmp.eCRZxSrNQf
azoth bundle ok: /tmp/tmp.eCRZxSrNQf
publish gate: staged /tmp/tmp.eCRZxSrNQf vs deployed /home/t/.local/share/atomdrift/scan/models/azoth
  test partition: 378,081 → 378,508 malware, 2,275,835 → 2,293,689 benign
  L0   recall  76.37% →  76.29% (-0.07pp)   FP 630 → 634 (allowed ≤ 685)
  L25  recall  84.14% →  84.10% (-0.04pp)   FP 890 → 895 (allowed ≤ 957)

largest per-filetype moves at L0 (informational):
  pe                   +35 caught   recall  74.08% →  74.04%
  npm                  +28 caught   recall  73.01% →  72.31%
  elf                  +20 caught   recall  96.16% →  96.14%
  apk_android          +10 caught   recall  93.80% →  93.92%
  macho                 +9 caught   recall  79.76% →  80.06%
  csharp               -67 caught   recall  35.84% →  20.50%
  7z                    -1 caught   recall  38.29% →  38.13%
  xpi                   -1 caught   recall 100.00% →  90.91%

largest per-filetype moves at L25 (informational):
  pe                   +53 caught   recall  83.13% →  83.09%
  npm                  +31 caught   recall  74.62% →  73.97%
  dos_com              +29 caught   recall  87.84% →  88.24%
  elf                  +22 caught   recall  98.24% →  98.23%
  apk_android          +10 caught   recall  98.00% →  98.04%
  csharp                -5 caught   recall  42.47% →  41.23%
  rust                  -2 caught   recall  49.15% →  45.76%
  xpi                   -1 caught   recall 100.00% →  90.91%

models that got better (PR-AUC moved ≥ 0.001, informational):
  filetypes/github_actions               PR-AUC 0.3902 → 0.5558 (+0.1656)   zero-FP recall +0.00pp   10 malware  unchanged model

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/nupkg                        PR-AUC 0.8333 → 0.6267 (-0.2066)   zero-FP recall -16.67pp   4 malware  unchanged model
  filetypes/gem                          PR-AUC 0.9115 → 0.8795 (-0.0320)   zero-FP recall -3.33pp   53 malware  unchanged model
  filegroups/rare_archive_recovery       PR-AUC 0.9900 → 0.9786 (-0.0113)   zero-FP recall -1.10pp   121 malware  unchanged model
  filetypes/text                         PR-AUC 0.8624 → 0.8587 (-0.0037)   zero-FP recall -0.12pp   806 malware  unchanged model
  filetypes/crx                          PR-AUC 0.9526 → 0.9492 (-0.0034)   zero-FP recall -0.03pp   298 malware  unchanged model
  filegroups/text_retained_hnm_recovery  PR-AUC 0.8661 → 0.8627 (-0.0034)   zero-FP recall -0.11pp   806 malware  unchanged model
  filegroups/crx_selected                PR-AUC 0.9573 → 0.9540 (-0.0033)   zero-FP recall -0.06pp   298 malware  unchanged model
  filegroups/filetypes_crx_oct26         PR-AUC 0.9591 → 0.9558 (-0.0033)   zero-FP recall -0.17pp   298 malware  unchanged model
  filegroups/data_recovery               PR-AUC 0.8848 → 0.8818 (-0.0030)   zero-FP recall +0.00pp   51 malware  unchanged model
  filegroups/filetypes_go_oct26          PR-AUC 0.8428 → 0.8414 (-0.0014)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filegroups/go_general_layout_recovery  PR-AUC 0.8922 → 0.8909 (-0.0013)   zero-FP recall -0.01pp   1,098 malware  unchanged model
  filetypes/apk_android                  PR-AUC 0.9784 → 0.9771 (-0.0012)   zero-FP recall -0.11pp   510 malware  unchanged model
  filetypes/crate                        PR-AUC 0.0845 → 0.0833 (-0.0012)   zero-FP recall +0.00pp   6 malware  unchanged model

FAIL: not better overall, not shipping —
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')
