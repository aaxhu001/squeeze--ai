# ⚡ Squeeze AI — Model Context Protocol (MCP) Server

Connect Squeeze AI's **AST Code Skeletonizer**, **DLP Secret Masker**, and **Context Compression** directly into **Claude Code**, **Claude Desktop**, and **Cursor IDE**.

---

### 🚀 Option 1: 1-Click Auto Install (Recommended)

Simply open your terminal in this folder and run:
```bash
python3 install.py
```
*(Or on Mac/Linux, double-click `install.sh` / on Windows double-click `install.bat`)*

**What it does automatically:**
- Auto-detects **Claude Code CLI** and runs `claude mcp add squeeze`
- Auto-detects **Claude Desktop** and configures `claude_desktop_config.json`
- Auto-detects **Cursor IDE** and configures `~/.cursor/mcp.json`
- Runs a self-test to verify all 4 Squeeze tools are ready

---

### 💻 Option 2: Manual 1-Line Setup

If you prefer to add it manually:

#### For Claude Code CLI:
```bash
claude mcp add squeeze python3 "$(pwd)/squeeze_mcp.py"
```

#### For Claude Desktop App:
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Win):
```json
{
  "mcpServers": {
    "squeeze": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/squeeze_mcp.py"]
    }
  }
}
```

#### For Cursor IDE:
Add to `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "squeeze": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/squeeze_mcp.py"]
    }
  }
}
```

---

### 🧪 How to Test Inside Claude Code / Claude Desktop / Cursor

Ask your AI assistant:
1. **AST Code Skeletonizer:**  
   > "Use `squeeze_skeleton` to get the interface skeleton of my codebase files."  
   *(Cuts 80% tokens by collapsing function bodies while keeping signatures and type annotations)*

2. **DLP Secret Masker & Compression:**  
   > "Use `squeeze_compress` on this prompt: 'Hi, kindly help with MONGO_URI=mongodb://admin:pass123@cluster.com/db' "  
   *(Redacts secrets before transmission and strips conversational fluff)*

3. **JSON Array Folding:**  
   > "Use `squeeze_shrink_json` on this 500-line API response to fold repetitive arrays."

---

### 🗑️ To Uninstall
Run:
```bash
python3 uninstall.py
```
