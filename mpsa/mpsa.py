#!/usr/bin/env python3
"""
Meezok Pentester Search Assistant — Pure Python 3 Final Version
Features:
- Persistent Loops in sections
- Full SecLists integration with Top 5 and All views
- Exploit Search with searchsploit and Metasploit
- Content search with regex, case sensitivity, and export
- Folder and filename search with pagination
- Purple Gradient Banner
- Full Color Menus
- Error handling for missing tools
- Pythonic implementation with clean modular code
"""

import os
import sys
import json
import csv
import re
import subprocess
import shlex
import tempfile
from typing import List, Dict, Tuple, Optional, Callable, Any

# ANSI color definitions
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
MAGENTA = "\033[0;35m"
BLUE = "\033[0;34m"

# Purple gradient generator
def purple_gradient(text: str) -> str:
    """Generate a purple gradient effect for the banner text"""
    colors = [
        '\033[38;5;93m',
        '\033[38;5;129m',
        '\033[38;5;135m',
        '\033[38;5;141m',
        '\033[38;5;177m',
        '\033[38;5;183m',
    ]
    out = ''
    for i, ch in enumerate(text):
        if ch.strip() == '':
            out += ch
            continue
        out += colors[i % len(colors)] + ch + RESET
    return out

# Banner
BANNER = purple_gradient("""
=========================================
   ███╗   ███╗██████╗ ███████╗ █████╗   
   ████╗ ████║██╔══██╗██╔════╝██╔══██╗  
   ██╔████╔██║██████╔╝███████╗███████║  
   ██║╚██╔╝██║██╔═══╝ ╚════██║██╔══██║  
   ██║ ╚═╝ ██║██║     ███████║██║  ██║  
   ╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝  
   Meezok Pentester Search Assistant    
             Python Edition             
=========================================
""")

# Configuration
EXCLUDE_DIRS = [
    "/proc", "/sys", "/dev", "/run", "/tmp", 
    "/var/cache", "/var/lib/docker", "/snap", 
    "/mnt", "/media"
]
SECLISTS_BASE = "/usr/share/seclists"
WORDLISTS_DIR = "/usr/share/wordlists"
LOG_FILE = f"/tmp/mpsa_search_{os.getpid()}.log"
MAX_RESULTS = 200
PAGE_SIZE = 25
PAGER_CMD = ["less", "-R", "-N", "-S", "-F", "-X"]

# SecLists categorization
SECLISTS_CATEGORIES = {
    "Fuzzing": "Fuzzing",
    "Usernames": "Usernames",
    "Passwords": "Passwords/Common-Credentials",
    "Directories": "Discovery/Web-Content",
    "Web Shells": "Web-Shells",
    "Sensitive Data": "Sensitive-Data",
    "DNS": "Discovery/DNS",
    "API Endpoints": "Miscellaneous/api"
}

# Top lists in each category
SECLISTS_TOP5 = {
    "Fuzzing": [
        "burp-parameter-names.txt",
        "fuzzdb-attack-payloads.txt",
        "jbrofuzz-headers.txt",
        "xss-payload-list.txt",
        "fuzz.txt"
    ],
    "Usernames": [
        "top-usernames-shortlist.txt",
        "names.txt",
        "xato-net-10-million-usernames.txt",
        "common-usernames.txt",
        "admin-usernames.txt"
    ],
    "Passwords": [
        "rockyou.txt",
        "10-million-password-list-top-10000.txt",
        "darkweb2017-top10000.txt",
        "best1050.txt",
        "10k-most-common.txt"
    ],
    "Directories": [
        "directory-list-2.3-small.txt",
        "directory-list-2.3-medium.txt",
        "directory-list-2.3-big.txt",
        "directory-list-2.3-quick.txt",
        "directory-list-2.3-extended.txt"
    ],
    "Web Shells": [
        "php-reverse-shell.php",
        "jsp-shell.jsp",
        "asp-shell.asp",
        "aspx-shell.aspx",
        "python-reverse-shell.py"
    ]
}

# Tool availability cache
TOOL_CACHE = {}

def log(message: str) -> None:
    """Log messages to the log file"""
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{os.times().elapsed_time:.2f}] {message}\n")
    except:
        pass

def check_tool(tool: str) -> bool:
    """Check if a tool is available in PATH"""
    if tool in TOOL_CACHE:
        return TOOL_CACHE[tool]
    
    try:
        subprocess.run(
            ["which", tool], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL, 
            check=True
        )
        TOOL_CACHE[tool] = True
        return True
    except subprocess.CalledProcessError:
        TOOL_CACHE[tool] = False
        return False

def human_size(size: int) -> str:
    """Convert bytes to human-readable size"""
    if size >= 1073741824:
        return f"{size / 1073741824:.1f}G"
    elif size >= 1048576:
        return f"{size / 1048576:.1f}M"
    elif size >= 1024:
        return f"{size / 1024:.1f}K"
    else:
        return f"{size}B"

