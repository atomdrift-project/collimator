#!/usr/bin/env bash
#
# install_nightly.sh — install (or remove) the systemd --user units for the
# Azoth nightly pipeline. Invoked by `make install-nightly` / `make uninstall-nightly`.
#
# Two units, because a publish-train can run 8-34h and the autocollie sweep is
# meant to soak up whatever hours are left over (see scripts/nightly.sh):
#
#   azoth-nightly.service    the train: repin -> publish-train -> deploy -> push.
#                            Fires on azoth-nightly.timer. Stops the sweep on the
#                            way in and starts it again on the way out.
#   azoth-autocollie.service the sweep: an indefinite shuffled autocollie walk.
#                            No timer — the train owns its lifecycle. Killed as a
#                            whole cgroup when the next train preempts it.
#
# Logs land in out/nightly/ (durable) and journald:
#   journalctl --user -u azoth-nightly.service
#   journalctl --user -u azoth-autocollie.service
# Change the schedule with: NIGHTLY_ONCALENDAR='*-*-* 03:00:00' make install-nightly
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLLIMATOR_DIR="$(dirname "$SCRIPT_DIR")"
NIGHTLY="$SCRIPT_DIR/nightly.sh"

USER_NAME="${USER:-$(id -un)}"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE="azoth-nightly.service"
SWEEP="azoth-autocollie.service"
TIMER="azoth-nightly.timer"
ONCALENDAR="${NIGHTLY_ONCALENDAR:-*-*-* 23:00:00}"

if [ "${1:-}" = "--remove" ] || [ "${1:-}" = "uninstall" ]; then
  systemctl --user disable --now "$TIMER" 2>/dev/null || true
  systemctl --user stop "$SWEEP" 2>/dev/null || true
  rm -f "$UNIT_DIR/$SERVICE" "$UNIT_DIR/$SWEEP" "$UNIT_DIR/$TIMER"
  systemctl --user daemon-reload 2>/dev/null || true
  echo "removed $SERVICE, $SWEEP and $TIMER"
  exit 0
fi

test -x "$NIGHTLY" || { echo "error: $NIGHTLY is not executable (run: chmod +x $NIGHTLY)"; exit 1; }
mkdir -p "$UNIT_DIR"

cat > "$UNIT_DIR/$SERVICE" <<EOF
[Unit]
Description=Azoth nightly retrain, publish, and deploy

[Service]
Type=oneshot
WorkingDirectory=$COLLIMATOR_DIR
ExecStart=$NIGHTLY train
# Multi-hour job — do not time it out at the default 90s.
TimeoutStartSec=0
EOF

# No [Install] section and no timer: the train starts this unit when it
# finishes and stops it when it next begins. Restart=on-failure covers the
# sweep dying on a transient (a postgres-in-recovery crash cost the whole
# 2026-07-23 night); an explicit `systemctl stop` from the train suppresses
# the restart, which is exactly the preemption behaviour we want.
cat > "$UNIT_DIR/$SWEEP" <<EOF
[Unit]
Description=Azoth autocollie sweep (idle-time filler; preempted by azoth-nightly)

[Service]
Type=simple
WorkingDirectory=$COLLIMATOR_DIR
ExecStart=$NIGHTLY autocollie
# Runs until preempted — never time it out.
TimeoutStartSec=0
# SIGTERM the whole cgroup (autocollie + its python children), SIGKILL after 2m.
KillMode=control-group
TimeoutStopSec=120
Restart=on-failure
RestartSec=300
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
echo "installed: $UNIT_DIR/$SWEEP  (no timer — started/stopped by the train)"
echo "installed: $UNIT_DIR/$TIMER  (OnCalendar=$ONCALENDAR)"
echo
systemctl --user list-timers "$TIMER" --no-pager 2>/dev/null || true
echo
echo "run train now:  systemctl --user start $SERVICE   (or: make nightly)"
echo "run sweep now:  systemctl --user start $SWEEP     (or: make nightly-sweep)"
echo "watch logs:     make nightly-logs  /  make nightly-sweep-logs"
echo "last run:       make nightly-status"
