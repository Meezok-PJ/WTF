### 🛠️ WTF Wrapper Tactical Framework

## 📖 Overview

**WTF (Wrapper Tactical Framework)** is a modular, Bash-based launcher designed to make penetration testers and sysadmins more **productive, user-friendly, and efficient**.

Instead of juggling long one-liner scripts and environment setup, WTF **wraps around tactical tools** and presents them in a clean, interactive way.

💡 **Note from the Author**\
The main reason I created this framework is to assist me in **CTFs (Capture The Flag challenges) and penetration testing simulations**, while also increasing my productivity and efficiency.

I am still in the **learning phase of penetration testing** and not yet a professional in the field, so this project is a **work in progress**. Some features may change or be removed as I gain more knowledge, and better features will be added along the way. This is both a **tool for practice** and a **concept I am continuously improving** as I grow in cybersecurity.

–– 

## 🔑 Features

* 🧩 **Modular Bash Launcher** — one framework, multiple tools.

* ⚡ **RustScan Wrapper** — requires knowledge of RustScan + Nmap flags.

* 🔍 **MPSA (Meezok Pentester Search Assistant)** — advanced file/wordlist search (regex, wildcards).

* 🐳 **Kali-Light Sandbox** — lightweight Dockerized Kali for tool testing.

* 📜 **Unified Logging** — JSON lines written to `logs/`, easy to parse.

* 🖥️ **Cross-Shell Support** — works on **Bash** and **Zsh**.

---

## 🏗️ Architecture

```text
WTF/
├── wtf.sh             # Main launcher
├── wtf_lib.sh         # Helper library
├── rustscan_wrapper.sh
├── kali_manager.sh    # Kali sandbox handler
├── mpsa_manager.sh    # MPSA handler
├── mpsa/              # Python search assistant
├── kali/              # Kali management scripts
├── logs/              # Central + per-tool logs
└── docs/              # Usage documentation
```

---

## ⚙️ Installation

### Requirements

* **Linux / macOS**

* **Bash or Zsh**

* **Docker** (for RustScan, MPSA, Kali sandbox)

### Setup

```bash
# Clone repo
git clone https://github.com/<your-username>/WTF.git
cd WTF

# Make scripts executable
chmod +x wtf.sh *.sh */*.sh

# Run launcher
./wtf.sh
```

***

## 🕹️ Usage

### Quickstart

```bash
cd ~/WTF
./wtf.sh
```

### Logs

* Central log → `logs/wtf.log` (JSON, machine-parsable)

* Per-tool logs → `logs/rustscan.log`, `logs/mpsa.log`, `logs/kali.log`

### Example: RustScan Wrapper

```bash
./rustscan_wrapper.sh -a 192.168.1.1 -- -sV
```

### Example: MPSA (Regex Search)

```bash
python3 mpsa/mpsa.py --search "*.conf" --regex "password"
```

### Example: Kali Sandbox

```bash
./kali_manager.sh start
./kali_manager.sh stop
```

***

## ⚙️ Configuration

* By default, MPSA will attempt to **mount host SecLists/wordlists** if present (read-only).

* The sandbox creates a `$HOME/kali_sandbox/README.md` with manual usage notes.

* All logs are JSON-structured for easier integration with **SIEM/ELK/Grafana**.

***

## 🤝 Contributing

Contributions are welcome! Since this framework is also part of my **learning journey in penetration testing**, I’m open to feedback, corrections, and suggestions.

Please:

1. Fork the repo

2. Create a feature branch (`git checkout -b feature/my-feature`)

3. Commit changes (`git commit -m "Add feature"`)

4. Push to branch (`git push origin feature/my-feature`)

5. Open a Pull Request 🚀

***

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](https://chatgpt.com/c/LICENSE) file for details.

***

## 🙏 Credits

* [RustScan](https://github.com/RustScan/RustScan)

* [SecLists](https://github.com/danielmiessler/SecLists)

* [Docker](https://www.docker.com/)

* Inspired by real-world pentesting frustrations and CTF practice 🕵️‍♂️

***

## 🙌 Special Thanks

I would like to give a huge **thank you** to the developers and communities behind:

* 🐳 **[Docker](https://www.docker.com/)** — for making containerization simple, fast, and reliable.

* 📂 **[SecLists](https://github.com/danielmiessler/SecLists)** — for providing an incredible resource of wordlists that power countless security projects.

* ⚡ **[RustScan](https://github.com/RustScan/RustScan)** — for building one of the fastest and most efficient port scanners out there.

Thanks to their amazing work, **WTF (Wrapper Tactical Framework)** became a true **powerhouse for productivity and efficiency** in pentesting simulations and CTF practice. 🚀

***

✅ Now your README has **purpose, honesty, professionalism, and gratitude** — perfect for GitHub.

Do you also want me to add a **Roadmap section** (planned features + improvements), so contributors and users can see where the project is heading?




## ⚠️ Limitations

* 🔍 **MPSA Module Search (Metasploit)** → The feature for searching directly within Metasploit modules is **not yet functional**.

* 🐳 **Docker dependency** → All containerized components (RustScan, MPSA, Kali Sandbox) require Docker to be installed and running.

* 🔄 **Learning Project** → As this framework evolves with my pentesting journey, some features may change, be removed, or replaced with better implementations.
