#!/usr/bin/env bash
set -euo pipefail

KALI_SANDBOX_DIR=""

SANDBOX_DIR=""

# --- Colors ---
RED="\e[31m"
GREEN="\e[32m"
BLUE="\e[34m"
YELLOW="\e[33m"
RESET="\e[0m"

DOCKER_COMPOSE_CMD=""
CONTAINER_NAME="kali_container"
SCRIPT_PATH=$(readlink -f "$0")




watermark() {
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${GREEN}      Powered by: Meezok's Sandbox Tool${RESET}"
    echo -e "${BLUE}========================================${RESET}"
}


detect_docker_compose() {
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 2>/dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    elif command -v docker-compose >/dev/null 2>&1; then
        DOCKER_COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}Error:${RESET} No docker-compose found. Install Docker Engine + Compose plugin or docker-compose."
        exit 1
    fi
}


check_docker() {
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}Docker is required. Install Docker and try again.${RESET}"
    fi
    detect_docker_compose
}


check_privileges() {

    if ! groups | grep -q "docker" && [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Error:${RESET} You must be in the 'docker' group or run this script with sudo."
        echo -e "To add yourself to the docker group, run: ${YELLOW}sudo usermod -aG docker \$USER${RESET}"
        echo -e "You will need to log out and log back in for the changes to take effect."
        echo -e "Alternatively, you can run this script with: ${YELLOW}sudo $0 $@${RESET}"
        exit 1
    fi
}


prompt_for_paths() {
    echo -e "${YELLOW}* Project files not found. Let's set up the directories.${RESET}"
    while true; do
        read -rp "Do you want to use the default path: $HOME/kali_sandbox (y/n)? " choice
        case "$choice" in
            y|Y)
                KALI_SANDBOX_DIR="$HOME/kali_sandbox"
                SANDBOX_DIR="$HOME/sandbox"
                break
                ;;
            n|N)
                read -rp "Enter the full path for the Kali Docker project: " custom_dir
                if [ -z "$custom_dir" ]; then
                    echo -e "${RED}Error:${RESET} Path cannot be empty."
                    continue
                fi
                KALI_SANDBOX_DIR="$custom_dir"
                SANDBOX_DIR="${KALI_SANDBOX_DIR}/sandbox_data" # Create a subdir for clarity
                # Basic validation: check if parent directory exists and is writable
                PARENT_DIR=$(dirname "$KALI_SANDBOX_DIR")
                if [ ! -d "$PARENT_DIR" ] || [ ! -w "$PARENT_DIR" ]; then
                    echo -e "${RED}Error:${RESET} The parent directory '$PARENT_DIR' does not exist or is not writable."
                    continue
                fi
                break
                ;;
            *)
                echo "Invalid input. Please enter 'y' or 'n'."
                ;;
        esac
    done
}