def display_result(file_path: str, is_dir: bool = False) -> None:
    """Display file information with color coding"""
    if not os.path.exists(file_path):
        return
    
    try:
        # Get file stats
        stat = os.stat(file_path)
        size = stat.st_size
        mtime = os.path.getmtime(file_path)
        perm = oct(stat.st_mode)[-3:]
        
        # Format time
        import time
        mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
        
        # Color coding based on file type
        color = GREEN
        if file_path.endswith(('.sh', '.py', '.pl', '.rb', '.ps1')):
            color = CYAN
        elif file_path.endswith(('.conf', '.cfg', '.ini', '.cnf', '.yaml', '.yml')):
            color = YELLOW
        elif os.access(file_path, os.X_OK):
            color = RED
            
        # Format the output
        size_str = human_size(size)
        output = (
            f"{color}{file_path[:110]:<110}{RESET} "
            f"{YELLOW}Size:{RESET} {size_str:<6} "
            f"{YELLOW}Modified:{RESET} {mtime_str:<19} "
            f"{YELLOW}Perms:{RESET} {perm}"
        )
        
        print(output)
    except Exception as e:
        print(f"{RED}Error displaying {file_path}: {str(e)}{RESET}")

def pager_or_print(content: List[str], use_pager: bool = True) -> None:
    """Display content with pager or print directly"""
    if not content:
        print(f"{YELLOW}No results to display{RESET}")
        return
    
    if use_pager and check_tool("less"):
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
                tmp.write("\n".join(content))
                tmp_path = tmp.name
            
            subprocess.run(PAGER_CMD + [tmp_path], check=True)
            os.unlink(tmp_path)
        except Exception as e:
            print(f"{RED}Pager error: {str(e)}{RESET}")
            for line in content:
                print(line)
    else:
        for line in content:
            print(line)

def detect_fast_tools() -> Tuple[Optional[str], Optional[str]]:
    """Detect fast search tools (rg and fd)"""
    rg_path = "rg" if check_tool("rg") else None
    fd_path = "fd" if check_tool("fd") else ("fdfind" if check_tool("fdfind") else None)
    return rg_path, fd_path

def suggest_seclists_install() -> None:
    """Suggest installation commands for SecLists"""
    print(f"\n{YELLOW}SecLists missing or incomplete at: {SECLISTS_BASE}{RESET}")
    print(f"{BOLD}{CYAN}Suggested commands (copy & paste to run):{RESET}")
    print(f"{GREEN}1) Apt (quick):{RESET}")
    print("   sudo apt update && sudo apt install seclists -y")
    print()
    print(f"{GREEN}2) Git clone (latest):{RESET}")
    print(f"   sudo mkdir -p {SECLISTS_BASE}")
    print(f"   sudo chown \"$(whoami)\" {SECLISTS_BASE} || true")
    print("   git clone https://github.com/danielmiessler/SecLists.git " + SECLISTS_BASE)
    print()
    print(f"{YELLOW}I will NOT run these automatically. Copy & paste to run them yourself.{RESET}")

def check_seclists_installed() -> bool:
    """Check if SecLists is properly installed"""
    if not os.path.isdir(SECLISTS_BASE):
        print(f"{RED}SecLists not found at {SECLISTS_BASE}{RESET}")
        suggest_seclists_install()
        return False
    return True

def list_seclists_info() -> None:
    """Display SecLists installation summary"""
    print(f"\n{BOLD}{CYAN}SecLists summary:{RESET}")
    
    if not os.path.isdir(SECLISTS_BASE):
        print(f"{RED}SecLists not found at {SECLISTS_BASE}.{RESET}")
        suggest_seclists_install()
        return
    
    print(f"{GREEN}SecLists base:{RESET} {SECLISTS_BASE}")
    for cat, path_suffix in SECLISTS_CATEGORIES.items():
        path = os.path.join(SECLISTS_BASE, path_suffix)
        if os.path.isdir(path):
            try:
                count = sum(1 for _ in os.listdir(path))
                print(f"  {YELLOW}{cat}:{RESET} {count} files in {path}")
            except:
                print(f"  {YELLOW}{cat}:{RESET} {RED}Cannot read directory{RESET}")
        else:
            print(f"  {YELLOW}{cat}:{RESET} {RED}Not installed ({path}){RESET}")

def show_seclists_top5(category: str) -> None:
    """Display top 5 SecLists for a category"""
    if category not in SECLISTS_CATEGORIES:
        print(f"{RED}Invalid category: {category}{RESET}")
        return
    
    if not check_seclists_installed():
        return
    
    rel_path = SECLISTS_CATEGORIES[category]
    base_path = os.path.join(SECLISTS_BASE, rel_path)
    
    print(f"\n{BOLD}{CYAN}Top 5 for {category}:{RESET}")
    
    if not os.path.isdir(base_path):
        print(f"{RED}Category path not found: {base_path}{RESET}")
        suggest_seclists_install()
        return
    
    results = []
    missing = []
    
    for filename in SECLISTS_TOP5.get(category, []):
        full_path = os.path.join(base_path, filename)
        if os.path.isfile(full_path):
            results.append(full_path)
        else:
            missing.append(full_path)
    
    if results:
        for path in results:
            display_result(path)
    
    if missing:
        print()
        for path in missing:
            print(f"{YELLOW}  (missing) {path}{RESET}")
        print(f"\n{YELLOW}Some Top-5 lists were missing.{RESET}")
        suggest_seclists_install()
    elif not results:
        print(f"{YELLOW}No Top5 files were found (maybe SecLists not installed fully){RESET}")
        suggest_seclists_install()

