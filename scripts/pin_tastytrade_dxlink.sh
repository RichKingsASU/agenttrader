#!/usr/bin/env bash
set -euo pipefail
VERSIONS=( "10.6.0" "10.5.0" "10.4.0" "10.3.0" "10.2.0" "10.1.0" "10.0.0" "9.9.0" "9.5.0" "9.0.0" "8.9.0" "8.6.0" )

echo "[pin] Uninstall current tastytrade (if any)..."
pip uninstall -y tastytrade || true

for V in "${VERSIONS[@]}"; do
  echo "[pin] Trying tastytrade==$V ..."
  if pip install -q "tastytrade==${V}"; then
    python - << 'PY'
import sys, inspect
try:
    from tastytrade.session import Session
    from tastytrade.dxfeed import DXLinkStreamer, Quote  # must import
    sig = str(inspect.signature(Session.__init__))
    ok = ("password" in sig or "user" in sig) and "DXLinkStreamer" in str(DXLinkStreamer)
    print("Session.__init__ =", sig)
    sys.exit(0 if ok else 2)
except Exception as e:
    print("CHECK_FAILED:", e)
    sys.exit(2)
PY
    if [[ $? -eq 0 ]]; then
      echo "[pin] SUCCESS: tastytrade==${V} provides DXLinkStreamer and user/password Session."
      exit 0
    else
      echo "[pin] Not compatible: tastytrade==${V}"
    fi
  fi
done

echo "[pin] ERROR: No compatible tastytrade version found in list."
exit 1
