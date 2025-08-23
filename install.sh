#!/bin/bash
# Install dependencies for WTF Framework on Kali

echo "[+] Updating system and installing Python3 + pip..."
sudo apt update
sudo apt install -y python3 python3-pip

echo "[+] Installing Python requirements..."
pip3 install -r requirements.txt

echo "[+] Setup complete. You can now run ./wtf.sh"