def show_seclists_all(category: str) -> None:
    """Display all SecLists for a category with pagination"""
    if category not in SECLISTS_CATEGORIES:
        print(f"{RED}Invalid category: {category}{RESET}")
        return
    
    if not check_seclists_installed():
        return
    
    rel_path = SECLISTS_CATEGORIES[category]
    base_path = os.path.join(SECLISTS_BASE, rel_path)
    
    print(f"\n{BOLD}{CYAN}All files for {category} (paged):{RESET}")
    
    if not os.path.isdir(base_path):
        print(f"{RED}Category path not found: {base_path}{RESET}")
        suggest_seclists_install()
        return
    
    # Collect all files
    results = []
    for root, _, files in os.walk(base_path):
        for file in files:
            results.append(os.path.join(root, file))
    
    if not results:
        print(f"{YELLOW}No files found in this category{RESET}")
        return
    
    # Display with pager
    output_lines = []
    for path in results:
        try:
            stat = os.stat(path)
            size_str = human_size(stat.st_size)
            mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
            perm = oct(stat.st_mode)[-3:]
            
            color = GREEN
            if path.endswith(('.sh', '.py', '.pl', '.rb', '.ps1')):
                color = CYAN
            elif path.endswith(('.conf', '.cfg', '.ini', '.cnf', '.yaml', '.yml')):
                color = YELLOW
            elif os.access(path, os.X_OK):
                color = RED
                
            output_lines.append(
                f"{color}{path[:110]:<110}{RESET} "
                f"{YELLOW}Size:{RESET} {size_str:<6} "
                f"{YELLOW}Modified:{RESET} {mtime_str:<19} "
                f"{YELLOW}Perms:{RESET} {perm}"
            )
        except:
            output_lines.append(f"{path}")
    
    pager_or_print(output_lines)

def search_wordlists() -> None:
    """Search and display common wordlists"""
    print(f"\n{BOLD}{CYAN}Wordlists in:{RESET} {WORDLISTS_DIR}")
    
    if not os.path.isdir(WORDLISTS_DIR):
        print(f"{RED}{WORDLISTS_DIR} missing{RESET}")
        print(f"{YELLOW}Install with: sudo apt install wordlists{RESET}")
        return
    
    common_wordlists = [
        "rockyou.txt",
        "dirb/common.txt",
        "dirbuster/directory-list-2.3-small.txt",
        "wfuzz/general/common.txt",
        "metasploit/unix_users.txt",
        "sqlmap.txt",
        "cewl.txt",
        "john.txt",
        "wfuzz/injections/xss.txt",
        "wfuzz/injections/sql.txt",
        "dnsmap.txt",
        "subdomains-top1million-5000.txt"
    ]
    
    results = []
    for w in common_wordlists:
        path = os.path.join(WORDLISTS_DIR, w)
        if os.path.isfile(path):
            results.append(path)
    
    if results:
        for path in results:
            display_result(path)
        
        # Count total wordlists
        total_count = 0
        for root, _, files in os.walk(WORDLISTS_DIR):
            total_count += len(files)
        
        print(f"\n{YELLOW}Total:{RESET} {total_count} wordlists")
    else:
        print(f"{YELLOW}No common wordlists found{RESET}")

