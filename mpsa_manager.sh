#!/bin/bash
# MPSA Manager (host-native version)

SCRIPT_DIR="$(dirname "$(realpath "$0")")/mpsa"

python3 "$SCRIPT_DIR/mpsa.py" "$@"
