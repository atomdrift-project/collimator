# Promote REJECTED — `c8cff3b313dd61b0` on `filetypes/c`

Generated 2026-11-12T20:25:27Z

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-12T12-44-09_20261112T123949-promote-c8cff3b313dd61b0_azoth-validate.log; tail:   elf                  +68 caught   recall  95.69% →  95.61%
  npm                  +35 caught   recall  72.60% →  71.89%
  macho                +26 caught   recall  77.98% →  79.12%

largest per-filetype moves at L25 (informational):
  c                    +96 caught   recall  40.07% →  44.49%
  elf                  +87 caught   recall  98.37% →  98.36%
  npm                  +43 caught   recall  74.45% →  73.91%
  dos_com              +34 caught   recall  79.65% →  80.34%
  macho                +27 caught   recall  85.71% →  86.54%
  pe                -3,482 caught   recall  83.01% →  81.02%
  zip                  -50 caught   recall  80.85% →  80.30%
  csharp                -9 caught   recall  40.87% →  38.72%
  xml                   -1 caught   recall  49.76% →  48.60%

models that got better (PR-AUC moved ≥ 0.001, informational):
  filetypes/c                                   PR-AUC 0.8385 → 0.8715 (+0.0330)   zero-FP recall -15.65pp   2,106 malware  retrained
  filetypes/gem                                 PR-AUC 0.9286 → 0.9334 (+0.0048)   zero-FP recall +0.54pp   54 malware  unchanged model
  filegroups/historical_filetypes_macho_frozen  PR-AUC 0.9780 → 0.9806 (+0.0026)   zero-FP recall -0.30pp   364 malware  unchanged model
  filetypes/macho                               PR-AUC 0.9779 → 0.9803 (+0.0024)   zero-FP recall -0.21pp   364 malware  unchanged model
  filetypes/java_class                          PR-AUC 0.4477 → 0.4491 (+0.0014)   zero-FP recall +0.00pp   286 malware  unchanged model
  filegroups/filegroups_source_oct26            PR-AUC 0.4122 → 0.4135 (+0.0012)   zero-FP recall -0.05pp   1,100 malware  unchanged model
  filegroups/perl_hnm_recovery                  PR-AUC 0.9574 → 0.9586 (+0.0012)   zero-FP recall +0.31pp   57 malware  unchanged model

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/nupkg                               PR-AUC 0.9429 → 0.7877 (-0.1551)   zero-FP recall -13.33pp   6 malware  unchanged model
  filetypes/go_module                           PR-AUC 1.0000 → 0.8774 (-0.1226)   zero-FP recall -50.00pp   6 malware  unchanged model
  filetypes/yaml                                PR-AUC 0.2625 → 0.1916 (-0.0709)   zero-FP recall -6.82pp   11 malware  unchanged model
  filetypes/github_actions                      PR-AUC 0.4726 → 0.4441 (-0.0284)   zero-FP recall -8.33pp   18 malware  unchanged model
  filegroups/rare_archive_recovery              PR-AUC 0.9936 → 0.9767 (-0.0169)   zero-FP recall -2.93pp   123 malware  unchanged model
  filetypes/xml                                 PR-AUC 0.7516 → 0.7411 (-0.0105)   zero-FP recall -0.42pp   214 malware  unchanged model
  filegroups/data_recovery                      PR-AUC 0.8790 → 0.8733 (-0.0058)   zero-FP recall -1.40pp   52 malware  unchanged model
  filetypes/text                                PR-AUC 0.8682 → 0.8629 (-0.0053)   zero-FP recall -0.08pp   807 malware  unchanged model
  filegroups/text_retained_hnm_recovery         PR-AUC 0.8589 → 0.8544 (-0.0046)   zero-FP recall -0.13pp   807 malware  unchanged model
  filetypes/ruby                                PR-AUC 0.9255 → 0.9211 (-0.0044)   zero-FP recall -1.89pp   31 malware  unchanged model
  filetypes/crx                                 PR-AUC 0.9795 → 0.9761 (-0.0034)   zero-FP recall -0.09pp   309 malware  unchanged model
  filegroups/crx_selected                       PR-AUC 0.9779 → 0.9745 (-0.0034)   zero-FP recall -0.10pp   309 malware  unchanged model
  filegroups/filetypes_crx_oct26                PR-AUC 0.9761 → 0.9729 (-0.0033)   zero-FP recall -0.10pp   309 malware  unchanged model
  filetypes/pkg_info                            PR-AUC 0.9019 → 0.8993 (-0.0026)   zero-FP recall +0.00pp   26 malware  unchanged model
  filegroups/filetypes_go_oct26                 PR-AUC 0.8374 → 0.8362 (-0.0011)   zero-FP recall -0.05pp   1,100 malware  unchanged model
  filegroups/config                             PR-AUC 0.9748 → 0.9738 (-0.0011)   zero-FP recall -0.06pp   2,930 malware  unchanged model
  filegroups/go_general_layout_recovery         PR-AUC 0.8831 → 0.8821 (-0.0010)   zero-FP recall -0.03pp   1,100 malware  unchanged model