def content_search() -> None:
    """Search for content within files using grep/rg"""
    print(f"\n{BOLD}{CYAN}===== CONTENT SEARCH ====={RESET}")
    
    # Target selection
    targets = [
        ("/", "Whole filesystem"),
        (SECLISTS_BASE, "SecLists"),
        (WORDLISTS_DIR, "Wordlists"),
        ("/var/log", "/var/log"),
        (None, "Custom path")
    ]
    
    for i, (_, desc) in enumerate(targets, 1):
        print(f"{YELLOW}{i}){RESET} {GREEN}{desc}{RESET}")
    
    try:
        choice = int(input(f"{BOLD}{GREEN}Select target [1-{len(targets)}]: {RESET}").strip())
        if choice < 1 or choice > len(targets):
            print(f"{RED}Invalid choice{RESET}")
            return
    except ValueError:
        print(f"{RED}Please enter a number{RESET}")
        return
    
    search_dir = targets[choice-1][0]
    if search_dir is None:
        search_dir = input(f"{GREEN}Enter full path: {RESET}").strip()
    
    if not os.path.isdir(search_dir):
        print(f"{RED}Directory not found: {search_dir}{RESET}")
        return
    
    # Search parameters
    search_term = input(f"{GREEN}Search term (regex supported): {RESET}").strip()
    if not search_term:
        print(f"{RED}Search term required{RESET}")
        return
    
    file_ext = input(f"{GREEN}Limit by extension (e.g. log,txt,sh) [enter=all]: {RESET}").strip()
    case_insensitive = input(f"{GREEN}Case-insensitive? (y/N): {RESET}").strip().lower() == 'y'
    use_pager = input(f"{GREEN}Use pagination (Y/n): {RESET}").strip().lower() != 'n'
    
    log(f"CONTENT_SEARCH:{search_dir}:{search_term}")
    print(f"\n{BOLD}Searching {CYAN}{search_term}{RESET} in {YELLOW}{search_dir}{RESET}")
    
    # Build find command with exclusions
    find_cmd = ["find", search_dir]
    for d in EXCLUDE_DIRS:
        find_cmd.extend(["-path", d, "-prune", "-o"])
    find_cmd.extend(["-type", "f"])
    
    if file_ext:
        find_cmd.extend(["-name", f"*.{file_ext}"])
    
    find_cmd.append("-print0")
    
    # Detect fast tools
    rg_path, _ = detect_fast_tools()
    use_rg = rg_path is not None
    
    # Execute search
    try:
        find_output = subprocess.run(
            find_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout
        
        files = find_output.strip().split('\x00')
        files = [f for f in files if f]
        
        if not files:
            print(f"{YELLOW}No files to search in{RESET}")
            return
        
        # Build grep command
        if use_rg:
            grep_cmd = [rg_path, "--line-number", "--with-filename"]
            if case_insensitive:
                grep_cmd.append("-i")
            grep_cmd.extend(["-e", search_term])
        else:
            grep_cmd = ["grep", "-nH", "--binary-files=without-match"]
            if case_insensitive:
                grep_cmd.append("-i")
            grep_cmd.extend(["-e", search_term])
        
        results = []
        hits = []
        
        for file in files:
            try:
                if use_rg:
                    output = subprocess.run(
                        [rg_path] + grep_cmd[1:] + [file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        text=True,
                        check=False
                    ).stdout
                else:
                    output = subprocess.run(
                        ["grep"] + grep_cmd[1:] + [file],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        text=True,
                        check=False
                    ).stdout
                
                if output:
                    # Process the output for display
                    for line in output.strip().split('\n'):
                        if not line:
                            continue
                        
                        # Colorize the match
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            path, lineno, match = parts[0], parts[1], parts[2]
                            colored_match = re.sub(
                                f"({re.escape(search_term)})", 
                                f"{RED}\\1{RESET}", 
                                match, 
                                flags=re.IGNORECASE if case_insensitive else 0
                            )
                            display_line = f"{GREEN}{path}{RESET}:{YELLOW}{lineno}{RESET}:{colored_match}"
                            results.append(display_line)
                            hits.append(f"{path}:{lineno}:{match}")
            except Exception as e:
                print(f"{RED}Error searching {file}: {str(e)}{RESET}")
        
        if not results:
            print(f"{YELLOW}No matches found.{RESET}")
            return
        
        # Display results
        if use_pager and results:
            pager_or_print(results)
        else:
            for line in results[:PAGE_SIZE]:
                print(line)
            if len(results) > PAGE_SIZE:
                print(f"\n{YELLOW}Showing first {PAGE_SIZE} of {len(results)} matches{RESET}")
        
        # Export option
        print(f"\n{BOLD}Export results?{RESET}")
        print(f"{YELLOW}1){RESET} {GREEN}CSV{RESET}")
        print(f"{YELLOW}2){RESET} {GREEN}JSON{RESET}")
        print(f"{YELLOW}3){RESET} {GREEN}No{RESET}")
        
        export_choice = input(f"{BOLD}{GREEN}Choice [1-3]: {RESET}").strip()
        
        if export_choice == '1':
            filename = f"mpsa_export_{int(time.time())}.csv"
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["path", "size", "mtime", "line_num", "matched_line"])
                
                for hit in hits:
                    parts = hit.split(':', 2)
                    if len(parts) < 3:
                        continue
                    
                    path, lineno, match = parts[0], parts[1], parts[2]
                    try:
                        stat = os.stat(path)
                        size = stat.st_size
                        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                        writer.writerow([path, size, mtime, lineno, match])
                    except:
                        writer.writerow([path, "", "", lineno, match])
            
            print(f"\n{GREEN}Exported CSV to: {filename}{RESET}")
        
        elif export_choice == '2':
            filename = f"mpsa_export_{int(time.time())}.json"
            export_data = []
            
            for hit in hits:
                parts = hit.split(':', 2)
                if len(parts) < 3:
                    continue
                
                path, lineno, match = parts[0], parts[1], parts[2]
                try:
                    stat = os.stat(path)
                    size = stat.st_size
                    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                    
                    export_data.append({
                        "path": path,
                        "size": size,
                        "mtime": mtime,
                        "line_num": lineno,
                        "matched_line": match
                    })
                except:
                    export_data.append({
                        "path": path,
                        "line_num": lineno,
                        "matched_line": match
                    })
            
            with open(filename, 'w') as jsonfile:
                json.dump(export_data, jsonfile, indent=2)
            
            print(f"\n{GREEN}Exported JSON to: {filename}{RESET}")
    
    except subprocess.CalledProcessError as e:
        print(f"{RED}Search error: {str(e)}{RESET}")

def filename_search() -> None:
    """Search for files by name using find"""
    print(f"\n{BOLD}{CYAN}===== FILENAME SEARCH ====={RESET}")
    
    # Target selection
    targets = [
        ("/", "Whole filesystem"),
        (SECLISTS_BASE, "SecLists"),
        (WORDLISTS_DIR, "Wordlists"),
        ("/etc", "/etc"),
        ("/var/log", "/var/log"),
        (None, "Custom path")
    ]
    
    for i, (_, desc) in enumerate(targets, 1):
        print(f"{YELLOW}{i}){RESET} {GREEN}{desc}{RESET}")
    
    try:
        choice = int(input(f"{BOLD}{GREEN}Select target [1-{len(targets)}]: {RESET}").strip())
        if choice < 1 or choice > len(targets):
            print(f"{RED}Invalid choice{RESET}")
            return
    except ValueError:
        print(f"{RED}Please enter a number{RESET}")
        return
    
    search_dir = targets[choice-1][0]
    if search_dir is None:
        search_dir = input(f"{GREEN}Enter full path: {RESET}").strip()
    
    if not os.path.isdir(search_dir):
        print(f"{RED}Directory not found{RESET}")
        return
    
    # Search parameters
    pattern = input(f"{GREEN}Filename pattern (supports wildcards, e.g. passwd, *.conf): {RESET}").strip()
    if not pattern:
        print(f"{RED}Pattern required{RESET}")
        return
    
    file_ext = input(f"{GREEN}Limit to extension (e.g., log,txt) [enter=all]: {RESET}").strip()
    use_pager = input(f"{GREEN}Use pagination (Y/n): {RESET}").strip().lower() != 'n'
    
    log(f"FILENAME_SEARCH:{search_dir}:{pattern}")
    print(f"\n{BOLD}Searching for {CYAN}{pattern}{RESET} in {YELLOW}{search_dir}{RESET}")
    
    # Build find command
    find_cmd = ["find", search_dir]
    for d in EXCLUDE_DIRS:
        find_cmd.extend(["-path", d, "-prune", "-o"])
    find_cmd.extend(["-type", "f", "-iname", f"*{pattern}*"])
    
    if file_ext:
        find_cmd.extend(["-name", f"*.{file_ext}"])
    
    find_cmd.append("-print0")
    
    # Execute search
    try:
        find_output = subprocess.run(
            find_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout
        
        files = find_output.strip().split('\x00')
        files = [f for f in files if f]
        
        if not files:
            print(f"{YELLOW}No files found matching pattern{RESET}")
            return
        
        # Display results
        results = []
        for file in files[:MAX_RESULTS]:
            results.append(file)
        
        if len(files) > MAX_RESULTS:
            print(f"\n{YELLOW}Showing first {MAX_RESULTS} of {len(files)} results{RESET}")
        
        # Format results for display
        display_lines = []
        for file in results:
            display_result(file)
        
        # Use pager if requested
        if use_pager and display_lines:
            pager_or_print(display_lines)
        
        # Export option
        print(f"\n{BOLD}Export filename results?{RESET}")
        print(f"{YELLOW}1){RESET} {GREEN}CSV{RESET}")
        print(f"{YELLOW}2){RESET} {GREEN}JSON{RESET}")
        print(f"{YELLOW}3){RESET} {GREEN}No{RESET}")
        
        export_choice = input(f"{BOLD}{GREEN}Choice [1-3]: {RESET}").strip()
        
        if export_choice in ['1', '2']:
            filename = f"mpsa_files_{int(time.time())}.{'csv' if export_choice == '1' else 'json'}"
            
            if export_choice == '1':
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["path", "size", "mtime"])
                    
                    for path in results:
                        try:
                            stat = os.stat(path)
                            size = stat.st_size
                            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                            writer.writerow([path, size, mtime])
                        except:
                            writer.writerow([path, "", ""])
                
                print(f"\n{GREEN}Exported CSV to: {filename}{RESET}")
            
            else:
                export_data = []
                for path in results:
                    try:
                        stat = os.stat(path)
                        size = stat.st_size
                        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                        
                        export_data.append({
                            "path": path,
                            "size": size,
                            "mtime": mtime
                        })
                    except:
                        export_data.append({"path": path})
                
                with open(filename, 'w') as jsonfile:
                    json.dump(export_data, jsonfile, indent=2)
                
                print(f"\n{GREEN}Exported JSON to: {filename}{RESET}")
    
    except subprocess.CalledProcessError as e:
        print(f"{RED}Search error: {str(e)}{RESET}")

def folder_search() -> None:
    """Search for directories by name"""
    print(f"\n{BOLD}{CYAN}===== FOLDER SEARCH ====={RESET}")
    
    # Target selection
    targets = [
        ("/", "Whole filesystem"),
        (SECLISTS_BASE, "SecLists"),
        (WORDLISTS_DIR, "Wordlists"),
        ("/var/www", "/var/www"),
        ("/var/log", "/var/log"),
        (None, "Custom path")
    ]
    
    for i, (_, desc) in enumerate(targets, 1):
        print(f"{YELLOW}{i}){RESET} {GREEN}{desc}{RESET}")
    
    try:
        choice = int(input(f"{BOLD}{GREEN}Select target [1-{len(targets)}]: {RESET}").strip())
        if choice < 1 or choice > len(targets):
            print(f"{RED}Invalid choice{RESET}")
            return
    except ValueError:
        print(f"{RED}Please enter a number{RESET}")
        return
    
    search_dir = targets[choice-1][0]
    if search_dir is None:
        search_dir = input(f"{GREEN}Enter full path: {RESET}").strip()
    
    if not os.path.isdir(search_dir):
        print(f"{RED}Directory not found: {search_dir}{RESET}")
        return
    
    # Search parameters
    pattern = input(f"{GREEN}Folder name pattern (supports wildcards, e.g. '*backup*'): {RESET}").strip()
    if not pattern:
        print(f"{RED}Pattern required{RESET}")
        return
    
    min_size = input(f"{GREEN}Minimum size (e.g. 10M) [enter=any]: {RESET}").strip()
    use_pager = input(f"{GREEN}Use pagination (Y/n): {RESET}").strip().lower() != 'n'
    
    log(f"FOLDER_SEARCH:{search_dir}:{pattern}:minsize={min_size}")
    
    # Build find command
    find_cmd = ["find", search_dir]
    for d in EXCLUDE_DIRS:
        find_cmd.extend(["-path", d, "-prune", "-o"])
    find_cmd.extend(["-type", "d", "-iname", pattern, "-print0"])
    
    # Execute search
    try:
        find_output = subprocess.run(
            find_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        ).stdout
        
        folders = find_output.strip().split('\x00')
        folders = [f for f in folders if f]
        
        # Filter by size if specified
        if min_size:
            filtered_folders = []
            for folder in folders:
                try:
                    # Parse size argument
                    units = min_size[-1].lower()
                    value = int(min_size[:-1]) if min_size[:-1] else 1
                    
                    if units == 'k':
                        min_bytes = value * 1024
                    elif units == 'm':
                        min_bytes = value * 1024 * 1024
                    elif units == 'g':
                        min_bytes = value * 1024 * 1024 * 1024
                    else:
                        min_bytes = value  # Assume bytes
                    
                    # Get folder size
                    du_output = subprocess.run(
                        ["du", "-sb", folder],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        text=True,
                        check=True
                    ).stdout
                    
                    size_bytes = int(du_output.split()[0])
                    
                    if size_bytes >= min_bytes:
                        filtered_folders.append(folder)
                except Exception as e:
                    print(f"{RED}Error processing {folder}: {str(e)}{RESET}")
                    continue
            
            folders = filtered_folders
        
        if not folders:
            print(f"{YELLOW}No matching folders found.{RESET}")
            return
        
        # Display results
        results = []
        for folder in folders[:MAX_RESULTS]:
            try:
                # Get folder stats
                du_output = subprocess.run(
                    ["du", "-sh", folder],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    check=True
                ).stdout
                
                size = du_output.split()[0]
                mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(folder)))
                perm = oct(os.stat(folder).st_mode)[-3:]
                
                results.append(
                    f"{CYAN}{folder}{RESET}\n"
                    f"  {YELLOW}Size:{RESET} {size}  "
                    f"{YELLOW}Modified:{RESET} {mtime}  "
                    f"{YELLOW}Perms:{RESET} {perm}\n"
                    f"  {'-' * 40}"
                )
            except Exception as e:
                results.append(
                    f"{RED}{folder}{RESET}\n"
                    f"  {YELLOW}Error:{RESET} {str(e)}"
                )
        
        if len(folders) > MAX_RESULTS:
            print(f"\n{YELLOW}Showing first {MAX_RESULTS} of {len(folders)} results{RESET}")
        
        # Use pager if requested
        if use_pager and results:
            pager_or_print(results)
        else:
            for r in results:
                print(r)
        
        # Export option
        print(f"\n{BOLD}Export folder results?{RESET}")
        print(f"{YELLOW}1){RESET} {GREEN}CSV{RESET}")
        print(f"{YELLOW}2){RESET} {GREEN}JSON{RESET}")
        print(f"{YELLOW}3){RESET} {GREEN}No{RESET}")
        
        export_choice = input(f"{BOLD}{GREEN}Choice [1-3]: {RESET}").strip()
        
        if export_choice in ['1', '2']:
            filename = f"mpsa_folders_{int(time.time())}.{'csv' if export_choice == '1' else 'json'}"
            
            if export_choice == '1':
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["path", "size", "mtime"])
                    
                    for path in folders[:MAX_RESULTS]:
                        try:
                            du_output = subprocess.run(
                                ["du", "-sb", path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL,
                                text=True,
                                check=True
                            ).stdout
                            
                            size = du_output.split()[0]
                            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                            writer.writerow([path, size, mtime])
                        except:
                            writer.writerow([path, "", ""])
                
                print(f"\n{GREEN}Exported CSV to: {filename}{RESET}")
            
            else:
                export_data = []
                for path in folders[:MAX_RESULTS]:
                    try:
                        du_output = subprocess.run(
                            ["du", "-sb", path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            text=True,
                            check=True
                        ).stdout
                        
                        size = du_output.split()[0]
                        mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(path)))
                        
                        export_data.append({
                            "path": path,
                            "size": size,
                            "mtime": mtime
                        })
                    except:
                        export_data.append({"path": path})
                
                with open(filename, 'w') as jsonfile:
                    json.dump(export_data, jsonfile, indent=2)
                
                print(f"\n{GREEN}Exported JSON to: {filename}{RESET}")
    
    except subprocess.CalledProcessError as e:
        print(f"{RED}Search error: {str(e)}{RESET}")

