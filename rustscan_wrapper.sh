#!/usr/bin/env bash
# RustScan Wrapper (Docker-alias integration) — logs to logs/rustscan_<target>_<timestamp>.log
set -Euo pipefail
WTF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
source "${WTF_ROOT}/wtf_lib.sh" 2>/dev/null || true

TOOL="rustscan"
RUSTSCAN_DEFAULT="rustscan/rustscan:alpine"
RUSTSCAN_LATEST="rustscan/rustscan:latest"
LOCAL_TAG="rustscan-local:latest"
LOG_DIR="${WTF_ROOT}/logs"

mkdir -p "$LOG_DIR"

: "${RESET:=$'\033[0m'}"
: "${RED:=$'\033[31m'}"
: "${GREEN:=$'\033[32m'}"
: "${YELLOW:=$'\033[33m'}"
: "${CYAN:=$'\033[36m'}"
: "${MAGENTA:=$'\033[35m'}"

purple_gradient() {
  local text="$1"
  echo -e "${MAGENTA}${text}${RESET}"
}

show_menu() {
  clear
  purple_gradient "================================================"
  echo -e "${CYAN}"
  cat <<'CROSSHAIR'
   \ | /
  -- o --
   / | \
CROSSHAIR
  echo -e "${RESET}"
  purple_gradient "=============== RustScan (WTF) ==============="
  echo
  echo -e "${YELLOW}[1]${RESET} ${GREEN}Run RustScan scan${RESET}"
  echo -e "${YELLOW}[2]${RESET} ${GREEN}Build local RustScan image${RESET}"
  echo -e "${YELLOW}[3]${RESET} ${GREEN}Setup alias (Bash/Zsh)${RESET}"
  echo -e "${YELLOW}[4]${RESET} ${GREEN}Help & Examples${RESET}"
  echo -e "${YELLOW}[0]${RESET} ${RED}Return to main menu${RESET}"
  purple_gradient "================================================"
}

ensure_image() {
  local image="$1"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "[*] Docker image '$image' not found — pulling..."
    docker pull "$image" || {
      echo "[!] ERROR: Failed to pull RustScan image $image"
      return 1
    }
  fi
}

build_local() {
  cat > "${WTF_ROOT}/Dockerfile.rustscan" <<'EOF'
FROM rustscan/rustscan:alpine
# you can add extras here if needed
EOF
  docker build -t "${LOCAL_TAG}" -f "${WTF_ROOT}/Dockerfile.rustscan" "${WTF_ROOT}"
}

setup_alias() {
  local alias_line="alias rustscan='docker run --rm -it --ulimit nofile=5000:5000 --network host ${RUSTSCAN_DEFAULT}'"
  for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q "alias rustscan=" "$rc"; then
      printf '\n# WTF: RustScan Docker alias\n%s\n' "$alias_line" >> "$rc"
    elif [ ! -f "$rc" ]; then
      printf '#!/usr/bin/env bash\n# created by WTF\n%s\n' "$alias_line" > "$rc"
    fi
  done
  echo "[*] Alias 'rustscan' added. Run 'source ~/.bashrc' or 'source ~/.zshrc'."
}

run_scan() {
  require_cmd docker || exit 1

  read -rp "Target(s) (e.g. 192.168.1.1,10.0.0.0/24,scanme.nmap.org): " targets
  read -rp "Extra RustScan flags (enter for none): " rs_flags
  echo "Nmap passthrough: everything after -- will be sent to nmap."
  read -rp "Nmap flags after -- (e.g. -sC -sV): " nmap_flags

  local image="${RUSTSCAN_DEFAULT}"
  read -rp "Use latest variant instead of alpine? (y/N): " use_latest
  if [[ "${use_latest,,}" == "y" ]]; then image="${RUSTSCAN_LATEST}"; fi

  ensure_image "$image" || return 1

  local sanitized_target
  sanitized_target=$(echo "$targets" | tr -d ' ./:' | cut -c -40)
  local timestamp
  timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
  local log_file="${LOG_DIR}/rustscan_${sanitized_target}_${timestamp}.log"

  echo "[*] Running RustScan ($image) on: $targets" | tee -a "$log_file"

  docker run --rm -i \
    --ulimit nofile=5000:5000 \
    --network host \
    "$image" -a "$targets" $rs_flags -- $nmap_flags 2>&1 | tee -a "$log_file"

  echo -e "\n${GREEN}[+] Scan finished. Results stored in:${RESET}"
  echo "    $log_file"
}

show_help() {
  cat <<'HELP'
RustScan Help & Examples
------------------------
Basic scan:
  rustscan 127.0.0.1

Scan with Nmap integration:
  rustscan 192.168.1.10 -- -A

Scan subnet:
  rustscan --addresses 192.168.1.0/24

Faster scan (timeout + batch size):
  rustscan 10.10.10.5 -t 500 -b 1500

Top 100 ports:
  rustscan 10.10.10.5 -- -F
HELP
  read -rp "Press enter to continue..."
}

main() {
  while true; do
    show_menu
    read -rp "Select: " ch
    case "${ch:-}" in
      1) run_scan ;;
      2) build_local ;;
      3) setup_alias ;;
      4) show_help ;;
      0) break ;;
      *) echo "Invalid"; sleep 1 ;;
    esac
  done
}

main "$@"

