# WTF — Wrapper for Tactical Frameworks (Title: WTF)

A modular Bash-based launcher that unifies **RustScan**,**MPSA** (Python), and a **Kali-light** sandbox.
Runs on Bash & Zsh. All tools log to `logs/<tool>.log` and central `logs/wtf.log` (JSON lines).

## Quickstart
```bash
chmod +x wtf.sh *.sh */*.sh
./wtf.sh
```

## Logs
- Central log: `logs/wtf.log` (JSON, machine-parsable)
- Per-tool logs: `logs/rustscan.log`, `logs/mpsa.log`, `logs/kali.log`

## Notes
- Docker is required for RustScan, MPSA, and Kali components.
- MPSA container mounts host SecLists/wordlists if present (read-only).
