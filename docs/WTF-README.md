

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
![01-00-18-WTF-24-08-2025.png](..\..\Finalized\WTF-images\01-00-18-WTF-24-08-2025.png)
![01-02-25-WTF-24-08-2025.png](..\..\Finalized\WTF-images\01-02-25-WTF-24-08-2025.png)
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

### **Use Cases**:
* [User-Friendly Kali Docker Tool](....)
* [RustScan]()
* 


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

***

### 👁️ User-Friendly RustScan Tool Usage

#### RustScan Module

* Designed to boost your efficiency, the RustScan module wraps the RustScan Docker image in a simple, user-friendly TUI (Terminal User Interface). A foundational knowledge of RustScan and Nmap flags will help you get the most out of the tool. Refer to this menu for a quick and comprehensive guide.

### ⚠️ Important Setup Note

* If you are running `./wtf.sh` with `sudo` for the very first time, it is highly recommended to use option **\[2] Build Local RustScan Image** first. This will ensure all permissions are correctly configured and that the local Docker image is available for subsequent scans.

***

### Usage Guide

This is a step-by-step guide on how to run a scan using the RustScan module within the WTF framework.

1. **Launch the Framework and Select the RustScan Option**

   Begin by running the main `wtf.sh` script. From the main menu, type `1` and press `Enter` to access the RustScan Wrapper.
![01-07-13-WTF-24-08-2025.png](..\..\Finalized\WTF-images\01-07-13-WTF-24-08-2025.png)
![01-17-40-WTF-24-08-2025.png](..\..\Finalized\WTF-images\01-17-40-WTF-24-08-2025.png)
2. **Input Scan Parameters**

   The tool will guide you through the required inputs for your scan in a user-friendly, interactive way. You'll be prompted to provide Four key parameters:

   * **Target(s):** The IP address, CIDR range, or hostname you want to scan.

   * **Extra RustScan flags:** Any additional flags for RustScan itself (e.g., `-t 500` for a faster timeout).

   * **Nmap flags:** Flags to be passed through to Nmap for more detailed analysis (e.g., `-sC -sV` for default script and version detection).
  ![02-27-05-WTF-24-08-2025.png](..\..\Finalized\WTF-images\02-27-05-WTF-24-08-2025.png)
   * Once you have entered your parameters, the tool will ask if you want to use the latest image variant. Type `y` and press `Enter` to confirm, or just press `Enter` to use the default. Finally, press `Enter` one more time to run the scan.

   ![02-34-35-WTF-24-08-2025.png](..\..\Finalized\WTF-images\02-34-35-WTF-24-08-2025.png)

3. **Review and Access the Scan Log**

   * **Logging and Post-Scan Review**

  After the scan is complete, the output is automatically saved to a log file in the `logs/` directory. The log file follows the format: `rustscan_ip_date_time-24format.log`. For example: `rustscan_19216832_2025-08-24_02-34-33.log`.
  * Return Back to the WTF menu by choosing option `0`
![02-42-55-WTF-24-08-2025.png](..\..\Finalized\WTF-images\02-42-55-WTF-24-08-2025.png)
* **View Scan Results**

  To view the scan results, you can use the `4` option in the menu. The tool will prompt you for the full path of the log file you wish to view. For easy access, you can copy the full log path (e.g., `/home/meezok/WTF/logs/rustscan_19216832_2025-08-24_02-34-33.log`) using `Ctrl+Shift+C` and paste it into the input field with `Ctrl+Shift+V`.

   
![03-16-43-WTF-24-08-2025.png](..\..\Finalized\WTF-images\03-16-43-WTF-24-08-2025.png)
* Result of rust scan inside the Log press `q` to quit :
 ![03-33-58-WTF-24-08-2025.png](..\..\Finalized\WTF-images\03-33-58-WTF-24-08-2025.png)

***

### Core Features

#### **\[1] Run RustScan Scan**