def exploit_search() -> None:
    """Search for exploits using searchsploit and Metasploit"""
    print(f"\n{BOLD}{CYAN}===== EXPLOIT SEARCH ====={RESET}")
    
    # Check for required tools
    searchsploit_available = check_tool("searchsploit")
    msfconsole_available = check_tool("msfconsole")
    
    if not searchsploit_available and not msfconsole_available:
        print(f"{RED}Neither searchsploit nor msfconsole is available.{RESET}")
        print(f"{YELLOW}Install with: sudo apt install exploitdb metasploit-framework{RESET}")
        return
    
    # Search parameters
    term = input(f"{GREEN}Enter exploit search term: {RESET}").strip()
    if not term:
        print(f"{RED}Search term required{RESET}")
        return
    
    use_pager = input(f"{GREEN}Use pagination (Y/n): {RESET}").strip().lower() != 'n'
    
    log(f"EXPLOIT_SEARCH:{term}")
    print(f"\n{BOLD}Searching for exploits related to: {CYAN}{term}{RESET}")
    
    results = []
    
    # Search with searchsploit if available
    if searchsploit_available:
        print(f"\n{BOLD}Searching with {CYAN}searchsploit{RESET}...")
        try:
            output = subprocess.run(
                ["searchsploit", term],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            ).stdout
            
            if output.strip():
                results.append(f"{BOLD}{YELLOW}Results from searchsploit:{RESET}")
                results.extend(output.strip().split('\n'))
                results.append("")  # Add spacing
        except subprocess.CalledProcessError as e:
            print(f"{RED}searchsploit error: {str(e)}{RESET}")
    
    # Search with Metasploit if available
    if msfconsole_available:
        print(f"\n{BOLD}Searching with {CYAN}Metasploit{RESET}...")
        try:
            # Run msfconsole command to search
            output = subprocess.run(
                ["msfconsole", "-q", "-x", f"search {term}; exit"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=True
            ).stdout
            
            # Extract relevant part of the output
            msf_results = []
            in_results = False
            for line in output.split('\n'):
                if "=====================" in line and not in_results:
                    in_results = True
                    continue
                if in_results and line.strip() == "":
                    break
                if in_results:
                    msf_results.append(line)
            
            if msf_results:
                results.append(f"{BOLD}{YELLOW}Results from Metasploit:{RESET}")
                results.extend(msf_results)
        except subprocess.CalledProcessError as e:
            print(f"{RED}Metasploit error: {str(e)}{RESET}")
    
    if not results:
        print(f"{YELLOW}No exploits found for '{term}'{RESET}")
        return
    
    # Display results
    if use_pager:
        pager_or_print(results)
    else:
        for line in results:
            print(line)
    
    # Export option
    print(f"\n{BOLD}Export exploit results?{RESET}")
    print(f"{YELLOW}1){RESET} {GREEN}CSV{RESET}")
    print(f"{YELLOW}2){RESET} {GREEN}JSON{RESET}")
    print(f"{YELLOW}3){RESET} {GREEN}No{RESET}")
    
    export_choice = input(f"{BOLD}{GREEN}Choice [1-3]: {RESET}").strip()
    
    if export_choice in ['1', '2']:
        filename = f"mpsa_exploits_{int(time.time())}.{'csv' if export_choice == '1' else 'json'}"
        
        if export_choice == '1':
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["source", "result"])
                
                current_source = ""
                for line in results:
                    if "Results from" in line:
                        current_source = line.split("from")[1].strip().rstrip(':')
                        continue
                    if line.strip() and not line.startswith("==="):
                        writer.writerow([current_source, line])
            
            print(f"\n{GREEN}Exported CSV to: {filename}{RESET}")
        
        else:
            export_data = []
            current_source = ""
            for line in results:
                if "Results from" in line:
                    current_source = line.split("from")[1].strip().rstrip(':')
                    continue
                if line.strip() and not line.startswith("==="):
                    export_data.append({
                        "source": current_source,
                        "result": line
                    })
            
            with open(filename, 'w') as jsonfile:
                json.dump(export_data, jsonfile, indent=2)
            
            print(f"\n{GREEN}Exported JSON to: {filename}{RESET}")