FAIL: not better overall, not shipping —
  - L0 FPs rose 540 → 595 (more than noise allows: ≤ 593)
  - L25 recall fell 1.12pp (more than 0.20pp)
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9934 -> 0.9963; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c8cff3b313dd61b0` | `6c863253b7999ef1` | `c9f9546c2fdd78e1` |
| PR AUC | 0.9934 | 0.9963 | 0.9907 |
| ROC AUC | 0.9977 | 0.9987 | 0.9984 |
| F1 | 0.9660 | 0.9782 | 0.9698 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-11-12T12-44-09_20261112T123949-promote-c8cff3b313dd61b0_azoth-validate.log; tail:   elf                  +68 caught   recall  95.69% →  95.61%
  npm                  +35 caught   recall  72.60% →  71.89%
  macho                +26 caught   recall  77.98% →  79.12%

largest per-filetype moves at L25 (informational):
  c                    +96 caught   recall  40.07% →  44.49%
  elf                  +87 caught   recall  98.37% →  98.36%
  npm                  +43 caught   recall  74.45% →  73.91%
  dos_com              +34 caught   recall  79.65% →  80.34%
  macho                +27 caught   recall  85.71% →  86.54%
  pe                -3,482 caught   recall  83.01% →  81.02%
  zip                  -50 caught   recall  80.85% →  80.30%
  csharp                -9 caught   recall  40.87% →  38.72%
  xml                   -1 caught   recall  49.76% →  48.60%

models that got better (PR-AUC moved ≥ 0.001, informational):
  filetypes/c                                   PR-AUC 0.8385 → 0.8715 (+0.0330)   zero-FP recall -15.65pp   2,106 malware  retrained
  filetypes/gem                                 PR-AUC 0.9286 → 0.9334 (+0.0048)   zero-FP recall +0.54pp   54 malware  unchanged model
  filegroups/historical_filetypes_macho_frozen  PR-AUC 0.9780 → 0.9806 (+0.0026)   zero-FP recall -0.30pp   364 malware  unchanged model
  filetypes/macho                               PR-AUC 0.9779 → 0.9803 (+0.0024)   zero-FP recall -0.21pp   364 malware  unchanged model
  filetypes/java_class                          PR-AUC 0.4477 → 0.4491 (+0.0014)   zero-FP recall +0.00pp   286 malware  unchanged model
  filegroups/filegroups_source_oct26            PR-AUC 0.4122 → 0.4135 (+0.0012)   zero-FP recall -0.05pp   1,100 malware  unchanged model
  filegroups/perl_hnm_recovery                  PR-AUC 0.9574 → 0.9586 (+0.0012)   zero-FP recall +0.31pp   57 malware  unchanged model

models that got worse (PR-AUC moved ≥ 0.001, informational):
  filetypes/nupkg                               PR-AUC 0.9429 → 0.7877 (-0.1551)   zero-FP recall -13.33pp   6 malware  unchanged model
  filetypes/go_module                           PR-AUC 1.0000 → 0.8774 (-0.1226)   zero-FP recall -50.00pp   6 malware  unchanged model
  filetypes/yaml                                PR-AUC 0.2625 → 0.1916 (-0.0709)   zero-FP recall -6.82pp   11 malware  unchanged model
  filetypes/github_actions                      PR-AUC 0.4726 → 0.4441 (-0.0284)   zero-FP recall -8.33pp   18 malware  unchanged model
  filegroups/rare_archive_recovery              PR-AUC 0.9936 → 0.9767 (-0.0169)   zero-FP recall -2.93pp   123 malware  unchanged model
  filetypes/xml                                 PR-AUC 0.7516 → 0.7411 (-0.0105)   zero-FP recall -0.42pp   214 malware  unchanged model
  filegroups/data_recovery                      PR-AUC 0.8790 → 0.8733 (-0.0058)   zero-FP recall -1.40pp   52 malware  unchanged model
  filetypes/text                                PR-AUC 0.8682 → 0.8629 (-0.0053)   zero-FP recall -0.08pp   807 malware  unchanged model
  filegroups/text_retained_hnm_recovery         PR-AUC 0.8589 → 0.8544 (-0.0046)   zero-FP recall -0.13pp   807 malware  unchanged model
  filetypes/ruby                                PR-AUC 0.9255 → 0.9211 (-0.0044)   zero-FP recall -1.89pp   31 malware  unchanged model
  filetypes/crx                                 PR-AUC 0.9795 → 0.9761 (-0.0034)   zero-FP recall -0.09pp   309 malware  unchanged model
  filegroups/crx_selected                       PR-AUC 0.9779 → 0.9745 (-0.0034)   zero-FP recall -0.10pp   309 malware  unchanged model
  filegroups/filetypes_crx_oct26                PR-AUC 0.9761 → 0.9729 (-0.0033)   zero-FP recall -0.10pp   309 malware  unchanged model
  filetypes/pkg_info                            PR-AUC 0.9019 → 0.8993 (-0.0026)   zero-FP recall +0.00pp   26 malware  unchanged model
  filegroups/filetypes_go_oct26                 PR-AUC 0.8374 → 0.8362 (-0.0011)   zero-FP recall -0.05pp   1,100 malware  unchanged model
  filegroups/config                             PR-AUC 0.9748 → 0.9738 (-0.0011)   zero-FP recall -0.06pp   2,930 malware  unchanged model
  filegroups/go_general_layout_recovery         PR-AUC 0.8831 → 0.8821 (-0.0010)   zero-FP recall -0.03pp   1,100 malware  unchanged model

FAIL: not better overall, not shipping —
  - L0 FPs rose 540 → 595 (more than noise allows: ≤ 593)
  - L25 recall fell 1.12pp (more than 0.20pp)
  - neither L0 nor L25 recall rose more than 0.10pp
Set AZOTH_ALLOW_REGRESSION=1 to ship anyway after review.
make[1]: *** [Makefile:1357: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')