This option initiates the RustScan wrapper's **Terminal User Interface (TUI)**. It guides you through a seamless and interactive process for running scans. A foundational knowledge of RustScan and Nmap flags will help you get the most out of this feature.

#### **\[2] Build Local RustScan Image**

This feature allows you to build a customized, local Docker image for RustScan. It's ideal for users who need to add specific tools or dependencies, or simply prefer to have a local version ready to go. The process automates the Docker build command using the `Dockerfile.rustscan` file, ensuring a seamless and repeatable setup.

#### **\[3] Setup Alias (Bash/Zsh)**

To simplify your workflow, this feature automatically creates a convenient alias for the RustScan Docker command in your `.bashrc` or `.zshrc` file. Once the alias is set up, you can run RustScan directly from your terminal as if it were natively installed, without having to type the long `docker run` command. After selecting this option, you must run `source ~/.bashrc` or `source ~/.zshrc` to apply the changes to your current terminal session.



3\. Review and Access the Scan Log

After the scan is complete, the output will be automatically saved to a log file in the logs/ directory. You can easily access this log file, which is named based on the target and timestamp, directly from the main wtf.sh menu.

[4] help menu 

```bash
-------------------------------------------------------------+
|              Nmap & RustScan Cheat Sheet                    |
+-------------------------------------------------------------+
|                    RustScan - The Modern Port Scanner       |
+-------------------------------------------------------------+
| Flag/Switch          | Description                          |
+----------------------+--------------------------------------+
| -a <target>          | Target IP address or CIDR range.     |
|                      | Example: 192.168.1.1 or 10.10.10.0/24|
+----------------------+--------------------------------------+
| -p <ports>           | Scan specified ports.                |
|                      | Example: -p 80,443                   |
+----------------------+--------------------------------------+
| -r <range>           | Scan a port range.                   |
|                      | Example: 1-1000                      |
+----------------------+--------------------------------------+
| --top <num>          | Scan the top N ports.                |
|                      | Example: --top 100                   |
+----------------------+--------------------------------------+
| -b <num>             | Set batch size for scanning.         |
|                      | Example: -b 1500                     |
+----------------------+--------------------------------------+
| -t <num>             | Set timeout in milliseconds.         |
|                      | Example: -t 500                      |
+----------------------+--------------------------------------+
|                        Nmap - Network Mapper                |
+-------------------------------------------------------------+
| Flag/Switch          | Description                          |
+----------------------+--------------------------------------+
| -sS                  | TCP SYN scan (stealth scan).         |
+----------------------+--------------------------------------+
| -sT                  | TCP Connect scan (full handshake).   |
+----------------------+--------------------------------------+
| -sU                  | UDP scan.                            |
+----------------------+--------------------------------------+
| -p <ports>           | Scan specified ports (e.g., -p 80,443).|
+----------------------+--------------------------------------+
| -p-                  | Scan all 65535 ports.                |
+----------------------+--------------------------------------+
| -F                   | Fast scan (top 100 ports).           |
+----------------------+--------------------------------------+
| -A                   | Aggressive scan (OS detection,       |
|                      | version detection, script scanning). |
+----------------------+--------------------------------------+
| -sV                  | Version detection.                   |
+----------------------+--------------------------------------+
| -O                   | OS detection.                        |
+----------------------+--------------------------------------+
| -T<0-5>              | Set scan timing (0=slow, 5=fast).    |
+----------------------+--------------------------------------+
| -Pn                  | Treat all hosts as online (skip ping).|
+----------------------+--------------------------------------+
| -oN <file>           | Output to normal format.             |
+----------------------+--------------------------------------+
| -oX <file>           | Output to XML format.                |
+----------------------+--------------------------------------+
| -iL <file>           | Scan targets from a file.            |
+----------------------+--------------------------------------+
| -v                   | Increase verbosity.                  |
+----------------------+--------------------------------------+
| --script=<script>    | Run a specific Nmap script.          |
+----------------------+--------------------------------------+
| -sC                  | Equivalent to --script=default.      |
+----------------------+--------------------------------------+

```