def system_info() -> None:
    """Display system information"""
    print(f"\n{BOLD}{CYAN}===== SYSTEM INFORMATION ====={RESET}")
    
    # SecLists info
    print(f"{YELLOW}SecLists Location:{RESET} {SECLISTS_BASE}")
    if os.path.isdir(SECLISTS_BASE):
        print(f"{GREEN}SecLists is installed{RESET}")
        print(f"{YELLOW}Total categories:{RESET} {len(SECLISTS_CATEGORIES)}")
        
        # Count files in each category
        for category, path_suffix in SECLISTS_CATEGORIES.items():
            category_path = os.path.join(SECLISTS_BASE, path_suffix)
            if os.path.isdir(category_path):
                try:
                    file_count = sum(1 for _ in os.listdir(category_path))
                    print(f"{YELLOW}  {category} files:{RESET} {file_count}")
                except:
                    print(f"{YELLOW}  {category} files:{RESET} {RED}Cannot read directory{RESET}")
            else:
                print(f"{YELLOW}  {category} files:{RESET} {RED}Not found{RESET}")
    else:
        print(f"{RED}SecLists is not installed!{RESET}")
        print(f"{YELLOW}Install with:{RESET} sudo apt install seclists")
    
    # Wordlists info
    print(f"\n{YELLOW}Wordlists Location:{RESET} {WORDLISTS_DIR}")
    if os.path.isdir(WORDLISTS_DIR):
        try:
            wordlist_count = sum(1 for _, _, files in os.walk(WORDLISTS_DIR) for _ in files)
            print(f"{YELLOW}Total wordlists:{RESET} {wordlist_count}")
        except:
            print(f"{YELLOW}Total wordlists:{RESET} {RED}Cannot count{RESET}")
    else:
        print(f"{RED}Wordlists package is not installed!{RESET}")
        print(f"{YELLOW}Install with:{RESET} sudo apt install wordlists")
    
    # Excluded directories
    print(f"\n{YELLOW}Excluded directories:{RESET}")
    for dir in EXCLUDE_DIRS:
        print(f"  - {dir}")
    
    # Tool availability
    print(f"\n{YELLOW}Available tools:{RESET}")
    tools = {
        "find": "File searching",
        "grep": "Content searching",
        "rg": "Fast content searching (ripgrep)",
        "fd": "Fast filename searching",
        "searchsploit": "Exploit database",
        "msfconsole": "Metasploit Framework"
    }
    
    for tool, desc in tools.items():
        status = GREEN + "available" + RESET if check_tool(tool) else RED + "missing" + RESET
        print(f"  {tool}: {status} - {desc}")
    
    print(f"\n{YELLOW}Note:{RESET} Showing top {MAX_RESULTS} results for all searches")
    input(f"{GREEN}\nPress Enter to return to main menu...{RESET}")

