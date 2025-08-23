#!/usr/bin/env bash
# XTF - Xtended Tactical Framework
set -Euo pipefail
WTF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
source "${WTF_ROOT}/wtf_lib.sh"

RESET="\033[0m"
BOLD="\033[1m"
GREEN="\033[38;5;82m"
YELLOW="\033[38;5;226m"
CYAN="\033[38;5;51m"
MAGENTA="\033[38;5;165m"
RED="\033[0;31m"

show_menu() {
  clear
  echo
  purple_gradient "========================================="
  echo -e "      ${BOLD}${MAGENTA}  (⌐■_■)   W T F   (■_■¬)${RESET}"
  purple_gradient "========================================="
  echo -e "${BOLD}${MAGENTA}    Wrapper Tactical Framework${RESET}"
  purple_gradient "========================================="
  echo -e "$(purple_gradient "           by Meezok")"
  echo

  echo -e "${BOLD}${YELLOW}Main Menu:${RESET}"
  echo -e "  ${YELLOW}[1]${RESET} ${GREEN}RustScan Wrapper${RESET}   ${CYAN}→ Rapid port scanning${RESET}"
  echo -e "  ${YELLOW}[2]${RESET} ${GREEN}MPSA Search Engine${RESET}  ${CYAN}→ File/Search toolkit${RESET}"
  echo -e "  ${YELLOW}[3]${RESET} ${GREEN}Kali Lightweight Env${RESET}${CYAN}→ Containerized Kali${RESET}"
  echo -e "  ${YELLOW}[4]${RESET} ${GREEN}Show Logs${RESET}          ${CYAN}→ View operation logs${RESET}"
  echo -e "  ${YELLOW}[5]${RESET} ${GREEN}Help/Documentation${RESET} ${CYAN}→ Usage instructions${RESET}"
  echo -e "  ${YELLOW}[0]${RESET} ${GREEN}Exit${RESET}"
  purple_gradient "========================================="
}

run_rustscan() { bash "${WTF_ROOT}/rustscan_wrapper.sh"; }
run_mpsa() { bash "${WTF_ROOT}/mpsa_manager.sh"; }
run_kali() { bash "${WTF_ROOT}/kali_manager.sh"; }

show_logs() {
  echo -e "\n${YELLOW}Available logs:${RESET}"
  ls -lh "${LOG_DIR}"/*.log | awk '{print $9}'
  echo -e "\n${GREEN}View which log? (full path):${RESET} "
  read logfile
  [[ -f "$logfile" ]] && less -R "$logfile" || echo "Invalid file"
}

show_help() {
  clear
  echo -e "${YELLOW}==== WTF Framework Usage ====${RESET}"
  cat <<'HELP'
1. RustScan:
   - User Friendly Rustscan (Faster Nmap)
   - Deploys installation of rustscan using Docker
   - Results saved in logs/rustscan_*.log
   - Managed pentest environment

2. MPSA:
   - User Friendly Python-based File search toolkit
   - Free's you from Writing complex Find and Grep commands.
   - Output is Well Organized more Detailed info
   - Supports search ny Wildcards.

3. Kali Light:
   - User Friendly Setup for containerized Kali
   - Test tools and scripts Safely.
   - Installed with all main Packages needed
   - Feel free to Customize the D

Logs Location:
   - All operations logged to: ./logs/
   - Rustscan output stored here.
HELP
  read -rp "Press Enter to continue..."
}

main() {
  mkdir -p "${LOG_DIR}"
  while true; do
    show_menu
    echo -e "${BOLD}${GREEN}\nSelect option [0-5]:${RESET} "
    read -r choice
    case "$choice" in
      1) run_rustscan ;;
      2) run_mpsa ;;
      3) run_kali ;;
      4) show_logs ;;
      5) show_help ;;
      0) echo -e "${CYAN}Exiting...${RESET}"; break ;;
      *) echo -e "${RED}Invalid option!${RESET}"; sleep 1 ;;
    esac
  done
}

main "$@"