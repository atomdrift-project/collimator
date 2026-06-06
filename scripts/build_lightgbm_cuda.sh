#!/usr/bin/env bash
# Build & install LightGBM with the CUDA tree learner (device_type=cuda) into
# the project venv. The PyPI wheel is CPU/OpenCL only, so the azoth learner
# silently runs on CPU even on a CUDA host. Two host-specific fixes are needed
# and baked in here:
#
#   1. nvcc's host compiler. The system gcc (16.x) is too new for CUDA 13.2's
#      nvcc (it can't parse gcc-16 libstdc++ headers: char8_t, `requires`).
#      We pin the host compiler to gcc-15 via CUDAHOSTCXX / CMAKE_CUDA_HOST_COMPILER.
#   2. Target architectures. LightGBM 4.6's CMakeLists hardcodes CUDA_ARCHS
#      starting at sm_60, which CUDA 13.2 has dropped — the build aborts with
#      "Unsupported gpu architecture 'compute_60'". We patch it to target only
#      this host's GPU (sm_120 / Blackwell).
#
# Re-run after any `pip install lightgbm` (a plain reinstall reverts to the
# CPU wheel). Verify with: python -c "from collimator.model import
# detect_lightgbm_cuda; print(detect_lightgbm_cuda())"  -> True
set -euo pipefail

VERSION="${LIGHTGBM_VERSION:-4.6.0}"
CUDA_HOME="${CUDA_HOME:-/opt/cuda}"
HOST_CXX="${CUDAHOSTCXX:-/usr/bin/g++-15}"
ARCH="${LIGHTGBM_CUDA_ARCH:-120}"          # Blackwell RTX PRO 6000 = sm_120
VENV="${VENV:-$(dirname "$0")/../.venv}"
WORK="$(mktemp -d)"

[ -x "$CUDA_HOME/bin/nvcc" ] || { echo "nvcc not found at $CUDA_HOME/bin/nvcc"; exit 1; }
[ -x "$HOST_CXX" ] || { echo "host compiler $HOST_CXX not found (need an nvcc-compatible gcc)"; exit 1; }

echo ">> downloading LightGBM $VERSION source"
"$VENV/bin/pip" download --no-deps --no-binary lightgbm "lightgbm==$VERSION" -d "$WORK"
tar xzf "$WORK/lightgbm-$VERSION.tar.gz" -C "$WORK"
SRC="$WORK/lightgbm-$VERSION"

echo ">> patching CUDA_ARCHS -> sm_$ARCH (CUDA 13.x dropped the old archs LightGBM hardcodes)"
python - "$SRC/CMakeLists.txt" "$ARCH" <<'PYEOF'
import re, sys
path, arch = sys.argv[1], sys.argv[2]
src = open(path).read()
# Replace the whole "set(CUDA_ARCHS ...) ... message(STATUS ...)" block.
new = f'    set(CUDA_ARCHS "{arch}-real" "{arch}-virtual")\n    message(STATUS "CUDA_ARCHITECTURES (patched): ${{CUDA_ARCHS}}")\n'
src2 = re.sub(r'    set\(CUDA_ARCHS "60".*?message\(STATUS "CUDA_ARCHITECTURES: \$\{CUDA_ARCHS\}"\)\n',
              new, src, count=1, flags=re.DOTALL)
assert src2 != src, "CUDA_ARCHS block not found — LightGBM CMakeLists layout changed"
open(path, "w").write(src2)
print("   patched", path)
PYEOF

echo ">> building (gcc-15 host compiler, USE_CUDA=ON)"
export PATH="$CUDA_HOME/bin:$PATH" CUDA_HOME CUDA_PATH="$CUDA_HOME" CUDACXX="$CUDA_HOME/bin/nvcc"
export CC=/usr/bin/gcc-15 CXX="$HOST_CXX" CUDAHOSTCXX="$HOST_CXX"
"$VENV/bin/pip" install --no-deps --force-reinstall \
  --config-settings=cmake.define.USE_CUDA=ON \
  --config-settings=cmake.define.CMAKE_CUDA_HOST_COMPILER="$HOST_CXX" \
  "$SRC"

echo ">> verifying"
"$VENV/bin/python" -c "from collimator.model import detect_lightgbm_cuda; assert detect_lightgbm_cuda(), 'CUDA not active'; print('OK: LightGBM CUDA active')"
rm -rf "$WORK"
