# Promote REJECTED — `b1121d062d1ee319` on `filetypes/lnk`

Generated 2026-11-10T19:48:59Z

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-10T10-58-42_20261110T105757-promote-b1121d062d1ee319_azoth-validate.log; tail:   filegroups/nightly_filegroups_config_frozen   PR-AUC 0.7595 → 0.7643 (+0.0048)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/text                                PR-AUC 0.8624 → 0.8663 (+0.0039)   zero-FP recall -3.84pp   806 malware  retrained
  filegroups/tar_benign_weight_recovery         PR-AUC 0.9782 → 0.9820 (+0.0038)   zero-FP recall -0.77pp   1,779 malware  unchanged model
  filegroups/tar_retained_hnm_recovery          PR-AUC 0.9798 → 0.9832 (+0.0034)   zero-FP recall -1.22pp   1,779 malware  unchanged model
  filegroups/source                             PR-AUC 0.9010 → 0.9043 (+0.0033)   zero-FP recall +13.22pp   7,396 malware  retrained
  filegroups/tar_general_layout_recovery        PR-AUC 0.9791 → 0.9824 (+0.0032)   zero-FP recall -1.46pp   1,779 malware  unchanged model
  filegroups/filetypes_tar_oct26                PR-AUC 0.9671 → 0.9699 (+0.0028)   zero-FP recall -1.06pp   1,779 malware  unchanged model
  filetypes/shell                               PR-AUC 0.9902 → 0.9922 (+0.0020)   zero-FP recall +13.01pp   2,446 malware  retrained
  filetypes/nupkg                               PR-AUC 0.8333 → 0.8352 (+0.0019)   zero-FP recall +16.67pp   6 malware  retrained
  filetypes/asp                                 PR-AUC 0.9863 → 0.9881 (+0.0018)   zero-FP recall +8.11pp   37 malware  retrained
  filegroups/filegroups_archive_oct26           PR-AUC 0.9461 → 0.9478 (+0.0017)   zero-FP recall -0.35pp   5,789 malware  unchanged model
  filegroups/historical_filetypes_macho_frozen  PR-AUC 0.9776 → 0.9792 (+0.0016)   zero-FP recall +0.44pp   348 malware  unchanged model
  filegroups/portable                           PR-AUC 0.9330 → 0.9345 (+0.0015)   zero-FP recall -3.34pp   706 malware  retrained
  filegroups/archive                            PR-AUC 0.9618 → 0.9631 (+0.0014)   zero-FP recall +2.92pp   25,670 malware  retrained
  filetypes/lnk                                 PR-AUC 0.9986 → 0.9998 (+0.0012)   zero-FP recall +16.30pp   579 malware  retrained
  filetypes/macho                               PR-AUC 0.9771 → 0.9782 (+0.0011)   zero-FP recall +4.14pp   348 malware  retrained

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/java_class                          PR-AUC 0.2779 → 0.2343 (-0.0435)   zero-FP recall +0.00pp   286 malware  retrained
  filetypes/pkg_info                            PR-AUC 0.9377 → 0.8989 (-0.0388)   zero-FP recall -9.49pp   26 malware  retrained
  filetypes/apk_android                         PR-AUC 0.9784 → 0.9409 (-0.0374)   zero-FP recall -2.85pp   510 malware  retrained
  filegroups/json_general_layout_recovery       PR-AUC 0.2124 → 0.1978 (-0.0147)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/jpeg                                PR-AUC 0.8325 → 0.8192 (-0.0133)   zero-FP recall -4.07pp   172 malware  retrained
  filetypes/ruby                                PR-AUC 0.9230 → 0.9136 (-0.0094)   zero-FP recall +3.92pp   30 malware  retrained
  filegroups/text_retained_hnm_recovery         PR-AUC 0.8661 → 0.8574 (-0.0087)   zero-FP recall -0.11pp   806 malware  unchanged model
  filetypes/crate                               PR-AUC 0.0845 → 0.0759 (-0.0086)   zero-FP recall +0.00pp   6 malware  retrained
  filegroups/rare_archive_recovery              PR-AUC 0.9852 → 0.9768 (-0.0084)   zero-FP recall -1.63pp   123 malware  unchanged model
  filetypes/jar                                 PR-AUC 0.9737 → 0.9671 (-0.0066)   zero-FP recall -1.21pp   482 malware  retrained
  filegroups/png_general_layout_recovery        PR-AUC 0.8641 → 0.8582 (-0.0059)   zero-FP recall +0.00pp   959 malware  unchanged model
  filegroups/data_recovery                      PR-AUC 0.8848 → 0.8792 (-0.0056)   zero-FP recall -5.88pp   51 malware  unchanged model
  filegroups/png_retained_hnm_recovery          PR-AUC 0.9519 → 0.9467 (-0.0053)   zero-FP recall -0.21pp   959 malware  unchanged model
  filegroups/filetypes_go_oct26                 PR-AUC 0.8428 → 0.8377 (-0.0051)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filegroups/go_retained_hnm_recovery           PR-AUC 0.8166 → 0.8129 (-0.0037)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filetypes/go                                  PR-AUC 0.8217 → 0.8183 (-0.0034)   zero-FP recall -1.02pp   1,098 malware  retrained
  filetypes/php                                 PR-AUC 0.9656 → 0.9626 (-0.0030)   zero-FP recall +0.71pp   764 malware  retrained
  filegroups/go_general_layout_recovery         PR-AUC 0.8922 → 0.8893 (-0.0029)   zero-FP recall -0.01pp   1,098 malware  unchanged model
  filegroups/filegroups_source_oct26            PR-AUC 0.4241 → 0.4212 (-0.0029)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filetypes/c                                   PR-AUC 0.8425 → 0.8396 (-0.0028)   zero-FP recall +7.09pp   2,103 malware  retrained
  filetypes/png                                 PR-AUC 0.9585 → 0.9561 (-0.0024)   zero-FP recall +4.80pp   959 malware  retrained
  filegroups/nightly_filetypes_json_frozen      PR-AUC 0.2781 → 0.2763 (-0.0018)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/lua                                 PR-AUC 0.9620 → 0.9605 (-0.0015)   zero-FP recall +14.29pp   14 malware  retrained
  filetypes/python_sdist                        PR-AUC 0.9992 → 0.9981 (-0.0010)   zero-FP recall +0.30pp   369 malware  retrained

