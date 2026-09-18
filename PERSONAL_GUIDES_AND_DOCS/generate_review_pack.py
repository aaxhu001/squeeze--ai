import os

OUTPUT_FILE = "/Users/aashu/Aashu/Squeeze/SQUEEZE_CODEBASE_PACK.md"

CORE_FILES = [
    ("manifest.json", "json"),
    ("skeletonizer.js", "javascript"),
    ("squeeze_mcp.py", "python"),
    ("background.js", "javascript"),
    ("content.js", "javascript"),
    ("sidepanel.js", "javascript"),
    ("sidepanel.html", "html"),
    ("popup.js", "javascript"),
    ("popup.html", "html")
]

def generate_pack():
    content = []
    content.append("# SQUEEZE AI — Complete Codebase & Architectural Review Pack\n")
    content.append("> **Project Overview:** Squeeze AI is a zero-latency, 100% private client-side token optimizer and context intelligence layer for Claude, ChatGPT, Gemini, and IDE assistants (Cursor, Claude Code).\n\n")
    content.append("## Core Value Metrics\n")
    content.append("- **Prompt Token Reduction:** 25% – 70%\n")
    content.append("- **AST Code Skeletonization:** 70% – 90% code token reduction\n")
    content.append("- **Content-Aware JSON Folding:** 88% token reduction on API responses\n")
    content.append("- **Provider CacheAligner™:** Locks 90% prompt-cache discounts on Anthropic & OpenAI\n")
    content.append("- **DLP Secret Shield:** Real-time in-memory masking for 8 credential types\n")
    content.append("- **Protocol Support:** Chrome Extension (MV3) + Model Context Protocol (MCP) Server\n\n")
    content.append("---\n\n")

    for filename, lang in CORE_FILES:
        filepath = os.path.join("/Users/aashu/Aashu/Squeeze", filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
            content.append(f"## File: `{filename}`\n")
            content.append(f"```{lang}\n{code}\n```\n\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("".join(content))

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"✅ Generated {OUTPUT_FILE} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    generate_pack()
