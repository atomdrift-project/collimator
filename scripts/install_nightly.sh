#!/usr/bin/env bash
#
# install_nightly.sh — install (or remove) the systemd --user timer that runs the
# Azoth nightly pipeline. Invoked by `make install-nightly` / `make uninstall-nightly`.
#
# Logs land in journald:   journalctl --user -u azoth-nightly.service
# Change the schedule with: NIGHTLY_ONCALENDAR='*-*-* 03:00:00' make install-nightly
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLLIMATOR_DIR="$(dirname "$SCRIPT_DIR")"
NIGHTLY="$SCRIPT_DIR/nightly.sh"

USER_NAME="${USER:-$(id -un)}"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE="azoth-nightly.service"
TIMER="azoth-nightly.timer"
ONCALENDAR="${NIGHTLY_ONCALENDAR:-*-*-* 23:00:00}"

if [ "${1:-}" = "--remove" ] || [ "${1:-}" = "uninstall" ]; then
  systemctl --user disable --now "$TIMER" 2>/dev/null || true
  rm -f "$UNIT_DIR/$SERVICE" "$UNIT_DIR/$TIMER"
  systemctl --user daemon-reload 2>/dev/null || true
  echo "removed $SERVICE and $TIMER"
  exit 0
fi

test -x "$NIGHTLY" || { echo "error: $NIGHTLY is not executable (run: chmod +x $NIGHTLY)"; exit 1; }
mkdir -p "$UNIT_DIR"

cat > "$UNIT_DIR/$SERVICE" <<EOF
[Unit]
Description=Azoth nightly retrain, publish, and autocollie sweep

[Service]
Type=oneshot
WorkingDirectory=$COLLIMATOR_DIR
ExecStart=$NIGHTLY
# Multi-hour job — do not time it out at the default 90s.
TimeoutStartSec=0
EOF

cat > "$UNIT_DIR/$TIMER" <<EOF
[Unit]
Description=Run the Azoth nightly pipeline daily

[Timer]
OnCalendar=$ONCALENDAR
Persistent=true
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now "$TIMER"

# The user manager must keep running when you're logged out, or the timer never
# fires on a headless box. Enable lingering (best-effort; may need sudo).
if ! loginctl show-user "$USER_NAME" 2>/dev/null | grep -q '^Linger=yes'; then
  if loginctl enable-linger "$USER_NAME" 2>/dev/null; then
    echo "enabled linger for $USER_NAME (timer fires even when logged out)"
  else
    echo "NOTE: could not enable linger automatically. Run this once so the timer"
    echo "      fires when you are not logged in:"
    echo "        sudo loginctl enable-linger $USER_NAME"
  fi
fi

echo
echo "installed: $UNIT_DIR/$SERVICE"
echo "installed: $UNIT_DIR/$TIMER  (OnCalendar=$ONCALENDAR)"
echo
systemctl --user list-timers "$TIMER" --no-pager 2>/dev/null || true
echo
echo "run now:     systemctl --user start $SERVICE     (or: make nightly)"
echo "watch logs:  journalctl --user -u $SERVICE -f"
echo "last run:    make nightly-status"
