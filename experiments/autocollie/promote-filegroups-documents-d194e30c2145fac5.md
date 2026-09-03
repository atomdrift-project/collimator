# Promote REJECTED — `d194e30c2145fac5` on `filegroups/documents`

Generated 2026-08-27T02:15:36Z

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-26T23-19-09_20260826T231744-promote-d194e30c2145fac5_azoth-validate.log; tail: 2026-08-26 20:47:41,580 INFO collimator.features: DB-backed feature extraction: 2595 rows, 1 workers, batch_size=1024
2026-08-26 20:47:46,745 INFO azoth_calibrate_ensemble: filetypes/xpi: saved route feature matrix cache out/cache/azoth-route-features/filetypes_xpi-3518179578-885f21f69c776742-1be8cf3f1030d8b0.matrix.npz
2026-08-26 20:47:46,807 INFO azoth_calibrate_ensemble: filetypes/xpi: refreshed 2595 rows in 5.4s (fetch 0.2s, filter 0.0s, load 0.0s, extract 5.2s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1258 nnz=229294)
2026-08-26 20:47:48,898 INFO collimator.features: DB-backed feature extraction: 1156 rows, 1 workers, batch_size=1024
2026-08-26 20:47:49,363 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: saved route feature matrix cache out/cache/azoth-route-features/filetypes_chrome_manifest-3518179578-fe4b991638733ebf-87a79f69348e217b.matrix.npz
2026-08-26 20:47:49,380 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: refreshed 1156 rows in 0.6s (fetch 0.0s, filter 0.0s, load 0.0s, extract 0.5s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=207 nnz=51591)
2026-08-26 20:47:49,540 INFO azoth_calibrate_ensemble: filetypes/gem: saved route feature matrix cache out/cache/azoth-route-features/filetypes_gem-3518179578-8936f70590e49536-7b1d3935a0890612.matrix.npz
2026-08-26 20:47:49,599 INFO azoth_calibrate_ensemble: filetypes/gem: refreshed 4476 rows in 11.1s (fetch 0.2s, filter 0.0s, load 0.0s, extract 10.8s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1737 nnz=426280)
2026-08-26 20:47:51,456 INFO collimator.features: DB-backed feature extraction: 586 rows, 1 workers, batch_size=1024
2026-08-26 20:47:51,720 INFO azoth_calibrate_ensemble: filetypes/applescript: saved route feature matrix cache out/cache/azoth-route-features/filetypes_applescript-3518179578-aa23d75355b05444-cab89b589d12527a.matrix.npz
2026-08-26 20:47:51,726 INFO azoth_calibrate_ensemble: filetypes/applescript: refreshed 586 rows in 0.3s (fetch 0.1s, filter 0.0s, load 0.0s, extract 0.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=350 nnz=15690)
2026-08-26 20:47:51,954 INFO collimator.features: DB-backed feature extraction: 409 rows, 1 workers, batch_size=1024
2026-08-26 20:47:53,876 INFO collimator.features: DB-backed feature extraction: 353 rows, 1 workers, batch_size=1024
2026-08-26 20:47:56,151 INFO azoth_calibrate_ensemble: filetypes/python_sdist: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python_sdist-3518179578-0c62adcec708b562-d542d0d940797a9c.matrix.npz
2026-08-26 20:47:56,158 INFO azoth_calibrate_ensemble: filetypes/python_sdist: refreshed 353 rows in 2.4s (fetch 0.0s, filter 0.0s, load 0.0s, extract 2.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1316 nnz=37136)
2026-08-26 20:47:58,169 INFO azoth_calibrate_ensemble: filetypes/asar: saved route feature matrix cache out/cache/azoth-route-features/filetypes_asar-3518179578-6c8f29d4f7004d6a-b64757bdad8b61fa.matrix.npz
2026-08-26 20:47:58,176 INFO azoth_calibrate_ensemble: filetypes/asar: refreshed 409 rows in 6.3s (fetch 0.0s, filter 0.0s, load 0.0s, extract 6.2s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1482 nnz=125161)
2026-08-26 20:47:58,334 INFO collimator.features: DB-backed feature extraction: 304 rows, 1 workers, batch_size=1024
2026-08-26 20:48:00,347 INFO collimator.features: DB-backed feature extraction: 294 rows, 1 workers, batch_size=1024
2026-08-26 20:48:00,601 INFO azoth_calibrate_ensemble: filetypes/chm: saved route feature matrix cache out/cache/azoth-route-features/filetypes_chm-3518179578-766086dae207039b-3ebc3f87e74d039a.matrix.npz
2026-08-26 20:48:00,603 INFO azoth_calibrate_ensemble: filetypes/chm: refreshed 294 rows in 0.3s (fetch 0.0s, filter 0.0s, load 0.0s, extract 0.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=825 nnz=18370)
2026-08-26 20:48:04,983 INFO azoth_calibrate_ensemble: filetypes/npm: saved route feature matrix cache out/cache/azoth-route-features/filetypes_npm-3518179578-5bc773696462f016-e6a039993a00a617.matrix.npz
2026-08-26 20:48:05,112 INFO azoth_calibrate_ensemble: filetypes/whl: saved route feature matrix cache out/cache/azoth-route-features/filetypes_whl-3518179578-58a81668dcacecc8-783766ac645a3183.matrix.npz
2026-08-26 20:48:05,191 INFO azoth_calibrate_ensemble: filetypes/npm: refreshed 14136 rows in 74.5s (fetch 1.3s, filter 0.0s, load 0.1s, extract 72.8s, matrix 0.0s, predict 0.2s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1775 nnz=1511087)
2026-08-26 20:48:05,403 INFO azoth_calibrate_ensemble: filetypes/whl: refreshed 17165 rows in 77.6s (fetch 1.8s, filter 0.0s, load 0.1s, extract 75.4s, matrix 0.0s, predict 0.3s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=2022 nnz=1879414)
2026-08-26 20:48:11,167 INFO azoth_calibrate_ensemble: filetypes/apk_android: saved route feature matrix cache out/cache/azoth-route-features/filetypes_apk_android-3518179578-95be9dd9615062fc-330176060052b46a.matrix.npz
2026-08-26 20:48:11,212 INFO azoth_calibrate_ensemble: filetypes/apk_android: refreshed 3098 rows in 30.5s (fetch 0.1s, filter 0.0s, load 0.0s, extract 30.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1628 nnz=191957)
2026-08-26 20:48:12,121 INFO azoth_calibrate_ensemble: filetypes/dmg: saved route feature matrix cache out/cache/azoth-route-features/filetypes_dmg-3518179578-bfb8163b8719c4c6-c7684ee52e0eea29.matrix.npz
2026-08-26 20:48:12,124 INFO azoth_calibrate_ensemble: filetypes/dmg: refreshed 304 rows in 13.8s (fetch 0.0s, filter 0.0s, load 0.0s, extract 13.8s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1746 nnz=57340)
2026-08-26 20:49:09,154 INFO azoth_calibrate_ensemble: filetypes/7z: saved route feature matrix cache out/cache/azoth-route-features/filetypes_7z-3518179578-f88794d4b57dd5e7-4a94220ae4efcfba.matrix.npz
2026-08-26 20:49:09,275 INFO azoth_calibrate_ensemble: filetypes/7z: refreshed 9308 rows in 114.5s (fetch 0.5s, filter 0.0s, load 0.0s, extract 113.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.8s; features=3189 nnz=2248620)
2026-08-26 20:50:04,501 INFO azoth_calibrate_ensemble: filetypes/vsix: saved route feature matrix cache out/cache/azoth-route-features/filetypes_vsix-3518179578-99df284b9c8b9a89-5cfa93e1258b1765.matrix.npz
2026-08-26 20:50:04,562 INFO azoth_calibrate_ensemble: filetypes/vsix: refreshed 5229 rows in 148.2s (fetch 0.3s, filter 0.0s, load 0.0s, extract 147.8s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1798 nnz=936671)
2026-08-26 20:50:36,906 INFO azoth_calibrate_ensemble: filetypes/python: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python-3518179578-9edd51c08ee568a3-62f3e159a58cca6b.matrix.npz
2026-08-26 20:50:43,646 INFO azoth_calibrate_ensemble: filetypes/python: refreshed 660577 rows in 552.4s (fetch 9.8s, filter 0.1s, load 0.1s, extract 525.5s, matrix 10.0s, predict 6.2s, write 0.5s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=1920 nnz=28227755)
2026-08-26 20:53:30,530 INFO azoth_calibrate_ensemble: filetypes/tar: saved route feature matrix cache out/cache/azoth-route-features/filetypes_tar-3518179578-2e592ef4b707001b-5b3d3c4f2b96ca6f.matrix.npz
2026-08-26 20:53:31,781 INFO azoth_calibrate_ensemble: filetypes/tar: refreshed 100831 rows in 493.6s (fetch 4.7s, filter 0.0s, load 0.1s, extract 487.2s, matrix 0.0s, predict 1.2s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.2s; features=2573 nnz=10420941)
2026-08-26 20:58:30,144 INFO azoth_calibrate_ensemble: filetypes/zip: saved route feature matrix cache out/cache/azoth-route-features/filetypes_zip-3518179578-d83ecf153fc38203-cd0f385593507291.matrix.npz
2026-08-26 20:58:32,114 INFO azoth_calibrate_ensemble: filetypes/zip: refreshed 144272 rows in 863.8s (fetch 3.4s, filter 0.0s, load 0.1s, extract 858.1s, matrix 0.0s, predict 1.9s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=3173 nnz=18336864)
2026-08-26 20:59:25,916 INFO azoth_calibrate_ensemble: filetypes/elf: saved route feature matrix cache out/cache/azoth-route-features/filetypes_elf-3518179578-3bb4efe429e508c0-c683ce14f28debd9.matrix.npz
2026-08-26 20:59:37,598 INFO azoth_calibrate_ensemble: filetypes/elf: refreshed 980269 rows in 1086.8s (fetch 7.0s, filter 0.2s, load 0.1s, extract 1065.4s, matrix 1.7s, predict 11.0s, write 0.7s; feature_cache_read 0.0s, feature_cache_write 0.5s; features=2878 nnz=74999208)
2026-08-26 21:05:02,915 INFO azoth_calibrate_ensemble: filegroups/source: saved route feature matrix cache out/cache/azoth-route-features/filegroups_source-3518179578-fb791505f0b8e762-3d9c0928c74add52.matrix.npz
2026-08-26 21:05:30,709 INFO azoth_calibrate_ensemble: filegroups/source: refreshed 2827592 rows in 1441.7s (fetch 67.1s, filter 0.3s, load 0.1s, extract 1344.7s, matrix 1.3s, predict 26.0s, write 1.7s; feature_cache_read 0.0s, feature_cache_write 0.3s; features=2022 nnz=76595604)
2026-08-26 21:09:22,354 INFO azoth_calibrate_ensemble: filetypes/javascript: saved route feature matrix cache out/cache/azoth-route-features/filetypes_javascript-3518179578-6d706f202595265c-4a6d4637a1ff014f.matrix.npz
2026-08-26 21:09:40,095 INFO azoth_calibrate_ensemble: filetypes/javascript: refreshed 1754276 rows in 1690.0s (fetch 54.8s, filter 0.2s, load 0.2s, extract 1614.4s, matrix 2.1s, predict 16.6s, write 1.2s; feature_cache_read 0.0s, feature_cache_write 0.4s; features=2248 nnz=95027966)
2026-08-26 21:27:38,217 INFO azoth_calibrate_ensemble: filegroups/scripts: saved route feature matrix cache out/cache/azoth-route-features/filegroups_scripts-3518179578-5430689cc0268981-a0596984f11a2dab.matrix.npz
2026-08-26 21:28:21,210 INFO azoth_calibrate_ensemble: filegroups/scripts: refreshed 3690267 rows in 2813.2s (fetch 69.1s, filter 0.5s, load 0.2s, extract 2693.7s, matrix 5.9s, predict 40.3s, write 2.7s; feature_cache_read 0.0s, feature_cache_write 0.6s; features=2560 nnz=172118342)
make[1]: *** [Makefile:1259: azoth-calibrate] Terminated
/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/multiprocessing/resource_tracker.py:279: UserWarning: resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d ')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9811)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d194e30c2145fac5` | `1bc137e20eaad336` | `f9633e7ac7f15ed3` |
| PR AUC | 0.9811 | 0.9954 | 0.9953 |
| ROC AUC | 0.9767 | 0.9876 | 0.9882 |
| F1 | 0.8494 | 0.9722 | 0.9722 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/collimator/out/autocollie/runs/2026-08-26T23-19-09_20260826T231744-promote-d194e30c2145fac5_azoth-validate.log; tail: 2026-08-26 20:47:41,580 INFO collimator.features: DB-backed feature extraction: 2595 rows, 1 workers, batch_size=1024
2026-08-26 20:47:46,745 INFO azoth_calibrate_ensemble: filetypes/xpi: saved route feature matrix cache out/cache/azoth-route-features/filetypes_xpi-3518179578-885f21f69c776742-1be8cf3f1030d8b0.matrix.npz
2026-08-26 20:47:46,807 INFO azoth_calibrate_ensemble: filetypes/xpi: refreshed 2595 rows in 5.4s (fetch 0.2s, filter 0.0s, load 0.0s, extract 5.2s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1258 nnz=229294)
2026-08-26 20:47:48,898 INFO collimator.features: DB-backed feature extraction: 1156 rows, 1 workers, batch_size=1024
2026-08-26 20:47:49,363 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: saved route feature matrix cache out/cache/azoth-route-features/filetypes_chrome_manifest-3518179578-fe4b991638733ebf-87a79f69348e217b.matrix.npz
2026-08-26 20:47:49,380 INFO azoth_calibrate_ensemble: filetypes/chrome_manifest: refreshed 1156 rows in 0.6s (fetch 0.0s, filter 0.0s, load 0.0s, extract 0.5s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=207 nnz=51591)
2026-08-26 20:47:49,540 INFO azoth_calibrate_ensemble: filetypes/gem: saved route feature matrix cache out/cache/azoth-route-features/filetypes_gem-3518179578-8936f70590e49536-7b1d3935a0890612.matrix.npz
2026-08-26 20:47:49,599 INFO azoth_calibrate_ensemble: filetypes/gem: refreshed 4476 rows in 11.1s (fetch 0.2s, filter 0.0s, load 0.0s, extract 10.8s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1737 nnz=426280)
2026-08-26 20:47:51,456 INFO collimator.features: DB-backed feature extraction: 586 rows, 1 workers, batch_size=1024
2026-08-26 20:47:51,720 INFO azoth_calibrate_ensemble: filetypes/applescript: saved route feature matrix cache out/cache/azoth-route-features/filetypes_applescript-3518179578-aa23d75355b05444-cab89b589d12527a.matrix.npz
2026-08-26 20:47:51,726 INFO azoth_calibrate_ensemble: filetypes/applescript: refreshed 586 rows in 0.3s (fetch 0.1s, filter 0.0s, load 0.0s, extract 0.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=350 nnz=15690)
2026-08-26 20:47:51,954 INFO collimator.features: DB-backed feature extraction: 409 rows, 1 workers, batch_size=1024
2026-08-26 20:47:53,876 INFO collimator.features: DB-backed feature extraction: 353 rows, 1 workers, batch_size=1024
2026-08-26 20:47:56,151 INFO azoth_calibrate_ensemble: filetypes/python_sdist: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python_sdist-3518179578-0c62adcec708b562-d542d0d940797a9c.matrix.npz
2026-08-26 20:47:56,158 INFO azoth_calibrate_ensemble: filetypes/python_sdist: refreshed 353 rows in 2.4s (fetch 0.0s, filter 0.0s, load 0.0s, extract 2.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1316 nnz=37136)
2026-08-26 20:47:58,169 INFO azoth_calibrate_ensemble: filetypes/asar: saved route feature matrix cache out/cache/azoth-route-features/filetypes_asar-3518179578-6c8f29d4f7004d6a-b64757bdad8b61fa.matrix.npz
2026-08-26 20:47:58,176 INFO azoth_calibrate_ensemble: filetypes/asar: refreshed 409 rows in 6.3s (fetch 0.0s, filter 0.0s, load 0.0s, extract 6.2s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1482 nnz=125161)
2026-08-26 20:47:58,334 INFO collimator.features: DB-backed feature extraction: 304 rows, 1 workers, batch_size=1024
2026-08-26 20:48:00,347 INFO collimator.features: DB-backed feature extraction: 294 rows, 1 workers, batch_size=1024
2026-08-26 20:48:00,601 INFO azoth_calibrate_ensemble: filetypes/chm: saved route feature matrix cache out/cache/azoth-route-features/filetypes_chm-3518179578-766086dae207039b-3ebc3f87e74d039a.matrix.npz
2026-08-26 20:48:00,603 INFO azoth_calibrate_ensemble: filetypes/chm: refreshed 294 rows in 0.3s (fetch 0.0s, filter 0.0s, load 0.0s, extract 0.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=825 nnz=18370)
2026-08-26 20:48:04,983 INFO azoth_calibrate_ensemble: filetypes/npm: saved route feature matrix cache out/cache/azoth-route-features/filetypes_npm-3518179578-5bc773696462f016-e6a039993a00a617.matrix.npz
2026-08-26 20:48:05,112 INFO azoth_calibrate_ensemble: filetypes/whl: saved route feature matrix cache out/cache/azoth-route-features/filetypes_whl-3518179578-58a81668dcacecc8-783766ac645a3183.matrix.npz
2026-08-26 20:48:05,191 INFO azoth_calibrate_ensemble: filetypes/npm: refreshed 14136 rows in 74.5s (fetch 1.3s, filter 0.0s, load 0.1s, extract 72.8s, matrix 0.0s, predict 0.2s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1775 nnz=1511087)
2026-08-26 20:48:05,403 INFO azoth_calibrate_ensemble: filetypes/whl: refreshed 17165 rows in 77.6s (fetch 1.8s, filter 0.0s, load 0.1s, extract 75.4s, matrix 0.0s, predict 0.3s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=2022 nnz=1879414)
2026-08-26 20:48:11,167 INFO azoth_calibrate_ensemble: filetypes/apk_android: saved route feature matrix cache out/cache/azoth-route-features/filetypes_apk_android-3518179578-95be9dd9615062fc-330176060052b46a.matrix.npz
2026-08-26 20:48:11,212 INFO azoth_calibrate_ensemble: filetypes/apk_android: refreshed 3098 rows in 30.5s (fetch 0.1s, filter 0.0s, load 0.0s, extract 30.3s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1628 nnz=191957)
2026-08-26 20:48:12,121 INFO azoth_calibrate_ensemble: filetypes/dmg: saved route feature matrix cache out/cache/azoth-route-features/filetypes_dmg-3518179578-bfb8163b8719c4c6-c7684ee52e0eea29.matrix.npz
2026-08-26 20:48:12,124 INFO azoth_calibrate_ensemble: filetypes/dmg: refreshed 304 rows in 13.8s (fetch 0.0s, filter 0.0s, load 0.0s, extract 13.8s, matrix 0.0s, predict 0.0s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1746 nnz=57340)
2026-08-26 20:49:09,154 INFO azoth_calibrate_ensemble: filetypes/7z: saved route feature matrix cache out/cache/azoth-route-features/filetypes_7z-3518179578-f88794d4b57dd5e7-4a94220ae4efcfba.matrix.npz
2026-08-26 20:49:09,275 INFO azoth_calibrate_ensemble: filetypes/7z: refreshed 9308 rows in 114.5s (fetch 0.5s, filter 0.0s, load 0.0s, extract 113.0s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.8s; features=3189 nnz=2248620)
2026-08-26 20:50:04,501 INFO azoth_calibrate_ensemble: filetypes/vsix: saved route feature matrix cache out/cache/azoth-route-features/filetypes_vsix-3518179578-99df284b9c8b9a89-5cfa93e1258b1765.matrix.npz
2026-08-26 20:50:04,562 INFO azoth_calibrate_ensemble: filetypes/vsix: refreshed 5229 rows in 148.2s (fetch 0.3s, filter 0.0s, load 0.0s, extract 147.8s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=1798 nnz=936671)
2026-08-26 20:50:36,906 INFO azoth_calibrate_ensemble: filetypes/python: saved route feature matrix cache out/cache/azoth-route-features/filetypes_python-3518179578-9edd51c08ee568a3-62f3e159a58cca6b.matrix.npz
2026-08-26 20:50:43,646 INFO azoth_calibrate_ensemble: filetypes/python: refreshed 660577 rows in 552.4s (fetch 9.8s, filter 0.1s, load 0.1s, extract 525.5s, matrix 10.0s, predict 6.2s, write 0.5s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=1920 nnz=28227755)
2026-08-26 20:53:30,530 INFO azoth_calibrate_ensemble: filetypes/tar: saved route feature matrix cache out/cache/azoth-route-features/filetypes_tar-3518179578-2e592ef4b707001b-5b3d3c4f2b96ca6f.matrix.npz
2026-08-26 20:53:31,781 INFO azoth_calibrate_ensemble: filetypes/tar: refreshed 100831 rows in 493.6s (fetch 4.7s, filter 0.0s, load 0.1s, extract 487.2s, matrix 0.0s, predict 1.2s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.2s; features=2573 nnz=10420941)
2026-08-26 20:58:30,144 INFO azoth_calibrate_ensemble: filetypes/zip: saved route feature matrix cache out/cache/azoth-route-features/filetypes_zip-3518179578-d83ecf153fc38203-cd0f385593507291.matrix.npz
2026-08-26 20:58:32,114 INFO azoth_calibrate_ensemble: filetypes/zip: refreshed 144272 rows in 863.8s (fetch 3.4s, filter 0.0s, load 0.1s, extract 858.1s, matrix 0.0s, predict 1.9s, write 0.1s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=3173 nnz=18336864)
2026-08-26 20:59:25,916 INFO azoth_calibrate_ensemble: filetypes/elf: saved route feature matrix cache out/cache/azoth-route-features/filetypes_elf-3518179578-3bb4efe429e508c0-c683ce14f28debd9.matrix.npz
2026-08-26 20:59:37,598 INFO azoth_calibrate_ensemble: filetypes/elf: refreshed 980269 rows in 1086.8s (fetch 7.0s, filter 0.2s, load 0.1s, extract 1065.4s, matrix 1.7s, predict 11.0s, write 0.7s; feature_cache_read 0.0s, feature_cache_write 0.5s; features=2878 nnz=74999208)
2026-08-26 21:05:02,915 INFO azoth_calibrate_ensemble: filegroups/source: saved route feature matrix cache out/cache/azoth-route-features/filegroups_source-3518179578-fb791505f0b8e762-3d9c0928c74add52.matrix.npz
2026-08-26 21:05:30,709 INFO azoth_calibrate_ensemble: filegroups/source: refreshed 2827592 rows in 1441.7s (fetch 67.1s, filter 0.3s, load 0.1s, extract 1344.7s, matrix 1.3s, predict 26.0s, write 1.7s; feature_cache_read 0.0s, feature_cache_write 0.3s; features=2022 nnz=76595604)
2026-08-26 21:09:22,354 INFO azoth_calibrate_ensemble: filetypes/javascript: saved route feature matrix cache out/cache/azoth-route-features/filetypes_javascript-3518179578-6d706f202595265c-4a6d4637a1ff014f.matrix.npz
2026-08-26 21:09:40,095 INFO azoth_calibrate_ensemble: filetypes/javascript: refreshed 1754276 rows in 1690.0s (fetch 54.8s, filter 0.2s, load 0.2s, extract 1614.4s, matrix 2.1s, predict 16.6s, write 1.2s; feature_cache_read 0.0s, feature_cache_write 0.4s; features=2248 nnz=95027966)
2026-08-26 21:27:38,217 INFO azoth_calibrate_ensemble: filegroups/scripts: saved route feature matrix cache out/cache/azoth-route-features/filegroups_scripts-3518179578-5430689cc0268981-a0596984f11a2dab.matrix.npz
2026-08-26 21:28:21,210 INFO azoth_calibrate_ensemble: filegroups/scripts: refreshed 3690267 rows in 2813.2s (fetch 69.1s, filter 0.5s, load 0.2s, extract 2693.7s, matrix 5.9s, predict 40.3s, write 2.7s; feature_cache_read 0.0s, feature_cache_write 0.6s; features=2560 nnz=172118342)
make[1]: *** [Makefile:1259: azoth-calibrate] Terminated
/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/multiprocessing/resource_tracker.py:279: UserWarning: resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d ')