def check_dependencies() -> bool:
    """Check for required dependencies"""
    required_tools = ["find", "stat", "grep", "xargs", "less", "sed", "awk", "bc"]
    missing = [tool for tool in required_tools if not check_tool(tool)]
    
    if missing:
        print(f"{RED}Missing required tools: {', '.join(missing)}{RESET}")
        print(f"{YELLOW}Install with: sudo apt install {' '.join(required_tools)}{RESET}")
        return False
    
    return True

def persistent_section(action_name: str, action_func: Callable[[], None]) -> None:
    """Run an action in a persistent loop"""
    while True:
        try:
            action_func()
        except Exception as e:
            print(f"{RED}Error: {str(e)}{RESET}")
        
        again = input(f"{YELLOW}Run another {action_name}? (Y/n): {RESET}").strip().lower()
        if again == 'n':
            break

def print_main_menu() -> None:
    """Print the main menu"""
    print(BANNER)
    print(f"{BOLD}{CYAN}===== MEEZOK'S PENTEST SEARCH ====={RESET}")
    print(f"{YELLOW}1){RESET} {GREEN}Browse SecLists categories (Top 5 / All){RESET}")
    print(f"{YELLOW}2){RESET} {GREEN}Exploit search (searchsploit / Metasploit){RESET}")
    print(f"{YELLOW}3){RESET} {GREEN}Content search{RESET}")
    print(f"{YELLOW}4){RESET} {GREEN}Filename search{RESET}")
    print(f"{YELLOW}5){RESET} {GREEN}Folder search{RESET}")
    print(f"{YELLOW}6){RESET} {GREEN}Wordlists summary{RESET}")
    print(f"{YELLOW}7){RESET} {GREEN}System info (one-shot){RESET}")
    print(f"{YELLOW}8){RESET} {RED}Exit{RESET}")

