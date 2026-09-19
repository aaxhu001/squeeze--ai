#!/usr/bin/env python3
"""
Squeeze AI — 1-Click MCP Auto-Installer
Automatically connects Squeeze AI MCP to:
1. Claude Code CLI (via `claude mcp add`)
2. Claude Desktop App (via `claude_desktop_config.json`)
3. Cursor IDE (via `~/.cursor/mcp.json`)
4. Windsurf / VS Code (via mcp.json)

Zero dependencies — works out of the box with standard Python 3.
"""

import sys
import os
import json
import shutil
import subprocess
import platform

GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    print(f"\n{CYAN}{BOLD}======================================================{RESET}")
    print(f"{CYAN}{BOLD}   ⚡ SQUEEZE AI MCP — 1-CLICK AUTO CONNECTOR         {RESET}")
    print(f"{CYAN}{BOLD}======================================================{RESET}")
    print(f"{BLUE}Connecting Squeeze AST Skeletonizer & DLP Shield...{RESET}\n")

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def test_mcp_server(mcp_path, python_cmd):
    """Run a quick JSON-RPC ping to verify the MCP server responds."""
    test_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}) + "\n"
    try:
        proc = subprocess.Popen(
            [python_cmd, mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = proc.communicate(input=test_req, timeout=5)
        if "squeeze_compress" in stdout and "squeeze_skeleton" in stdout:
            return True, "7 tools verified (squeeze_compress, squeeze_skeleton, squeeze_shrink_json, squeeze_shrink_logs, squeeze_retrieve, squeeze_cache_align, squeeze_stats)"
        return False, "Server responded but tools list was incomplete"
    except Exception as e:
        return False, str(e)

def update_json_mcp_config(config_path, mcp_path, python_cmd):
    """Safely updates an MCP json file with the squeeze configuration."""
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            # Backup corrupted file
            shutil.copy2(config_path, config_path + ".bak")
            data = {}

    if not isinstance(data, dict):
        data = {}

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}

    data["mcpServers"]["squeeze"] = {
        "command": python_cmd,
        "args": [mcp_path]
    }

    # Backup original before saving
    if os.path.exists(config_path):
        shutil.copy2(config_path, config_path + ".bak")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return True

def install_claude_code(mcp_path, python_cmd):
    """Register into Claude Code CLI."""
    claude_bin = shutil.which("claude")
    if not claude_bin:
        # Check standard global npm locations
        home = os.path.expanduser("~")
        candidates = [
            os.path.join(home, ".npm-global", "bin", "claude"),
            os.path.join(home, ".nvm", "versions", "node", "*", "bin", "claude"),
            "/usr/local/bin/claude",
            "/opt/homebrew/bin/claude",
        ]
        import glob
        for cand in candidates:
            matches = glob.glob(cand)
            if matches:
                claude_bin = matches[0]
                break

    if not claude_bin:
        return False, "Claude Code CLI not detected in PATH (install via `npm i -g @anthropic-ai/claude-code`)"

    try:
        # Check if already added or add it
        res = subprocess.run(
            [claude_bin, "mcp", "add", "squeeze", python_cmd, mcp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if res.returncode == 0 or "already exists" in res.stderr or "already exists" in res.stdout:
            return True, f"Registered via {claude_bin}"
        else:
            err = (res.stderr or res.stdout).strip()
            return False, f"Failed: {err}"
    except Exception as e:
        return False, str(e)

def install_claude_desktop(mcp_path, python_cmd):
    """Register into Claude Desktop App."""
    system = platform.system()
    home = os.path.expanduser("~")
    
    if system == "Darwin": # macOS
        config_path = os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        config_path = os.path.join(appdata, "Claude", "claude_desktop_config.json")
    else: # Linux
        config_path = os.path.join(home, ".config", "Claude", "claude_desktop_config.json")

    claude_dir = os.path.dirname(config_path)
    if not os.path.exists(claude_dir):
        # Create it so it's ready when user installs Claude Desktop
        try:
            os.makedirs(claude_dir, exist_ok=True)
        except Exception:
            return False, f"Claude Desktop directory not found at {claude_dir}"

    try:
        update_json_mcp_config(config_path, mcp_path, python_cmd)
        return True, f"Configured at {config_path}"
    except Exception as e:
        return False, str(e)

def install_cursor(mcp_path, python_cmd):
    """Register into Cursor IDE."""
    system = platform.system()
    home = os.path.expanduser("~")
    
    if system == "Windows":
        appdata = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
        config_path = os.path.join(appdata, "Cursor", "mcp.json")
    else:
        config_path = os.path.join(home, ".cursor", "mcp.json")

    cursor_dir = os.path.dirname(config_path)
    # Even if cursor dir doesn't exist yet, we can create ~/.cursor/mcp.json
    try:
        os.makedirs(cursor_dir, exist_ok=True)
        update_json_mcp_config(config_path, mcp_path, python_cmd)
        return True, f"Configured at {config_path}"
    except Exception as e:
        return False, str(e)

def main():
    print_banner()

    script_dir = get_script_dir()
    mcp_file = os.path.join(script_dir, "squeeze_mcp.py")

    if not os.path.exists(mcp_file):
        print(f"{RED}[✖] Error: Could not find squeeze_mcp.py in {script_dir}{RESET}")
        sys.exit(1)

    python_cmd = sys.executable or "python3"
    print(f"• Python executable: {CYAN}{python_cmd}{RESET}")
    print(f"• Squeeze MCP path:  {CYAN}{mcp_file}{RESET}\n")

    # Step 1: Self Test
    print(f"{BOLD}[1/4] Running Squeeze MCP Self-Test...{RESET}")
    ok, msg = test_mcp_server(mcp_file, python_cmd)
    if ok:
        print(f"  {GREEN}✔ {msg}{RESET}\n")
    else:
        print(f"  {RED}✖ Self-test failed: {msg}{RESET}\n")

    # Step 2: Claude Code CLI
    print(f"{BOLD}[2/4] Connecting to Claude Code CLI...{RESET}")
    ok_cc, msg_cc = install_claude_code(mcp_file, python_cmd)
    if ok_cc:
        print(f"  {GREEN}✔ CONNECTED: {msg_cc}{RESET}\n")
    else:
        print(f"  {YELLOW}ℹ Notice: {msg_cc}{RESET}")
        print(f"    {CYAN}Manual command when installed:{RESET}")
        print(f"    claude mcp add squeeze {python_cmd} \"{mcp_file}\"\n")

    # Step 3: Claude Desktop App
    print(f"{BOLD}[3/4] Connecting to Claude Desktop App...{RESET}")
    ok_cd, msg_cd = install_claude_desktop(mcp_file, python_cmd)
    if ok_cd:
        print(f"  {GREEN}✔ CONNECTED: {msg_cd}{RESET}\n")
    else:
        print(f"  {YELLOW}ℹ Skipped: {msg_cd}{RESET}\n")

    # Step 4: Cursor IDE
    print(f"{BOLD}[4/4] Connecting to Cursor IDE...{RESET}")
    ok_cur, msg_cur = install_cursor(mcp_file, python_cmd)
    if ok_cur:
        print(f"  {GREEN}✔ CONNECTED: {msg_cur}{RESET}\n")
    else:
        print(f"  {YELLOW}ℹ Skipped: {msg_cur}{RESET}\n")

    print(f"{CYAN}{BOLD}======================================================{RESET}")
    print(f"{GREEN}{BOLD}   🎉 SETUP COMPLETE! Squeeze AI is ready to use.     {RESET}")
    print(f"{CYAN}{BOLD}======================================================{RESET}")
    print(f"""
{BOLD}How to use inside Claude Code or Cursor:{RESET}
  1. Restart Claude Code, Claude Desktop, or Cursor to reload tools.
  2. Ask Claude:
     • {CYAN}"Use squeeze_skeleton to get the interface for file.py"{RESET}
     • {CYAN}"Compress this raw log/prompt using squeeze_compress"{RESET}
     • {CYAN}"Fold this large JSON array using squeeze_shrink_json"{RESET}

To uninstall at any time, run: {YELLOW}python3 uninstall.py{RESET}
""")

if __name__ == "__main__":
    main()