FAIL: not better overall, not shipping —
  - L0 recall fell 3.97pp (more than 0.20pp)
  - L25 recall fell 1.53pp (more than 0.20pp)
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9985 -> 0.9992; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b1121d062d1ee319` | `e015482c80d791b5` | `f97b643d69d79afc` |
| PR AUC | 0.9985 | 0.9992 | 0.9985 |
| ROC AUC | 0.9946 | 0.9969 | 0.9946 |
| F1 | 0.9839 | 0.9904 | 0.9839 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-10T10-58-42_20261110T105757-promote-b1121d062d1ee319_azoth-validate.log; tail:   filegroups/nightly_filegroups_config_frozen   PR-AUC 0.7595 → 0.7643 (+0.0048)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/text                                PR-AUC 0.8624 → 0.8663 (+0.0039)   zero-FP recall -3.84pp   806 malware  retrained
  filegroups/tar_benign_weight_recovery         PR-AUC 0.9782 → 0.9820 (+0.0038)   zero-FP recall -0.77pp   1,779 malware  unchanged model
  filegroups/tar_retained_hnm_recovery          PR-AUC 0.9798 → 0.9832 (+0.0034)   zero-FP recall -1.22pp   1,779 malware  unchanged model
  filegroups/source                             PR-AUC 0.9010 → 0.9043 (+0.0033)   zero-FP recall +13.22pp   7,396 malware  retrained
  filegroups/tar_general_layout_recovery        PR-AUC 0.9791 → 0.9824 (+0.0032)   zero-FP recall -1.46pp   1,779 malware  unchanged model
  filegroups/filetypes_tar_oct26                PR-AUC 0.9671 → 0.9699 (+0.0028)   zero-FP recall -1.06pp   1,779 malware  unchanged model
  filetypes/shell                               PR-AUC 0.9902 → 0.9922 (+0.0020)   zero-FP recall +13.01pp   2,446 malware  retrained
  filetypes/nupkg                               PR-AUC 0.8333 → 0.8352 (+0.0019)   zero-FP recall +16.67pp   6 malware  retrained
  filetypes/asp                                 PR-AUC 0.9863 → 0.9881 (+0.0018)   zero-FP recall +8.11pp   37 malware  retrained
  filegroups/filegroups_archive_oct26           PR-AUC 0.9461 → 0.9478 (+0.0017)   zero-FP recall -0.35pp   5,789 malware  unchanged model
  filegroups/historical_filetypes_macho_frozen  PR-AUC 0.9776 → 0.9792 (+0.0016)   zero-FP recall +0.44pp   348 malware  unchanged model
  filegroups/portable                           PR-AUC 0.9330 → 0.9345 (+0.0015)   zero-FP recall -3.34pp   706 malware  retrained
  filegroups/archive                            PR-AUC 0.9618 → 0.9631 (+0.0014)   zero-FP recall +2.92pp   25,670 malware  retrained
  filetypes/lnk                                 PR-AUC 0.9986 → 0.9998 (+0.0012)   zero-FP recall +16.30pp   579 malware  retrained
  filetypes/macho                               PR-AUC 0.9771 → 0.9782 (+0.0011)   zero-FP recall +4.14pp   348 malware  retrained

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/java_class                          PR-AUC 0.2779 → 0.2343 (-0.0435)   zero-FP recall +0.00pp   286 malware  retrained
  filetypes/pkg_info                            PR-AUC 0.9377 → 0.8989 (-0.0388)   zero-FP recall -9.49pp   26 malware  retrained
  filetypes/apk_android                         PR-AUC 0.9784 → 0.9409 (-0.0374)   zero-FP recall -2.85pp   510 malware  retrained
  filegroups/json_general_layout_recovery       PR-AUC 0.2124 → 0.1978 (-0.0147)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/jpeg                                PR-AUC 0.8325 → 0.8192 (-0.0133)   zero-FP recall -4.07pp   172 malware  retrained
  filetypes/ruby                                PR-AUC 0.9230 → 0.9136 (-0.0094)   zero-FP recall +3.92pp   30 malware  retrained
  filegroups/text_retained_hnm_recovery         PR-AUC 0.8661 → 0.8574 (-0.0087)   zero-FP recall -0.11pp   806 malware  unchanged model
  filetypes/crate                               PR-AUC 0.0845 → 0.0759 (-0.0086)   zero-FP recall +0.00pp   6 malware  retrained
  filegroups/rare_archive_recovery              PR-AUC 0.9852 → 0.9768 (-0.0084)   zero-FP recall -1.63pp   123 malware  unchanged model
  filetypes/jar                                 PR-AUC 0.9737 → 0.9671 (-0.0066)   zero-FP recall -1.21pp   482 malware  retrained
  filegroups/png_general_layout_recovery        PR-AUC 0.8641 → 0.8582 (-0.0059)   zero-FP recall +0.00pp   959 malware  unchanged model
  filegroups/data_recovery                      PR-AUC 0.8848 → 0.8792 (-0.0056)   zero-FP recall -5.88pp   51 malware  unchanged model
  filegroups/png_retained_hnm_recovery          PR-AUC 0.9519 → 0.9467 (-0.0053)   zero-FP recall -0.21pp   959 malware  unchanged model
  filegroups/filetypes_go_oct26                 PR-AUC 0.8428 → 0.8377 (-0.0051)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filegroups/go_retained_hnm_recovery           PR-AUC 0.8166 → 0.8129 (-0.0037)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filetypes/go                                  PR-AUC 0.8217 → 0.8183 (-0.0034)   zero-FP recall -1.02pp   1,098 malware  retrained
  filetypes/php                                 PR-AUC 0.9656 → 0.9626 (-0.0030)   zero-FP recall +0.71pp   764 malware  retrained
  filegroups/go_general_layout_recovery         PR-AUC 0.8922 → 0.8893 (-0.0029)   zero-FP recall -0.01pp   1,098 malware  unchanged model
  filegroups/filegroups_source_oct26            PR-AUC 0.4241 → 0.4212 (-0.0029)   zero-FP recall -0.02pp   1,098 malware  unchanged model
  filetypes/c                                   PR-AUC 0.8425 → 0.8396 (-0.0028)   zero-FP recall +7.09pp   2,103 malware  retrained
  filetypes/png                                 PR-AUC 0.9585 → 0.9561 (-0.0024)   zero-FP recall +4.80pp   959 malware  retrained
  filegroups/nightly_filetypes_json_frozen      PR-AUC 0.2781 → 0.2763 (-0.0018)   zero-FP recall +0.00pp   36 malware  unchanged model
  filetypes/lua                                 PR-AUC 0.9620 → 0.9605 (-0.0015)   zero-FP recall +14.29pp   14 malware  retrained
  filetypes/python_sdist                        PR-AUC 0.9992 → 0.9981 (-0.0010)   zero-FP recall +0.30pp   369 malware  retrained

FAIL: not better overall, not shipping —
  - L0 recall fell 3.97pp (more than 0.20pp)
  - L25 recall fell 1.53pp (more than 0.20pp)
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')