def main_menu() -> None:
    """Main menu loop"""
    if not check_dependencies():
        print(f"\n{YELLOW}Some required tools are missing. The tool may not function properly.{RESET}")
        input(f"{YELLOW}Press Enter to continue anyway...{RESET}")
    
    log(f"Started MPSA Python version {os.getpid()}")
    
    while True:
        print_main_menu()
        choice = input(f"{BOLD}{GREEN}Select option [1-8]: {RESET}").strip()
        
        try:
            if choice == '1':
                def browse_action():
                    list_seclists_info()
                    print(f"\nChoose a category to inspect:")
                    
                    categories = list(SECLISTS_CATEGORIES.keys())
                    for i, cat in enumerate(categories, 1):
                        print(f"{YELLOW}{i}){RESET} {GREEN}{cat}{RESET}")
                    print(f"{YELLOW}{len(categories)+1}){RESET} {GREEN}Back{RESET}")
                    
                    try:
                        cat_choice = int(input(f"{BOLD}{GREEN}Choice: {RESET}").strip())
                        if 1 <= cat_choice <= len(categories):
                            selected = categories[cat_choice-1]
                            print(f"{BOLD}Selected:{RESET} {selected}")
                            
                            print(f"{YELLOW}1){RESET} {GREEN}Top 5 (recommended){RESET}")
                            print(f"{YELLOW}2){RESET} {GREEN}All (paged){RESET}")
                            print(f"{YELLOW}3){RESET} {GREEN}Back{RESET}")
                            
                            show_choice = input(f"{BOLD}{GREEN}Choose: {RESET}").strip()
                            
                            if show_choice == '1':
                                show_seclists_top5(selected)
                            elif show_choice == '2':
                                show_seclists_all(selected)
                    except ValueError:
                        print(f"{RED}Please enter a number{RESET}")
                
                persistent_section("SecLists browsing", browse_action)
            
            elif choice == '2':
                persistent_section("exploit search", exploit_search)
            
            elif choice == '3':
                persistent_section("content search", content_search)
            
            elif choice == '4':
                persistent_section("filename search", filename_search)
            
            elif choice == '5':
                persistent_section("folder search", folder_search)
            
            elif choice == '6':
                persistent_section("wordlists summary", search_wordlists)
            
            elif choice == '7':
                system_info()
            
            elif choice == '8':
                log("Exit")
                print(f"{GREEN}Bye — happy hunting!{RESET}")
                break
            
            else:
                print(f"{RED}Invalid choice. Try again.{RESET}")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Interrupted by user. Returning to main menu...{RESET}")
        except Exception as e:
            print(f"{RED}Unexpected error: {str(e)}{RESET}")

if __name__ == '__main__':
    try:
        import time
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user.{RESET}")
        sys.exit(1)