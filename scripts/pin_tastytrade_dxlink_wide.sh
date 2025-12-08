#!/usr/bin/env bash
set -euo pipefail

# Exhaustive list of known published versions (descending)
VERSIONS=( 
  "10.3.0" "10.2.3" "10.2.2" "10.2.1" "10.2.0" "10.1.1" "10.1.0" "10.0.1" "10.0.0"
  "9.13" "9.12" "9.11" "9.10" "9.9" "9.8" "9.7" "9.6" "9.5" "9.4" "9.3" "9.2" "9.1" "9.0"
  "8.9.0" "8.8.0" "8.7.0" "8.6.0" "8.5" "8.3" "8.2" "8.1"
  "7.9" "7.8" "7.7" "7.6" "7.5" "7.4" "7.3" "7.2" "7.1" "7.0"
)

echo "[pin] Uninstall current tastytrade (if any)..."
pip uninstall -y tastytrade >/dev/null 2>&1 || true

for V in "${VERSIONS[@]}"; do
  echo "[pin] Trying tastytrade==${V} ..."
  if pip install -q "tastytrade==${V}"; then
    python - << 'PY'
import sys, inspect
try:
    from tastytrade.session import Session
    try:
        from tastytrade.dxfeed import DXLinkStreamer, Quote
        has_dx = True
    except Exception:
        has_dx = False
    sig = str(inspect.signature(Session.__init__))
    # crude check for user/pass style constructor
    wants_userpass = any(k in sig for k in ["user", "username", "email", "password"])
    print("Session.__init__ =", sig)
    print("Has DXLinkStreamer:", has_dx)
    sys.exit(0 if (has_dx and wants_userpass) else 2)
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
  else
    echo "[pin] pip install failed for tastytrade==${V}"
  fi
done

echo "[pin] ERROR: No compatible tastytrade version found."
exit 1