create_project_files() {
    echo -e "${GREEN}* Creating project files in ${KALI_SANDBOX_DIR}...${RESET}"
    mkdir -p "$SANDBOX_DIR"
    mkdir -p "$KALI_SANDBOX_DIR"
    cd "$KALI_SANDBOX_DIR" || exit 1

    cat > Dockerfile <<EOF
FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    net-tools \
    iproute2 \
    iputils-ping \
    curl \
    wget \
    nmap \
    nano \
    dnsutils \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    gcc \
    make \
    unzip \
    sudo \
    vim \
    ruby \
    perl && apt clean

# Install Go (adjust version if needed)
RUN wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz -O /tmp/go.tar.gz \
    && tar -C /usr/local -xzf /tmp/go.tar.gz \
    && rm /tmp/go.tar.gz \
    && mkdir -p /root/go/bin \
    && echo 'export PATH=$PATH:/usr/local/go/bin:/root/go/bin' >> /root/.bashrc

# Default shell
CMD ["/bin/bash"]
EOF

    cat > docker-compose.yml <<EOF
services:
  kali:
    build: .
    container_name: ${CONTAINER_NAME:-kali_container}
    volumes:
      - "${SANDBOX_DIR:-./sandbox}:/mnt"
    tty: true
    stdin_open: true
    cap_add:
      - NET_ADMIN
      - NET_RAW
    security_opt:
      - seccomp=unconfined
    # privileged: true   # Uncomment for full privilege
    networks:
      kali_net:
        ipv4_address: 169.16.138.3

networks:
  kali_net:
    driver: bridge
    ipam:
      config:
        - subnet: 169.16.138.0/24
EOF


    cat > README.md <<EOF
# Kali Docker Sandbox — Break Code, Not Your System

## Overview
An isolated Kali Linux environment for safe script testing, debugging, and experimentation without risking your host system's dependencies.

## Project location
- Project dir: ${KALI_SANDBOX_DIR}
- Persistent data: ${SANDBOX_DIR} (mounted to /mnt inside container)

## Quick start (from the project directory)
\`\`\`bash
cd "${KALI_SANDBOX_DIR}"
# start
${DOCKER_COMPOSE_CMD} up -d
# stop
${DOCKER_COMPOSE_CMD} down
# view logs
${DOCKER_COMPOSE_CMD} logs -f
# access container
sudo docker exec -it ${CONTAINER_NAME} bash
\`\`\`

## Use the included management script
A copy of this management script has been placed in your project directory at:
\`\`\`bash
${KALI_SANDBOX_DIR}/manage.sh
\`\`\`
You can use it from anywhere. You will need to either be in the docker group or use \`sudo\`.
\`\`\`bash
# with sudo
sudo bash "${KALI_SANDBOX_DIR}/manage.sh" start
# as a user in the docker group
bash "${KALI_SANDBOX_DIR}/manage.sh" start
\`\`\`

## Why use this tool
- Host-safe: Avoid breaking host dependencies.
- Persistent storage: Files survive container restarts (/mnt).
- Custom network: Test networking scenarios in isolation.
- Quick to set up and remove for iterative script testing.

**Author:** Meezok
EOF
}


copy_self_to_project_dir() {
    echo -e "${YELLOW}* Copying management script to ${KALI_SANDBOX_DIR}/manage.sh...${RESET}"
    cp "$SCRIPT_PATH" "${KALI_SANDBOX_DIR}/manage.sh"
    chmod +x "${KALI_SANDBOX_DIR}/manage.sh"
}


start() {

    if [[ "$EUID" -eq 0 ]] && [[ -n "${SUDO_USER}" ]]; then
        export HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    fi

    if [ -z "$KALI_SANDBOX_DIR" ]; then
        KALI_SANDBOX_DIR="$HOME/kali_sandbox"
        SANDBOX_DIR="$HOME/sandbox"
    fi

    check_docker

    if [ ! -d "$KALI_SANDBOX_DIR" ]; then
        prompt_for_paths
    fi


    if [ ! -f "$KALI_SANDBOX_DIR/docker-compose.yml" ]; then
        echo -e "${YELLOW}* Project files not found. Creating them now...${RESET}"
        create_project_files
        copy_self_to_project_dir
    fi
    
    echo -e "${GREEN}* Starting Kali sandbox...${RESET}"
    cd "$KALI_SANDBOX_DIR" || exit 1
    ${DOCKER_COMPOSE_CMD} up -d --build
    echo -e "${GREEN}* Kali sandbox is now running.${RESET}"
    echo -e "${YELLOW}Use 'bash ${KALI_SANDBOX_DIR}/manage.sh access' to enter the container.${RESET}"
}


stop() {

    if [[ "$EUID" -eq 0 ]] && [[ -n "${SUDO_USER}" ]]; then
        export HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    fi

    if [ -z "$KALI_SANDBOX_DIR" ]; then
        KALI_SANDBOX_DIR="$HOME/kali_sandbox"
        SANDBOX_DIR="$HOME/sandbox"
    fi
    
    check_docker

    if [ ! -f "$KALI_SANDBOX_DIR/docker-compose.yml" ]; then
        echo -e "${YELLOW}* Project not found at '${KALI_SANDBOX_DIR}'. Nothing to stop.${RESET}"
        exit 0
    fi
    
    echo -e "${GREEN}* Stopping Kali sandbox...${RESET}"
    cd "$KALI_SANDBOX_DIR" || exit 1
    ${DOCKER_COMPOSE_CMD} down
    echo -e "${GREEN}* Kali sandbox stopped.${RESET}"
}

access() {

    if [[ "$EUID" -eq 0 ]] && [[ -n "${SUDO_USER}" ]]; then
        export HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    fi

    if [ -z "$KALI_SANDBOX_DIR" ]; then
        KALI_SANDBOX_DIR="$HOME/kali_sandbox"
        SANDBOX_DIR="$HOME/sandbox"
    fi

    echo -e "${GREEN}* Accessing Kali container...${RESET}"
    sudo docker exec -it ${CONTAINER_NAME} bash
}

uninstall() {

    if [[ "$EUID" -eq 0 ]] && [[ -n "${SUDO_USER}" ]]; then
        export HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
    fi

    if [ -z "$KALI_SANDBOX_DIR" ]; then
        KALI_SANDBOX_DIR="$HOME/kali_sandbox"
        SANDBOX_DIR="$HOME/sandbox"
    fi

    check_docker

    if [ ! -d "$KALI_SANDBOX_DIR" ]; then
        echo -e "${YELLOW}* Project directory not found. Nothing to uninstall.${RESET}"
        exit 0
    fi

    echo -e "${RED}* Stopping and removing Kali sandbox containers and network...${RESET}"
    cd "$KALI_SANDBOX_DIR" || exit 1
    ${DOCKER_COMPOSE_CMD} down -v
    
    echo -e "${RED}* Removing project directory: ${KALI_SANDBOX_DIR}...${RESET}"
    rm -rf "$KALI_SANDBOX_DIR"
    echo -e "${RED}* Removing persistent data directory: ${SANDBOX_DIR}...${RESET}"
    rm -rf "$SANDBOX_DIR"

    echo -e "${GREEN}* Uninstallation complete.${RESET}"
}

help() {
    watermark
    echo -e "${YELLOW}Usage: bash $0 [command]${RESET}"
    echo
    echo -e "${BLUE}Commands:${RESET}"
    echo -e "  ${GREEN}start${RESET}     - Builds and starts the Kali sandbox container."
    echo -e "  ${GREEN}stop${RESET}      - Stops and removes the sandbox container and network."
    echo -e "  ${GREEN}access${RESET}    - Enters the running container's bash shell."
    echo -e "  ${GREEN}uninstall${RESET} - Removes all project files, containers, and persistent data."
    echo -e "  ${GREEN}help${RESET}      - Displays this help message."
    echo
    echo -e "${BLUE}Configuration:${RESET}"
    echo -e "  You can override the default directories by setting these environment variables:"
    echo -e "  ${YELLOW}KALI_SANDBOX_DIR=${RESET}  (default: ${KALI_SANDBOX_DIR})"
    echo -e "  ${YELLOW}KALI_SANDBOX_DATA_DIR=${RESET} (default: ${SANDBOX_DIR})"
    echo
    echo -e "${BLUE}Additional Commands:${RESET}"
    echo -e "  ${YELLOW}* Manual container access: sudo docker exec -it kali_container bash${RESET}"
    echo
}

# --- Main Logic ---
main() {
    watermark
    if [ $# -eq 0 ]; then
        help
        exit 1
    fi

    check_privileges
    
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        access)
            access
            ;;
        uninstall)
            uninstall
            ;;
        help|--help|-h)
            help
            ;;
        *)
            echo -e "${RED}Invalid command: $1${RESET}"
            help
            exit 1
            ;;
    esac
}

main "$@"


write_kali_templates() {
  SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  cat > "$SCRIPT_DIR/Dockerfile" <<'EOF'
FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
  net-tools \
  iproute2 \
  iputils-ping \
  curl \
  wget \
  nmap \
  nano \
  dnsutils \
  git \
  python3 \
  python3-pip \
  python3-venv \
  build-essential \
  gcc \
  make \
  unzip \
  sudo \
  tmux \
  vim \
  ruby \
  perl && apt clean

CMD ["/bin/bash"]
EOF

  cat > "$SCRIPT_DIR/docker-compose.yml" <<'EOF'
version: "3.8"
services:
  kali:
    build: .
    container_name: ${CONTAINER_NAME:-kali_container}
    volumes:
      - "${SANDBOX_DIR:-./sandbox}:/mnt"
    tty: true
    stdin_open: true
    cap_add:
      - NET_ADMIN
      - NET_RAW
    security_opt:
      - seccomp=unconfined
    # privileged: true   # uncomment if you want the container fully privileged
    networks:
      kali_net:
        ipv4_address: 169.16.138.3

networks:
  kali_net:
    driver: bridge
    ipam:
      config:
        - subnet: 169.16.138.0/24
EOF

  echo "Wrote Dockerfile and docker-compose.yml to $SCRIPT_DIR"
}

# Add a simple CLI hook
if [ "${1:-}" = "write-templates" ]; then
  write_kali_templates
  exit 0
fi
