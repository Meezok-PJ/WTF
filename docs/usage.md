# Usage & Workflows

## RustScan
1. Choose **RustScan Wrapper** → *Run scan*.
2. Enter targets and optional flags.
3. Provide Nmap flags after `--` to pass through.

## Exegol
- Install wrapper (`pipx install exegol`) via menu.
- Start a workspace container with a chosen image (e.g., `full`).

## MPSA
1. Build image once.
2. Run it; interactive Python TUI launches inside the container.

## Kali-light
- Uses provided `kali/manage.sh` to build and start a compose-based rolling Kali with a mounted `/mnt` volume.
- Access shell directly via the menu.
