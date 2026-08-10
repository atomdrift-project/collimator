# Promote REJECTED — `2379fa869c87b2dc` on `filetypes/vbs`

Generated 2026-08-04T23:04:39Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-04T22-20-09_20260804T221956-promote-2379fa869c87b2dc_azoth-validate.log; tail: 2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/java already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/javascript already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/macho already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/nupkg already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/ole_doc already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/pe already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/perl already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/php already has model.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_42.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_43.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_44.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/python already has model.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rpm already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_42.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_43.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_44.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/shell already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/whl already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/zip already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO found 3 .txt files to convert
2026-08-04 19:04:30,130 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_42.onnx
2026-08-04 19:04:33,034 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:34,114 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=1.50e-07 on 200 rows, 4436 ms)
2026-08-04 19:04:34,243 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_43.onnx
2026-08-04 19:04:34,314 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:35,257 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=1.31e-07 on 200 rows, 1143 ms)
2026-08-04 19:04:35,408 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_44.onnx
2026-08-04 19:04:35,504 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:36,521 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=1.21e-07 on 200 rows, 1264 ms)

converted 3/3 files (0 intentionally skipped, 0 specialist route(s) dropped, 0 failed)
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc
Traceback (most recent call last):
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 194, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 188, in main
    stage_runtime_bundle(args.src, args.dst)
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 175, in stage_runtime_bundle
    if not _copy_route(route_src, route_dst):
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 121, in _copy_route
    _stage_feature_spec(src / name, dst / name)
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 90, in _stage_feature_spec
    json.dump(spec, f, indent=2)
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/json/__init__.py", line 180, in dump
    fp.write(chunk)
OSError: [Errno 28] No space left on device
make[1]: *** [Makefile:1375: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9980)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2379fa869c87b2dc` | `1d9354f1f8205ac9` | `2d950a88bd999c0d` |
| PR AUC | 0.9980 | 0.9987 | 0.9984 |
| ROC AUC | 0.9924 | 0.9955 | 0.9942 |
| F1 | 0.9723 | 0.9845 | 0.9823 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-08-04T22-20-09_20260804T221956-promote-2379fa869c87b2dc_azoth-validate.log; tail: 2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/java already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/javascript already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/macho already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/nupkg already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/ole_doc already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/pe already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/perl already has model.onnx; skipping
2026-08-04 19:04:29,675 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/php already has model.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_42.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_43.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/powershell already has seed_44.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/python already has model.onnx; skipping
2026-08-04 19:04:29,676 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rpm already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_42.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_43.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/rtf already has seed_44.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/shell already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/whl already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/zip already has model.onnx; skipping
2026-08-04 19:04:29,677 INFO found 3 .txt files to convert
2026-08-04 19:04:30,130 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_42.onnx
2026-08-04 19:04:33,034 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:34,114 INFO filetypes/vbs/models/seed_42.txt -> seed_42.onnx OK (delta=1.50e-07 on 200 rows, 4436 ms)
2026-08-04 19:04:34,243 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_43.onnx
2026-08-04 19:04:34,314 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:35,257 INFO filetypes/vbs/models/seed_43.txt -> seed_43.onnx OK (delta=1.31e-07 on 200 rows, 1143 ms)
2026-08-04 19:04:35,408 INFO exported LightGBM ONNX to /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc/filetypes/vbs/models/seed_44.onnx
2026-08-04 19:04:35,504 INFO DB-backed feature extraction: 200 rows, 4 workers, batch_size=1024
2026-08-04 19:04:36,521 INFO filetypes/vbs/models/seed_44.txt -> seed_44.onnx OK (delta=1.21e-07 on 200 rows, 1264 ms)

converted 3/3 files (0 intentionally skipped, 0 specialist route(s) dropped, 0 failed)
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-2379fa869c87b2dc
Traceback (most recent call last):
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 194, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 188, in main
    stage_runtime_bundle(args.src, args.dst)
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 175, in stage_runtime_bundle
    if not _copy_route(route_src, route_dst):
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 121, in _copy_route
    _stage_feature_spec(src / name, dst / name)
  File "/home/t/collimator/scripts/stage_azoth_runtime_bundle.py", line 90, in _stage_feature_spec
    json.dump(spec, f, indent=2)
  File "/home/t/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/lib/python3.12/json/__init__.py", line 180, in dump
    fp.write(chunk)
OSError: [Errno 28] No space left on device
make[1]: *** [Makefile:1375: azoth-validate] Error 1
make[1]: Leaving directory '/home/t/collimator')
