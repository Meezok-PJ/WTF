#!/usr/bin/env bash
# WTF shared lib: logging + common helpers (Bash & Zsh friendly)
set -Euo pipefail

WTF_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%x}}")" && pwd)"
LOG_DIR="${WTF_ROOT}/logs"
mkdir -p "${LOG_DIR}"

log_json() {

  local tool="$1"; shift || true
  local status="$1"; shift || true
  local msg="${*:-}"
  local ts="$(date -Iseconds)"
  local line
  line="$(jq -c --null-input --arg ts "$ts" --arg tool "$tool" --arg status "$status" --arg msg "$msg"     '{"ts":$ts,"tool":$tool,"status":$status,"msg":$msg}' 2>/dev/null || echo "{\"ts\":\"$ts\",\"tool\":\"$tool\",\"status\":\"$status\",\"msg\":\"$msg\"}")"
  echo "$line" | tee -a "${LOG_DIR}/wtf.log" > /dev/null
}

log_pipe_to() {

  local tool="$1"
  tee -a "${LOG_DIR}/${tool}.log"
}

require_cmd() {
  local name="$1"
  if ! command -v "$name" >/dev/null 2>&1; then
    echo "[!] Missing required command: $name" >&2
    return 1
  fi
}

auto_pull_image() {
  local image="$1"
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    echo "[*] Pulling image: $image" >&2
    docker pull "$image"
  fi
}

cleanup_on_exit() {
  local tool="$1"
  local start_ts="$2"
  local status="success"
  local msg="completed"
  trap 'status="failure"; msg="aborted via INT/TERM"; log_json "$tool" "$status" "$msg"; exit 1' INT TERM
  trap 'rc=$?; if [ $rc -ne 0 ]; then status="failure"; msg="exit code $rc"; fi; log_json "$tool" "$status" "$msg"' EXIT
}

purple_gradient() {
  local text="$1"
  local colors=( "\033[38;5;93m" "\033[38;5;129m" "\033[38;5;135m" "\033[38;5;141m" "\033[38;5;177m" "\033[38;5;183m" )
  local out=""
  local i=0
  local len=${#text}
  while [ $i -lt $len ]; do
    local ch="${text:$i:1}"
    if [[ "$ch" =~ [[:space:]] ]]; then
      out+="$ch"
    else
      local idx=$(( i % ${#colors[@]} ))
      out+="${colors[$idx]}${ch}\033[0m"
    fi
    i=$(( i + 1 ))
  done
  printf "%b" "$out"
}
