#!/usr/bin/env bash
# Kali Lightweight Env (Docker) — logs to logs/kali.log and logs/wtf.log
set -Euo pipefail
WTF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
source "${WTF_ROOT}/wtf_lib.sh"
TOOL="kali"

banner() {
  echo
  purple_gradient "========= Kali Lightweight Env (WTF) ========="
  echo
  cat <<'MENU'
 [1] Build & start Kali (compose)
 [2] Stop Kali
 [3] Access shell
 [4] Uninstall everything
 [0] Return to main menu
-----------------------------------
MENU
}

do_start() {
  cleanup_on_exit "$TOOL" "$(date -Iseconds)"
  ( cd "${WTF_ROOT}/kali" && bash ./manage.sh start ) 2>&1 | log_pipe_to "$TOOL"
}

do_stop() {
  cleanup_on_exit "$TOOL" "$(date -Iseconds)"
  ( cd "${WTF_ROOT}/kali" && bash ./manage.sh stop ) 2>&1 | log_pipe_to "$TOOL"
}

do_access() {
  ( cd "${WTF_ROOT}/kali" && bash ./manage.sh access ) 2>&1 | log_pipe_to "$TOOL"
}

do_uninstall() {
  cleanup_on_exit "$TOOL" "$(date -Iseconds)"
  ( cd "${WTF_ROOT}/kali" && bash ./manage.sh uninstall ) 2>&1 | log_pipe_to "$TOOL"
}

main() {
  while true; do
    banner
    read -rp "Select: " ch
    case "${ch:-}" in
      1) do_start ;;
      2) do_stop ;;
      3) do_access ;;
      4) do_uninstall ;;
      0) break ;;
      *) echo "Invalid"; sleep 1 ;;
    esac
  done
}
main "$@"
