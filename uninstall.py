#!/usr/bin/env python3
"""
Squeeze AI — 1-Click MCP Uninstaller
Cleanly removes Squeeze AI MCP from Claude Code, Claude Desktop, and Cursor.
"""

import sys
import os
import json
import shutil
import subprocess
import platform

GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def remove_from_json(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "mcpServers" in data and "squeeze" in data["mcpServers"]:
            del data["mcpServers"]["squeeze"]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
    except Exception:
        pass
    return False

def main():
    print(f"\n{CYAN}{BOLD}--- Squeeze AI MCP Uninstaller ---{RESET}\n")

    # 1. Claude Code
    claude_bin = shutil.which("claude")
    if claude_bin:
        try:
            res = subprocess.run([claude_bin, "mcp", "remove", "squeeze"], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"  {GREEN}✔ Removed from Claude Code CLI{RESET}")
        except Exception:
            pass

    # 2. Claude Desktop
    system = platform.system()
    home = os.path.expanduser("~")
    if system == "Darwin":
        cd_path = os.path.join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
    elif system == "Windows":
        cd_path = os.path.join(os.environ.get("APPDATA", home), "Claude", "claude_desktop_config.json")
    else:
        cd_path = os.path.join(home, ".config", "Claude", "claude_desktop_config.json")

    if remove_from_json(cd_path):
        print(f"  {GREEN}✔ Removed from Claude Desktop ({cd_path}){RESET}")

    # 3. Cursor
    if system == "Windows":
        cur_path = os.path.join(os.environ.get("APPDATA", home), "Cursor", "mcp.json")
    else:
        cur_path = os.path.join(home, ".cursor", "mcp.json")

    if remove_from_json(cur_path):
        print(f"  {GREEN}✔ Removed from Cursor ({cur_path}){RESET}")

    # 4. Google Antigravity
    agy_path = os.path.join(home, ".gemini", "config", "mcp_config.json")
    if remove_from_json(agy_path):
        print(f"  {GREEN}✔ Removed from Google Antigravity ({agy_path}){RESET}")

    print(f"\n{GREEN}✔ Squeeze AI MCP successfully uninstalled.{RESET}\n")

if __name__ == "__main__":
    main()
