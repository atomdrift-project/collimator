# Promote REJECTED — `65ba9452a2426a47` on `filegroups/source`

Generated 2026-06-28T08:30:21Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-25-34_20260628T082533-promote-65ba9452a2426a47_azoth-validate.log; tail: 2026-06-28 04:29:57,067 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-28 04:29:57,077 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-28 04:29:57,281 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-28 04:29:57,497 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-28 04:29:57,668 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-06-28 04:29:57,861 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-28 04:29:57,995 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-28 04:29:58,208 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-28 04:29:58,403 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-28 04:29:58,588 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-28 04:29:58,783 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-28 04:29:58,952 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-28 04:29:59,145 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-28 04:29:59,370 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-28 04:29:59,545 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-28 04:29:59,716 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-28 04:29:59,952 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-28 04:30:00,147 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-28 04:30:00,304 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-28 04:30:00,531 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-28 04:30:00,702 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-28 04:30:00,888 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-28 04:30:01,104 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-28 04:30:01,310 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-28 04:30:01,474 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-28 04:30:01,663 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-28 04:30:01,842 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-28 04:30:02,102 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-28 04:30:02,219 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-28 04:30:02,485 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-28 04:30:02,621 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-28 04:30:02,748 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-28 04:30:02,934 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-28 04:30:03,089 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1398, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1287, in main
    score_table_hash = _write_score_table(
                       ^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 997, in _write_score_table
    return _file_sha256(path)
           ^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 38, in _file_sha256
    with open(path, "rb") as f:
         ^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filegroups-source-65ba9452a2426a47/score_table.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9956)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `65ba9452a2426a47` | `bc9d4bb5a9c49cb1` | `8d3f2419cb9a8342` |
| PR AUC | 0.9956 | 0.9967 | 0.9966 |
| ROC AUC | 0.9960 | 0.9971 | 0.9970 |
| F1 | 0.9695 | 0.9755 | 0.9760 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-28T08-25-34_20260628T082533-promote-65ba9452a2426a47_azoth-validate.log; tail: 2026-06-28 04:29:57,067 INFO azoth_calibrate_ensemble: filetypes/php: using cached scores
2026-06-28 04:29:57,077 INFO azoth_calibrate_ensemble: filetypes/png: using cached scores
2026-06-28 04:29:57,281 INFO azoth_calibrate_ensemble: filetypes/go: using cached scores
2026-06-28 04:29:57,497 INFO azoth_calibrate_ensemble: filetypes/text: using cached scores
2026-06-28 04:29:57,668 INFO azoth_calibrate_ensemble: filetypes/java: using cached scores
2026-06-28 04:29:57,861 INFO azoth_calibrate_ensemble: filetypes/zip: using cached scores
2026-06-28 04:29:57,995 INFO azoth_calibrate_ensemble: filetypes/shell: using cached scores
2026-06-28 04:29:58,208 INFO azoth_calibrate_ensemble: filetypes/kotlin: using cached scores
2026-06-28 04:29:58,403 INFO azoth_calibrate_ensemble: filetypes/csharp: using cached scores
2026-06-28 04:29:58,588 INFO azoth_calibrate_ensemble: filetypes/tar: using cached scores
2026-06-28 04:29:58,783 INFO azoth_calibrate_ensemble: filetypes/xlsx: using cached scores
2026-06-28 04:29:58,952 INFO azoth_calibrate_ensemble: filetypes/xls: using cached scores
2026-06-28 04:29:59,145 INFO azoth_calibrate_ensemble: filetypes/package.json: using cached scores
2026-06-28 04:29:59,370 INFO azoth_calibrate_ensemble: filetypes/perl: using cached scores
2026-06-28 04:29:59,545 INFO azoth_calibrate_ensemble: filetypes/ruby: using cached scores
2026-06-28 04:29:59,716 INFO azoth_calibrate_ensemble: filetypes/jpeg: using cached scores
2026-06-28 04:29:59,952 INFO azoth_calibrate_ensemble: filetypes/objc: using cached scores
2026-06-28 04:30:00,147 INFO azoth_calibrate_ensemble: filetypes/macho: using cached scores
2026-06-28 04:30:00,304 INFO azoth_calibrate_ensemble: filetypes/html: using cached scores
2026-06-28 04:30:00,531 INFO azoth_calibrate_ensemble: filetypes/vbs: using cached scores
2026-06-28 04:30:00,702 INFO azoth_calibrate_ensemble: filetypes/pkg-info: using cached scores
2026-06-28 04:30:00,888 INFO azoth_calibrate_ensemble: filetypes/ole: using cached scores
2026-06-28 04:30:01,104 INFO azoth_calibrate_ensemble: filetypes/plist: using cached scores
2026-06-28 04:30:01,310 INFO azoth_calibrate_ensemble: filetypes/jar: using cached scores
2026-06-28 04:30:01,474 INFO azoth_calibrate_ensemble: filetypes/deb: using cached scores
2026-06-28 04:30:01,663 INFO azoth_calibrate_ensemble: filetypes/powershell: using cached scores
2026-06-28 04:30:01,842 INFO azoth_calibrate_ensemble: filetypes/whl: using cached scores
2026-06-28 04:30:02,102 INFO azoth_calibrate_ensemble: filetypes/msi: using cached scores
2026-06-28 04:30:02,219 INFO azoth_calibrate_ensemble: filetypes/docx: using cached scores
2026-06-28 04:30:02,485 INFO azoth_calibrate_ensemble: filetypes/npm: using cached scores
2026-06-28 04:30:02,621 INFO azoth_calibrate_ensemble: filetypes/cargo.toml: using cached scores
2026-06-28 04:30:02,748 INFO azoth_calibrate_ensemble: filetypes/dockerfile: using cached scores
2026-06-28 04:30:02,934 INFO azoth_calibrate_ensemble: filetypes/crx: using cached scores
2026-06-28 04:30:03,089 INFO azoth_calibrate_ensemble: filetypes/chrome-manifest: using cached scores
Traceback (most recent call last):
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1398, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 1287, in main
    score_table_hash = _write_score_table(
                       ^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 997, in _write_score_table
    return _file_sha256(path)
           ^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/azoth_calibrate_ensemble.py", line 38, in _file_sha256
    with open(path, "rb") as f:
         ^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '/home/t/collimator/out/models/azoth-candidate-filegroups-source-65ba9452a2426a47/score_table.npz'
make[1]: *** [Makefile:1234: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
