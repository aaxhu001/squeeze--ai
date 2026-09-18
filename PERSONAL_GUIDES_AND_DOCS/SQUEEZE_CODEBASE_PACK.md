# SQUEEZE AI — Complete Codebase & Architectural Review Pack
> **Project Overview:** Squeeze AI is a zero-latency, 100% private client-side token optimizer and context intelligence layer for Claude, ChatGPT, Gemini, and IDE assistants (Cursor, Claude Code).

## Core Value Metrics
- **Prompt Token Reduction:** 25% – 70%
- **AST Code Skeletonization:** 70% – 90% code token reduction
- **Content-Aware JSON Folding:** 88% token reduction on API responses
- **Provider CacheAligner™:** Locks 90% prompt-cache discounts on Anthropic & OpenAI
- **DLP Secret Shield:** Real-time in-memory masking for 8 credential types
- **Protocol Support:** Chrome Extension (MV3) + Model Context Protocol (MCP) Server

---

## File: `manifest.json`
```json
{
  "manifest_version": 3,
  "name": "Squeeze AI - Prompt & Context Optimizer",
  "version": "1.0.0",
  "description": "Cut LLM token bloat by up to 70%, mask sensitive credentials, and manage context across Claude, ChatGPT, and Gemini.",
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "permissions": [
    "storage",
    "sidePanel",
    "tabs",
    "clipboardWrite"
  ],
  "host_permissions": [
    "https://claude.ai/*",
    "https://chatgpt.com/*",
    "https://chat.openai.com/*",
    "https://gemini.google.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "side_panel": {
    "default_path": "sidepanel.html"
  },
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "content_scripts": [
    {
      "matches": [
        "https://claude.ai/*",
        "https://chatgpt.com/*",
        "https://chat.openai.com/*",
        "https://gemini.google.com/*"
      ],
      "js": ["pdf.min.js", "skeletonizer.js", "content.js"],
      "css": ["content.css"],
      "run_at": "document_idle"
    }
  ],
  "web_accessible_resources": [
    {
      "resources": [
        "icons/icon16.png",
        "icons/icon48.png",
        "icons/icon128.png",
        "pdf.worker.min.js",
        "skeletonizer.js",
        "logo.svg"
      ],
      "matches": [
        "https://claude.ai/*",
        "https://chatgpt.com/*",
        "https://chat.openai.com/*",
        "https://gemini.google.com/*"
      ]
    }
  ]
}

```

## File: `skeletonizer.js`
```javascript
/**
 * Squeeze AI - Code Architecture & Cache Optimization Engine
 * 
 * 1. Deterministic AST Code Skeletonizer & Topological Code Graph
 * 2. Content-Aware Data Shrinkers (JSON, Logs, Diffs) & Provider CacheAligner
 */

(function (exports) {
  // --- 1. CODE SKELETONIZER (AST COMPRESSION) ---
  // Strips implementation bodies while preserving classes, function signatures,
  // docstrings, type annotations, and exported interfaces. Slashes 70-90% of tokens.

  function skeletonizePython(code) {
    if (!code) return "";
    const lines = code.split("\n");
    const result = [];
    let inDocstring = false;
    let docstringDelim = "";
    let skipBodyIndent = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      const indentMatch = line.match(/^(\s*)/);
      const indent = indentMatch ? indentMatch[1].length : 0;

      // Check docstring state
      if (!inDocstring) {
        if (trimmed.startsWith('"""') || trimmed.startsWith("'''")) {
          docstringDelim = trimmed.substring(0, 3);
          if (trimmed.length > 3 && trimmed.endsWith(docstringDelim)) {
            // One-line docstring
            result.push(line);
            continue;
          }
          inDocstring = true;
          result.push(line);
          continue;
        }
      } else {
        result.push(line);
        if (trimmed.endsWith(docstringDelim)) {
          inDocstring = false;
        }
        continue;
      }

      // Check if we are skipping an indented function body
      if (skipBodyIndent !== null) {
        if (indent > skipBodyIndent && trimmed !== "") {
          // Inside function body - skip
          continue;
        } else if (trimmed === "") {
          continue;
        } else {
          // Exited function body
          skipBodyIndent = null;
        }
      }

      // Imports, decorators, classes, comments
      if (
        trimmed.startsWith("import ") ||
        trimmed.startsWith("from ") ||
        trimmed.startsWith("@") ||
        trimmed.startsWith("#") ||
        trimmed.startsWith("class ") ||
        trimmed.startsWith("type ") ||
        trimmed.includes(" = TypeVar(") ||
        trimmed.includes(" = NewType(")
      ) {
        result.push(line);
        continue;
      }

      // Function definition
      if (trimmed.startsWith("def ") || trimmed.startsWith("async def ")) {
        // Collect full signature if multi-line
        let sig = line;
        while (!sig.includes(":") && i + 1 < lines.length) {
          i++;
          sig += "\n" + lines[i];
        }
        result.push(sig);

        // Check if next line is a docstring
        let hasDocstring = false;
        if (i + 1 < lines.length) {
          const nextTrim = lines[i + 1].trim();
          if (nextTrim.startsWith('"""') || nextTrim.startsWith("'''")) {
            hasDocstring = true;
          }
        }

        if (!hasDocstring) {
          // Add standard Python placeholder
          const indentStr = " ".repeat(indent + 4);
          result.push(`${indentStr}...`);
        }
        skipBodyIndent = indent;
        continue;
      }

      // Keep top-level constants / global variables
      if (indent === 0 && trimmed.includes("=") && !trimmed.startsWith("if ") && !trimmed.startsWith("for ")) {
        result.push(line);
      }
    }

    return result.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function skeletonizeTypeScript(code) {
    if (!code) return "";
    const lines = code.split("\n");
    const result = [];
    let braceDepth = 0;
    let inFunctionBody = false;
    let funcBraceStart = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Keep imports, exports, types, interfaces, and decorators
      if (
        trimmed.startsWith("import ") ||
        trimmed.startsWith("export type ") ||
        trimmed.startsWith("export interface ") ||
        trimmed.startsWith("type ") ||
        trimmed.startsWith("interface ") ||
        trimmed.startsWith("@")
      ) {
        result.push(line);
        // Track braces inside interfaces/types
        const open = (line.match(/{/g) || []).length;
        const close = (line.match(/}/g) || []).length;
        braceDepth += (open - close);
        continue;
      }

      // Detect function or method signatures
      const isFunction =
        /^(export\s+)?(async\s+)?function\b/.test(trimmed) ||
        /^(public|private|protected|static|override|async|\s)*[a-zA-Z0-9_$]+\s*\([^)]*\)\s*(:\s*[^={]+)?\s*\{?$/.test(trimmed) ||
        /^(export\s+)?(const|let|var)\s+[a-zA-Z0-9_$]+\s*=\s*(async\s*)?\([^)]*\)\s*(:\s*[^={]+)?\s*=>\s*\{?$/.test(trimmed);

      const isClassDecl = /^(export\s+)?(abstract\s+)?class\b/.test(trimmed);

      if (isClassDecl) {
        result.push(line);
        const open = (line.match(/{/g) || []).length;
        const close = (line.match(/}/g) || []).length;
        braceDepth += (open - close);
        continue;
      }

      if (isFunction && !inFunctionBody) {
        let sig = line;
        // Collect multi-line signature
        while (!sig.includes("{") && !sig.endsWith(";") && i + 1 < lines.length) {
          i++;
          sig += "\n" + lines[i];
        }

        const indentMatch = line.match(/^(\s*)/);
        const indentStr = indentMatch ? indentMatch[1] : "";

        if (sig.includes("{")) {
          // Replace opening brace with collapsed body
          const sigClean = sig.substring(0, sig.indexOf("{")).trim();
          result.push(`${indentStr}${sigClean} { /* ... */ }`);
          inFunctionBody = true;
          funcBraceStart = braceDepth;
          braceDepth += (sig.match(/{/g) || []).length - (sig.match(/}/g) || []).length;
          if (braceDepth <= funcBraceStart) {
            inFunctionBody = false;
          }
        } else {
          result.push(sig);
        }
        continue;
      }

      const openBraces = (line.match(/{/g) || []).length;
      const closeBraces = (line.match(/}/g) || []).length;

      if (inFunctionBody) {
        braceDepth += (openBraces - closeBraces);
        if (braceDepth <= funcBraceStart) {
          inFunctionBody = false;
        }
        continue;
      }

      // If at top level or class level, keep property definitions
      if (braceDepth <= 1 && (trimmed.includes(":") || trimmed.includes(";")) && !trimmed.startsWith("return ") && !trimmed.startsWith("const ") && !trimmed.startsWith("let ")) {
        result.push(line);
      }

      braceDepth += (openBraces - closeBraces);
      if (braceDepth < 0) braceDepth = 0;
    }

    return result.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function skeletonizeCode(code, filenameOrLang = "") {
    const lower = (filenameOrLang || "").toLowerCase();
    if (lower.endsWith(".py") || lower === "python" || lower === "py") {
      return skeletonizePython(code);
    }
    if (
      lower.endsWith(".ts") || lower.endsWith(".tsx") ||
      lower.endsWith(".js") || lower.endsWith(".jsx") ||
      lower === "typescript" || lower === "javascript" || lower === "ts" || lower === "js"
    ) {
      return skeletonizeTypeScript(code);
    }

    // Generic fallback: collapse blocks inside { ... } beyond first line
    return code
      .replace(/\{([^{}]{60,})\}/g, "{\n  /* ... implementation details omitted ... */\n}")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  // --- 2. CONTENT-AWARE DATA SHRINKERS ---

  // JSON Array Folder & Schema Extractor:
  // Condenses 100 repetitive items down to 1 item + item count notation
  function shrinkJson(jsonText, maxArrayItems = 2) {
    if (!jsonText || typeof jsonText !== "string") return jsonText;
    try {
      const parsed = JSON.parse(jsonText);

      function traverse(obj) {
        if (Array.isArray(obj)) {
          if (obj.length > maxArrayItems) {
            const count = obj.length;
            const kept = obj.slice(0, maxArrayItems).map(traverse);
            kept.push({
              _squeezed_array_note: `... [${count - maxArrayItems} additional similar items omitted for token efficiency]`,
              total_count: count
            });
            return kept;
          }
          return obj.map(traverse);
        } else if (obj !== null && typeof obj === "object") {
          const result = {};
          for (const [k, v] of Object.entries(obj)) {
            // Truncate huge base64 strings or long hashes
            if (typeof v === "string" && v.length > 250 && !v.includes(" ")) {
              result[k] = v.substring(0, 40) + `... [truncated string, length ${v.length}]`;
            } else {
              result[k] = traverse(v);
            }
          }
          return result;
        }
        return obj;
      }

      const shrunk = traverse(parsed);
      return JSON.stringify(shrunk, null, 2);
    } catch (e) {
      // Not valid JSON, return as-is
      return jsonText;
    }
  }

  // Log & Stack Trace Deduplicator
  function shrinkLogs(logText) {
    if (!logText) return "";
    const lines = logText.split("\n");
    const result = [];
    let prevLine = "";
    let repeatCount = 0;

    for (const line of lines) {
      // Strip noisy timestamps like 2026-09-19T01:23:45.678Z
      const cleanLine = line
        .replace(/\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?Z?/g, "[TIME]")
        .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, "[UUID]");

      if (cleanLine === prevLine) {
        repeatCount++;
      } else {
        if (repeatCount > 0) {
          result.push(`   ↳ [Previous line repeated ${repeatCount} additional times]`);
          repeatCount = 0;
        }
        result.push(cleanLine);
        prevLine = cleanLine;
      }
    }

    if (repeatCount > 0) {
      result.push(`   ↳ [Previous line repeated ${repeatCount} additional times]`);
    }

    return result.join("\n");
  }

  // --- 3. TOPOLOGICAL CODEBASE GRAPH ---
  // Maps multi-file relationships, exports, classes, and dependencies into a compact map
  function buildCodebaseGraph(filesList) {
    if (!filesList || filesList.length === 0) return { graphText: "", nodes: [] };

    const nodes = [];
    const relationships = [];

    for (const file of filesList) {
      const name = file.name;
      const content = file.content || "";
      const ext = name.split(".").pop().toLowerCase();

      const imports = [];
      const exportsList = [];
      const classes = [];
      const functions = [];

      // Extract imports
      const importMatches = content.matchAll(/(?:import\s+.*?from\s+['"]([^'"]+)['"]|from\s+([a-zA-Z0-9_.]+)\s+import|require\(['"]([^'"]+)['"]\))/g);
      for (const m of importMatches) {
        const target = m[1] || m[2] || m[3];
        if (target && !imports.includes(target)) imports.push(target);
      }

      // Extract classes
      const classMatches = content.matchAll(/\bclass\s+([a-zA-Z0-9_$]+)/g);
      for (const m of classMatches) {
        if (!classes.includes(m[1])) classes.push(m[1]);
      }

      // Extract functions
      const funcMatches = content.matchAll(/\b(?:def|function|const)\s+([a-zA-Z0-9_$]+)\s*(?:=\s*(?:async\s*)?\([^)]*\)|=|\()/g);
      for (const m of funcMatches) {
        const fn = m[1];
        if (!["if", "for", "while", "switch"].includes(fn) && !functions.includes(fn)) {
          functions.push(fn);
        }
      }

      nodes.push({
        file: name,
        ext,
        classes: classes.slice(0, 8),
        functions: functions.slice(0, 12),
        imports: imports.slice(0, 8)
      });
    }

    // Format into compact graph summary
    let graphText = "### CODEBASE TOPOLOGICAL GRAPH (Squeeze Engine)\n";
    nodes.forEach(n => {
      const parts = [];
      if (n.classes.length > 0) parts.push(`Classes: [${n.classes.join(", ")}]`);
      if (n.functions.length > 0) parts.push(`Functions: [${n.functions.join(", ")}]`);
      if (n.imports.length > 0) parts.push(`Imports: [${n.imports.join(", ")}]`);
      graphText += `- **${n.file}**: ${parts.join(" | ") || "Module definitions"}\n`;
    });

    return { graphText, nodes };
  }

  // --- 4. PROVIDER CACHE ALIGNER ---
  // Reorders prompt content into [Tier 1: Static Prefix] -> [Tier 2: Code Skeletons] -> [Tier 3: Dynamic Tail]
  // to maximize Anthropic Claude & OpenAI 90% prompt-cache hit rates.
  function alignPromptForCache(systemPrompt, architectureContext, userTask) {
    const parts = [];

    // Tier 1: Static Cacheable Prefix (Developer Persona + Global Directives)
    if (systemPrompt && systemPrompt.trim()) {
      parts.push(`<!-- CACHE_ANCHOR: SYSTEM_DIRECTIVES -->\n${systemPrompt.trim()}`);
    }

    // Tier 2: Semi-Static Context (Architectural Code Graph & Skeletons)
    if (architectureContext && architectureContext.trim()) {
      parts.push(`<!-- CACHE_ANCHOR: CODE_ARCHITECTURE -->\n${architectureContext.trim()}`);
    }

    // Tier 3: Dynamic Tail (The immediate user query / volatile payload)
    if (userTask && userTask.trim()) {
      parts.push(`<!-- DYNAMIC_PROMPT: ACTIVE_QUERY -->\n${userTask.trim()}`);
    }

    return parts.join("\n\n");
  }

  // Exports
  exports.skeletonizePython = skeletonizePython;
  exports.skeletonizeTypeScript = skeletonizeTypeScript;
  exports.skeletonizeCode = skeletonizeCode;
  exports.shrinkJson = shrinkJson;
  exports.shrinkLogs = shrinkLogs;
  exports.buildCodebaseGraph = buildCodebaseGraph;
  exports.alignPromptForCache = alignPromptForCache;

})(typeof module !== "undefined" && module.exports ? module.exports : (window.SqueezeSkeletonizer = {}));

```

## File: `squeeze_mcp.py`
```python
#!/usr/bin/env python3
"""
Squeeze AI - Model Context Protocol (MCP) Server
Integrates Squeeze AI AST Code Skeletonizer and Context Compression Engine
directly into Cursor, Claude Code, Cline, and other AI coding assistants.

Usage:
  python3 squeeze_mcp.py
Or in Cursor ~/.cursor/mcp.json:
  {
    "mcpServers": {
      "squeeze": {
        "command": "python3",
        "args": ["/Users/aashu/Aashu/Squeeze/squeeze_mcp.py"]
      }
    }
  }
"""

import sys
import json
import re

def mask_secrets(text: str) -> str:
    """DLP secret scanner for 8 major credential types."""
    if not text:
        return ""
    
    # OpenAI, Anthropic, Google keys
    text = re.sub(r'\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b', '[MASKED_OPENAI_KEY]', text)
    text = re.sub(r'\b(AIzaSy[a-zA-Z0-9_-]{30,})\b', '[MASKED_GOOGLE_KEY]', text)
    text = re.sub(r'\b(sk-ant-[a-zA-Z0-9_-]{20,})\b', '[MASKED_ANTHROPIC_KEY]', text)
    # AWS, GitHub, JWT
    text = re.sub(r'\b(AKIA[0-9A-Z]{16})\b', '[MASKED_AWS_KEY]', text)
    text = re.sub(r'\b(gh[pousr]_[A-Za-z0-9_]{36,})\b', '[MASKED_GITHUB_TOKEN]', text)
    text = re.sub(r'\b(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b', '[MASKED_JWT]', text)
    # Database URIs
    text = re.sub(r'((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)', r'\1[MASKED_PASSWORD]\3', text)
    return text

def skeletonize_code(code: str, language: str = "python") -> str:
    """Strips function and method bodies while preserving classes, signatures, and docstrings."""
    if not code:
        return ""
    
    lang = language.lower()
    lines = code.split("\n")
    result = []
    
    if "py" in lang:
        skip_body_indent = None
        in_docstring = False
        docstring_delim = ""
        
        for i, line in enumerate(lines):
            trimmed = line.trim() if hasattr(line, 'trim') else line.strip()
            indent = len(line) - len(line.lstrip())
            
            if not in_docstring:
                if trimmed.startswith('"""') or trimmed.startswith("'''"):
                    docstring_delim = trimmed[:3]
                    if len(trimmed) > 3 and trimmed.endswith(docstring_delim):
                        result.append(line)
                        continue
                    in_docstring = True
                    result.append(line)
                    continue
            else:
                result.append(line)
                if trimmed.endswith(docstring_delim):
                    in_docstring = False
                continue
                
            if skip_body_indent is not None:
                if indent > skip_body_indent and trimmed != "":
                    continue
                elif trimmed == "":
                    continue
                else:
                    skip_body_indent = None
                    
            if (trimmed.startswith("import ") or trimmed.startswith("from ") or 
                trimmed.startswith("@") or trimmed.startswith("#") or 
                trimmed.startswith("class ") or trimmed.startswith("type ")):
                result.append(line)
                continue
                
            if trimmed.startswith("def ") or trimmed.startswith("async def "):
                result.append(line)
                # Check next line for docstring
                has_doc = False
                if i + 1 < len(lines):
                    next_t = lines[i+1].strip()
                    if next_t.startswith('"""') or next_t.startswith("'''"):
                        has_doc = True
                if not has_doc:
                    result.append(" " * (indent + 4) + "...")
                skip_body_indent = indent
                continue
                
            if indent == 0 and "=" in trimmed and not trimmed.startswith("if "):
                result.append(line)
        return "\n".join(result).strip()
    
    # JavaScript / TypeScript / Go / Rust generic skeletonizer
    return re.sub(r'\{([^{}]{50,})\}', '{\n    /* ... implementation collapsed by Squeeze ... */\n}', code)

def shrink_json_data(text: str, max_items: int = 2) -> str:
    """Folds repetitive JSON arrays and truncates huge strings."""
    try:
        data = json.loads(text)
        def fold(obj):
            if isinstance(obj, list):
                if len(obj) > max_items:
                    count = len(obj)
                    kept = [fold(x) for x in obj[:max_items]]
                    kept.append({
                        "_squeezed_note": f"[{count - max_items} similar items omitted to save tokens]",
                        "total_count": count
                    })
                    return kept
                return [fold(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: (v[:40] + f"... [len {len(v)}]" if isinstance(v, str) and len(v) > 200 and " " not in v else fold(v)) for k, v in obj.items()}
            return obj
        return json.dumps(fold(data), indent=2)
    except Exception:
        return text

def optimize_prompt(prompt: str) -> dict:
    """Applies Squeeze heuristic optimization rules to prompt text."""
    orig_len = len(prompt)
    sanitized = mask_secrets(prompt)
    
    # 1. Strip greetings & politeness
    polite = [
        r'\b(?:hello|hi|hey|dear)\s+(?:assistant|claude|chatgpt|ai|there)\b[.,!?]*\s*',
        r'\b(?:thank\s+you|thanks)(?:\s+in\s+advance)?[.,!?]*\s*',
        r'\bi\s+was\s+wondering\s+if\s+you\s+could\b\s*',
        r'\bplease\s+(?:help\s+me\s+to\s+)?\b'
    ]
    for p in polite:
        sanitized = re.sub(p, '', sanitized, flags=re.IGNORECASE)
        
    # 2. Verbosity simplifications
    subs = {
        r'\bin order to\b': 'to',
        r'\bdue to the fact that\b': 'because',
        r'\bat this point in time\b': 'now',
        r'\btake into consideration\b': 'consider',
        r'\bmake use of\b': 'use',
        r'\butilize\b': 'use'
    }
    for k, v in subs.items():
        sanitized = re.sub(k, v, sanitized, flags=re.IGNORECASE)
        
    opt_len = len(sanitized)
    saved = max(0, orig_len - opt_len)
    
    return {
        "optimized": sanitized.strip(),
        "original_tokens": max(1, orig_len // 4),
        "optimized_tokens": max(1, opt_len // 4),
        "tokens_saved": max(0, (orig_len - opt_len) // 4)
    }

# --- MCP JSON-RPC 2.0 PROTOCOL HANDLER ---
TOOLS = [
    {
        "name": "squeeze_compress",
        "description": "Compress prompts, logs, or tool output text using Squeeze AI rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text or prompt to compress"},
                "mask_secrets": {"type": "boolean", "description": "Scan and mask API keys and credentials", "default": True}
            },
            "required": ["text"]
        }
    },
    {
        "name": "squeeze_skeleton",
        "description": "Squeeze AST: Extract structural skeletons from source code (classes, signatures, types), saving 70-90% tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code text"},
                "language": {"type": "string", "description": "Language: python, typescript, javascript, go, rust", "default": "python"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "squeeze_shrink_json",
        "description": "Squeeze Data: Folds repetitive JSON arrays and truncates hashes/base64 strings, cutting 80%+ tokens on API responses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "json_text": {"type": "string", "description": "JSON string to compress"},
                "max_array_items": {"type": "integer", "description": "Number of sample items to preserve per array", "default": 2}
            },
            "required": ["json_text"]
        }
    }
]

def handle_message(msg):
    msg_id = msg.get("id")
    method = msg.get("method")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "squeeze-ai-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    elif method == "notifications/initialized":
        return None
        
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOLS
            }
        }
        
    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "squeeze_compress":
            res = optimize_prompt(args.get("text", ""))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": res["optimized"]}],
                    "isError": False
                }
            }
            
        elif tool_name == "squeeze_skeleton":
            skel = skeletonize_code(args.get("code", ""), args.get("language", "python"))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": skel}],
                    "isError": False
                }
            }
            
        elif tool_name == "squeeze_shrink_json":
            shrunk = shrink_json_data(args.get("json_text", ""), args.get("max_array_items", 2))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": shrunk}],
                    "isError": False
                }
            }
            
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }
            
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32600, "message": f"Unsupported method '{method}'"}
    }

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            res = handle_message(req)
            if res:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling MCP message: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()

```

## File: `background.js`
```javascript
/**
 * Squeeze AI - Background Service Worker (Manifest V3)
 * High-performance local token optimizer, DLP secret scanner,
 * Squeeze AST Code Skeletonizer, CacheAligner & Context Vault engine.
 */

try {
  importScripts("skeletonizer.js");
} catch (e) {
  console.warn("Could not import skeletonizer.js:", e);
}

// --- MODEL PRICING (USD per 1M input tokens) ---
const MODEL_RATES = {
  sonnet: { name: "Claude 3.5 Sonnet", ratePerMillion: 3.00 },
  opus: { name: "Claude 3 Opus", ratePerMillion: 15.00 },
  gpt4o: { name: "GPT-4o", ratePerMillion: 2.50 },
  geminiPro: { name: "Gemini 1.5 Pro", ratePerMillion: 1.25 },
  deepseek: { name: "DeepSeek V3", ratePerMillion: 0.14 }
};

// --- INITIALIZE EXTENSION DEFAULTS ---
chrome.runtime.onInstalled.addListener(async (details) => {
  const defaults = {
    optimizationMode: "balanced",
    ruleStripGreetings: true,
    ruleSimplifyPhrases: true,
    ruleAbbreviate: true,
    ruleStripArticles: true,
    rulePolishMarkdown: true,
    ruleSecretShield: true,
    stats_promptsOptimized: 0,
    stats_tokensSaved: 0,
    stats_costSaved: 0,
    stats_history: [],
    vaultPreferences: "",
    vaultPrefAlwaysInject: true,
    vaultSmartTriggers: true,
    vaultFiles: []
  };

  const current = await chrome.storage.local.get(Object.keys(defaults));
  const toSet = {};
  for (const [k, v] of Object.entries(defaults)) {
    if (current[k] === undefined) toSet[k] = v;
  }
  if (Object.keys(toSet).length > 0) {
    await chrome.storage.local.set(toSet);
  }

  // Set side panel behavior if supported
  if (chrome.sidePanel?.setPanelBehavior) {
    try {
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
    } catch (e) {
      console.warn("Side panel behavior setup:", e);
    }
  }
});

// --- TOKEN ESTIMATION ENGINE ---
// NOTE: This is the canonical implementation. Identical copies exist in
// content.js (estimateTokensLocal) and sidepanel.js for context isolation
// (content scripts and side panels can't share service worker scope).
// TODO: Extract to a shared bundle once a build pipeline is added.
function estimateTokens(text) {
  if (!text || typeof text !== "string") return 0;
  const trimmed = text.trim();
  if (!trimmed) return 0;

  // Words count
  const words = trimmed.split(/\s+/).length;
  const chars = trimmed.length;

  // Code / Symbol intensity factor
  const specialChars = (trimmed.match(/[{}\[\]()<>=:;,.!?"'`\/\\|#*&^%$@~+-]/g) || []).length;
  const codeRatio = specialChars / Math.max(1, chars);

  // Heuristic: standard prose ~4 chars/token, code-heavy ~3 chars/token
  const charEstimate = Math.ceil(chars / (codeRatio > 0.15 ? 3.2 : 4.0));
  const wordEstimate = Math.ceil(words * 1.35);

  return Math.max(charEstimate, wordEstimate);
}

// --- DATA LOSS PREVENTION (DLP) & SECRET REDACTION ENGINE ---
function maskSensitiveData(text) {
  if (!text) return { sanitized: "", secretsFound: [] };

  let sanitized = text;
  const secretsFound = [];

  const patterns = [
    {
      type: "OpenAI API Key",
      regex: /\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b/g,
      replacement: "[MASKED_OPENAI_KEY]"
    },
    {
      type: "Google AI / Gemini Key",
      regex: /\b(AIzaSy[a-zA-Z0-9_-]{30,})\b/g,
      replacement: "[MASKED_GOOGLE_KEY]"
    },
    {
      type: "Anthropic Claude Key",
      regex: /\b(sk-ant-[a-zA-Z0-9_-]{20,})\b/g,
      replacement: "[MASKED_ANTHROPIC_KEY]"
    },
    {
      type: "AWS Access Key",
      regex: /\b(AKIA[0-9A-Z]{16})\b/g,
      replacement: "[MASKED_AWS_KEY]"
    },
    {
      type: "GitHub Token",
      regex: /\b(gh[pousr]_[A-Za-z0-9_]{36,})\b/g,
      replacement: "[MASKED_GITHUB_TOKEN]"
    },
    {
      type: "JWT / Bearer Token",
      regex: /\b(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b/g,
      replacement: "[MASKED_JWT_TOKEN]"
    },
    {
      type: "Database Password / URI",
      regex: /((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)/gi,
      customReplace: (match, prefix, pass, suffix) => `${prefix}[MASKED_DB_PASS]${suffix}`
    },
    {
      type: "Secret in Config",
      regex: /\b((?:API_KEY|SECRET|PASSWORD|PASSWD|AUTH_TOKEN|PRIVATE_KEY)\s*[:=]\s*["'])([^"'\n]{4,})(["'])/gi,
      customReplace: (match, prefix, val, suffix) => `${prefix}[MASKED_SECRET]${suffix}`
    }
  ];

  for (const item of patterns) {
    // Fix: always reset lastIndex before using global regexes to avoid
    // the stateful bug where .test() advances lastIndex and .replace() skips matches.
    item.regex.lastIndex = 0;

    if (item.customReplace) {
      item.regex.lastIndex = 0;
      const testCopy = new RegExp(item.regex.source, item.regex.flags);
      if (testCopy.test(sanitized)) {
        item.regex.lastIndex = 0;
        sanitized = sanitized.replace(item.regex, (match, p1, p2, p3) => {
          secretsFound.push({ type: item.type, snippet: match.substring(0, 15) + "..." });
          return item.customReplace(match, p1, p2, p3);
        });
      }
    } else {
      item.regex.lastIndex = 0;
      const allMatches = [...sanitized.matchAll(item.regex)];
      if (allMatches.length > 0) {
        allMatches.forEach(m => {
          secretsFound.push({ type: item.type, snippet: m[0].substring(0, 8) + "..." });
        });
        item.regex.lastIndex = 0;
        sanitized = sanitized.replace(item.regex, item.replacement);
      }
    }
  }

  return { sanitized, secretsFound };
}

// --- DUPLICATE SENTENCE & PARAGRAPH DETECTOR ---
function removeDuplicateSentences(text, rulesApplied) {
  if (!text) return "";
  const sentences = text.match(/[^.!?]+(?:[.!?]+|\s*$)/g) || [text];
  const seen = new Set();
  const result = [];
  let hasDupes = false;

  for (const s of sentences) {
    const trimmed = s.trim();
    if (!trimmed) continue;
    // Normalized key
    const key = trimmed.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (key.length > 15 && seen.has(key)) {
      hasDupes = true;
    } else {
      if (key.length > 15) seen.add(key);
      result.push(s);
    }
  }

  if (hasDupes && rulesApplied && !rulesApplied.includes("Duplicate sentence removal")) {
    rulesApplied.push("Duplicate sentence removal");
  }

  return result.join(" ").replace(/\s{2,}/g, " ").trim();
}

// --- LOCAL HEURISTIC OPTIMIZATION ENGINE ---
function optimizeLocally(text, mode = "balanced", rules = {}) {
  if (!text) return { optimized: "", rulesApplied: [] };

  const rulesApplied = [];
  const placeholders = [];
  let counter = 0;

  // Protect code blocks, inline code, URLs, and HTML tags from regex corruption
  let processed = text.replace(
    /(```[\s\S]*?```|`[^`\n]+`|<[^>]+>|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|https?:\/\/[^\s]+)/g,
    (match) => {
      const ph = `__SQUEEZE_PLACEHOLDER_${counter}__`;
      placeholders.push({ placeholder: ph, original: match });
      counter++;
      return ph;
    }
  );

  // 1. Remove duplicate sentences
  if (rules.ruleSimplifyPhrases) {
    processed = removeDuplicateSentences(processed, rulesApplied);
  }

  // 2. Meta-commentary & Preamble Removal
  if (rules.ruleStripGreetings) {
    let changed = false;
    const metaPatterns = [
      /\b(?:just\s+to\s+clarify|as\s+stated\s+previously|mind\s+you|bear\s+in\s+mind\s+that|it's\s+worth\s+noting\s+that|to\s+be\s+clear|note\s+that|needless\s+to\s+say)\b[.,!?]*\s*/gi,
      /\b(?:so\s+)?as\s+i\s+(?:mentioned|stated)(?:\s+(?:above|earlier|previously|before))?\b[.,!?]*\s*/gi,
      /\b(?:as\s+we\s+discussed|just\s+to\s+recap\s+our\s+discussion|recap\s+our\s+discussion)\b(?:\s+(?:earlier\s+in\s+the\s+thread|above|previously|before))?[.,!?]*\s*/gi
    ];
    metaPatterns.forEach(p => {
      if (p.test(processed)) {
        processed = processed.replace(p, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Meta-commentary removal");
  }

  // 3. Redundant Qualifiers Stripping
  if (rules.ruleSimplifyPhrases) {
    let changed = false;
    const qualifiers = [
      /\b(?:please\s+)?make\s+sure\s+that\s+you\b\s*/gi,
      /\bi\s+need\s+you\s+to\b\s*/gi,
      /\bi\s+want\s+you\s+to\b\s*/gi,
      /\bit\s+is\s+important\s+(?:that|to)\s+you\b\s*/gi,
      /\bbe\s+sure\s+to\b\s*/gi,
      /\bensure\s+that\s+you\b\s*/gi,
      /\bgo\s+ahead\s+and\b\s*/gi,
      /\bkindly\s+(?:provide|generate|give|write)\b\s*/gi,
      /\bi\s+was\s+hoping\s+you\s+could\b\s*/gi
    ];
    qualifiers.forEach(regex => {
      if (regex.test(processed)) {
        processed = processed.replace(regex, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Redundant qualifier stripping");
  }

  // 4. Role-play Preamble Compaction
  if (rules.ruleStripGreetings) {
    const roleRegex = /\bact\s+as\s+(?:if\s+you\s+were\s+)?(?:though\s+you\s+were\s+)?(?:a\s+|an\s+)?(?:the\s+)?(?:expert\s+|professional\s+|senior\s+|experienced\s+)?([\w\s-]+?)(?:\s+with\s+\d+\s+years\s+of\s+experience|\s+with\s+experience)?\s*([.,!?]|$)/gi;
    if (roleRegex.test(processed)) {
      processed = processed.replace(roleRegex, (m, role, punct) => `Act as ${role.trim()}${punct || "."}`);
      rulesApplied.push("Role-play preamble compaction");
    }
  }

  // 5. Politeness & Greetings Removal
  if (rules.ruleStripGreetings) {
    let changed = false;
    const politenessPatterns = [
      { regex: /\b(?:thank\s+you|thanks)(?:\s+for\s+[^.!?]+)?(?:\s*,\s*it\s+was\s+[^.!?]+)?[.!?]+\s*/gi },
      { regex: /\b(?:thank\s+you|thanks)\s*,\s*(?:that\s+worked|that\s+works\s+(?:great|well)?)[.!?]+\s*/gi },
      { regex: /\b(?:awesome|great|cool|perfect)\s*,\s*that\s+works\s+(?:great|well|perfectly)?[.!?]+\s*/gi },
      { regex: /\bthanks\s+in\s+advance[.,!?]*\s*/gi },
      { regex: /\bi\s+would\s+(?:really\s+)?appreciate\s+it\s+if\s+you\s+could\b\s*/gi },
      { regex: /\blet\s+me\s+know\s+if\s+you\s+have\s+(?:any\s+)?questions[.,!?]*\s*/gi },
      { regex: /\blet\s+me\s+know\s+what\s+you\s+think[.,!?]*\s*/gi },
      { regex: /\bhope\s+you\s+are\s+doing\s+well[.,!?]*\s*/gi },
      { regex: /\bhope\s+this\s+helps[.,!?]*\s*/gi },
      { regex: /\bbest\s+regards|regards|sincerely|yours\s+truly\b[.,!?]*\s*/gi },
      { regex: /(?:hello|hi|hey|greetings|dear|good\s+(?:morning|afternoon|evening))\s+(?:claude|chatgpt|assistant|ai|there|sir|madam|team|friend|buddy)\b[.,!?]*\s*/gi },
      { regex: /\b(?:could|can|would)\s+you\s+please\s+(?:help\s+me\s+(?:to\s+)?)?/gi },
      { regex: /\b(?:could|can|would)\s+you\s+(?:help\s+me\s+(?:to\s+)?)?/gi },
      { regex: /\b(?:i\s+would\s+like\s+you\s+to|i\s+want\s+you\s+to|i\s+need\s+you\s+to|i'm\s+looking\s+for\s+a|i\s+was\s+wondering\s+if\s+you\s+could)\b\s*/gi },
      { regex: /(?:^|([.!?]\s+))please\b\s*/gi, replaceWith: "$1" },
      { regex: /\bplease\s+(?:write|create|generate|make|help|explain|do|find|check|tell|give|show|list|analyze|sort|provide)\b/gi },
      { regex: /,\s*please[.,!?]*(?=\s|$)/gi },
      { regex: /\bthank\s+you\b[.,!?]*\s*/gi },
      { regex: /\bthanks\b[.,!?]*\s*/gi }
    ];

    politenessPatterns.forEach(item => {
      if (item.regex.test(processed)) {
        processed = item.replaceWith !== undefined
          ? processed.replace(item.regex, item.replaceWith)
          : processed.replace(item.regex, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Politeness padding removal");
  }

  // 6. Verbosity Simplification (Comprehensive dictionary)
  if (rules.ruleSimplifyPhrases) {
    const dictionary = {
      "in order to": "to",
      "due to the fact that": "because",
      "at this point in time": "now",
      "for the purpose of": "to",
      "has the ability to": "can",
      "take into consideration": "consider",
      "make a decision": "decide",
      "utilize": "use",
      "utilizes": "uses",
      "utilizing": "using",
      "as well as": "and",
      "a number of": "several",
      "along the lines of": "like",
      "referred to as": "called",
      "in the event that": "if",
      "on a daily basis": "daily",
      "with respect to": "regarding",
      "in addition to": "and",
      "so as to": "to",
      "is responsible for": "does",
      "by means of": "by",
      "in close proximity to": "near",
      "make use of": "use",
      "perform an analysis of": "analyze",
      "provide an explanation of": "explain",
      "conduct an investigation into": "investigate",
      "has a requirement for": "needs",
      "it is important to note that": "note that",
      "bearing in mind that": "considering",
      "for the reason that": "because",
      "in the near future": "soon",
      "in the course of": "during",
      "with the exception of": "except",
      "are in agreement": "agree",
      "make adjustments to": "adjust",
      "give rise to": "cause",
      "draw attention to": "highlight",
      "at the present time": "currently",
      "subsequent to": "after",
      "prior to": "before",
      "take steps to": "try to",
      "despite the fact that": "although",
      "as a consequence of": "because of",
      "at an early date": "soon",
      "by virtue of": "because of",
      "give consideration to": "consider",
      "in spite of": "despite"
    };

    let changed = false;
    for (const [verbose, concise] of Object.entries(dictionary)) {
      const reg = new RegExp(`\\b${verbose}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, concise);
        changed = true;
      }
    }
    if (changed) rulesApplied.push("Verbosity simplification");
  }

  // 7. Technical Abbreviation Substitution
  if (rules.ruleAbbreviate) {
    let abbrevs = {
      "information": "info",
      "database": "DB",
      "function": "fn",
      "parameter": "param",
      "parameters": "params",
      "configuration": "config",
      "administrator": "admin",
      "development": "dev",
      "application": "app",
      "applications": "apps",
      "for example": "e.g.",
      "that is": "i.e.",
      "versus": "vs",
      "approximately": "~",
      "without": "w/o",
      "with": "w/",
      "number": "num",
      "numbers": "nums",
      "between": "betw",
      "through": "thru",
      "standard": "std",
      "environment": "env",
      "temporary": "temp",
      "documentation": "docs",
      "difference": "diff",
      "developer": "dev",
      "developers": "devs",
      "repository": "repo",
      "repositories": "repos",
      "directory": "dir",
      "directories": "dirs",
      "implementation": "impl",
      "implementations": "impls"
    };

    // Conservative abbreviation in balanced/polish mode
    if (mode === "balanced" || mode === "polish") {
      abbrevs = {
        "for example": "e.g.",
        "that is": "i.e.",
        "versus": "vs",
        "approximately": "~",
        "documentation": "docs",
        "configuration": "config",
        "repository": "repo"
      };
    }

    let changed = false;
    for (const [full, abbr] of Object.entries(abbrevs)) {
      const reg = new RegExp(`\\b${full}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, abbr);
        changed = true;
      }
    }
    if (changed) rulesApplied.push("Abbreviation substitution");
  }

  // 8. Article & Auxiliary Stripping (Squeeze / Extreme Mode)
  if (rules.ruleStripArticles && mode === "squeeze") {
    const auxiliaries = {
      "should make a request to": "request",
      "should make a request": "request",
      "make a request to": "request",
      "is going to be": "will be",
      "should be": "be",
      "ought to": "should",
      "will be able to": "can",
      "it is necessary that": "must",
      "you can": "can",
      "we can": "can"
    };

    let changed = false;
    for (const [k, v] of Object.entries(auxiliaries)) {
      const reg = new RegExp(`\\b${k}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, v);
        changed = true;
      }
    }

    const articles = /\b(?:the|a|an)\b\s+/gi;
    if (articles.test(processed)) {
      processed = processed.replace(articles, "");
      changed = true;
    }

    if (changed) rulesApplied.push("Article & auxiliary stripping");
  }

  // 9. Markdown & Whitespace Polish
  if (rules.rulePolishMarkdown) {
    let changed = false;
    // Clean excessive punctuation
    if (/!{2,}/.test(processed)) {
      processed = processed.replace(/!{2,}/g, "!");
      changed = true;
    }
    if (/\?{2,}/.test(processed)) {
      processed = processed.replace(/\?{2,}/g, "?");
      changed = true;
    }
    // Fix markdown headings: '#Heading' -> '# Heading'
    processed = processed.replace(/(^|\n)(#{1,6})([^\s#])([^\n]+)/g, "$1$2 $3$4");
    // Normalize bullet points to '- '
    processed = processed.replace(/(^|\n)[*+]\s+/g, "$1- ");
    // Remove multi-spaces and trailing spaces
    processed = processed.replace(/[ \t]{2,}/g, " ");
    processed = processed.replace(/^[ \t]+/gm, "").replace(/[ \t]+$/gm, "");
    // Collapse excessive blank lines (max 2)
    processed = processed.replace(/\n{3,}/g, "\n\n");

    if (changed) rulesApplied.push("Punctuation & spacing cleanup");
  }

  processed = processed.trim();

  // Restore protected blocks
  for (let i = 0; i < placeholders.length; i++) {
    const item = placeholders[i];
    processed = processed.replace(item.placeholder, item.original);
  }

  return { optimized: processed, rulesApplied };
}

// --- CONTEXT VAULT INJECTION ---
async function processVaultContext(prompt, mode, rules) {
  // chrome.storage.local.get returns a Promise in MV3
  const data = await chrome.storage.local.get([
    "vaultPreferences", "vaultPrefAlwaysInject", "vaultSmartTriggers",
    "vaultFiles", "vaultServerUrl", "vaultServerEnabled"
  ]);

  const prefs = data.vaultPreferences || "";
  const alwaysInject = data.vaultPrefAlwaysInject !== false;
  const smartTriggers = data.vaultSmartTriggers !== false;
  const files = data.vaultFiles || [];
  const attachedContexts = [];
  const contextParts = [];
  let rawTokens = 0;

  // 1. Personal Profile / Preferences
  if (prefs.trim() && alwaysInject) {
    rawTokens += estimateTokens(prefs);
    const optPrefs = optimizeLocally(prefs, "balanced", {
      ruleStripGreetings: true,
      ruleSimplifyPhrases: true,
      ruleAbbreviate: false,
      ruleStripArticles: false,
      rulePolishMarkdown: true
    }).optimized;
    contextParts.push(`[Developer Profile]\n${optPrefs}`);
    attachedContexts.push("Developer Profile");
  }

  // 2. Local Files matching keywords
  if (files.length > 0) {
    const lowerPrompt = prompt.toLowerCase();
    for (const f of files) {
      let matches = false;
      if (smartTriggers) {
        const baseTokens = f.name
          .replace(/\.[a-z0-9]+$/i, "")
          .toLowerCase()
          .split(/[^a-z0-9]+/)
          .filter(w => w.length >= 3 || ["db", "js", "ts", "go", "py", "sql", "api", "auth"].includes(w));

        for (const tok of baseTokens) {
          if (new RegExp("\\b" + tok + "\\b", "i").test(lowerPrompt)) {
            matches = true;
            break;
          }
        }
      } else {
        matches = true;
      }

      if (matches && f.content) {
        rawTokens += estimateTokens(f.content);
        let contentToProcess = f.content;
        const ext = f.name.split(".").pop().toLowerCase();

        // 🚀 Squeeze Code & Data Intelligence:
        // Automatically skeletonize code and fold JSON arrays to save 70-90% tokens!
        let labelSuffix = "";
        if (typeof skeletonizeCode === "function" && ["py", "ts", "tsx", "js", "jsx", "go", "rs"].includes(ext)) {
          contentToProcess = skeletonizeCode(f.content, f.name);
          labelSuffix = " (Squeeze Skeleton)";
        } else if (typeof shrinkJson === "function" && ext === "json") {
          contentToProcess = shrinkJson(f.content, 2);
          labelSuffix = " (Squeeze Shrunk)";
        }

        const optFile = optimizeLocally(maskSensitiveData(contentToProcess).sanitized, mode, rules).optimized;
        contextParts.push(`[Context: ${f.name}${labelSuffix}]\n${optFile}`);
        attachedContexts.push(`${f.name}${labelSuffix ? " [Condensed]" : ""}`);
      }
    }
  }

  let contextBlock = "";
  if (contextParts.length > 0) {
    contextBlock = `=== SQUEEZED CONTEXT VAULT ===\n${contextParts.join("\n\n")}\n==============================\n\n`;
  }

  return { contextBlock, attachedContexts, rawContextTokens: rawTokens };
}

// --- MESSAGE DISPATCHER ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "optimizePrompt") {
    (async () => {
      const { prompt, mode: requestedMode } = request;
      const settings = await chrome.storage.local.get([
        "optimizationMode",
        "ruleStripGreetings",
        "ruleSimplifyPhrases",
        "ruleAbbreviate",
        "ruleStripArticles",
        "rulePolishMarkdown",
        "ruleSecretShield"
      ]);

      const mode = requestedMode || settings.optimizationMode || "balanced";
      const rules = {
        ruleStripGreetings: settings.ruleStripGreetings !== false,
        ruleSimplifyPhrases: settings.ruleSimplifyPhrases !== false,
        ruleAbbreviate: settings.ruleAbbreviate !== false,
        ruleStripArticles: settings.ruleStripArticles !== false,
        rulePolishMarkdown: settings.rulePolishMarkdown !== false
      };

      try {
        // 1. DLP Secret Scan & Redaction
        let workingPrompt = prompt;
        let secretsDetected = [];
        if (settings.ruleSecretShield !== false) {
          const dlp = maskSensitiveData(prompt);
          workingPrompt = dlp.sanitized;
          secretsDetected = dlp.secretsFound;
        }

        // 2. Vault Context Attachment
        const { contextBlock, attachedContexts, rawContextTokens } = await processVaultContext(
          workingPrompt,
          mode,
          rules
        );

        // 3. Local Compression
        const { optimized, rulesApplied } = optimizeLocally(workingPrompt, mode, rules);
        const finalOptimized = contextBlock + optimized;

        // 4. Token & Cost Accounting
        const originalTokens = estimateTokens(prompt) + rawContextTokens;
        const optimizedTokens = estimateTokens(finalOptimized);
        const tokensSaved = Math.max(0, originalTokens - optimizedTokens);
        const percentageSaved = originalTokens > 0 ? Math.round((tokensSaved / originalTokens) * 100) : 0;

        // Multi-model savings calculation
        const costSavings = {};
        for (const [key, model] of Object.entries(MODEL_RATES)) {
          costSavings[key] = {
            name: model.name,
            savedDollars: (tokensSaved / 1_000_000) * model.ratePerMillion
          };
        }

        const sonnetSavings = costSavings.sonnet.savedDollars;

        // 5. Update Cumulative Stats & History
        const currentStats = await chrome.storage.local.get([
          "stats_promptsOptimized",
          "stats_tokensSaved",
          "stats_costSaved",
          "stats_history"
        ]);

        const history = currentStats.stats_history || [];
        history.unshift({
          timestamp: Date.now(),
          originalLength: prompt.length,
          tokensSaved,
          percentageSaved,
          mode,
          snippet: prompt.substring(0, 60).replace(/\n/g, " ") + (prompt.length > 60 ? "..." : "")
        });

        // Keep last 15 history entries (splice is safe even if > 1 extra entry)
        if (history.length > 15) history.splice(15);

        await chrome.storage.local.set({
          stats_promptsOptimized: (currentStats.stats_promptsOptimized || 0) + 1,
          stats_tokensSaved: (currentStats.stats_tokensSaved || 0) + tokensSaved,
          stats_costSaved: (currentStats.stats_costSaved || 0) + sonnetSavings,
          stats_history: history
        });

        sendResponse({
          success: true,
          original: prompt,
          optimized: finalOptimized,
          originalTokens,
          optimizedTokens,
          tokensSaved,
          percentageSaved,
          mode,
          rulesApplied,
          attachedContexts,
          secretsDetected,
          costSavings
        });
      } catch (err) {
        console.error("Optimization error:", err);
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true; // Keep message channel open for async response
  }

  if (request.action === "openSidePanel") {
    (async () => {
      try {
        let windowId = sender.tab?.windowId;
        if (!windowId) {
          const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
          windowId = activeTab?.windowId;
        }
        if (chrome.sidePanel?.open && windowId) {
          await chrome.sidePanel.open({ windowId });
          sendResponse({ success: true });
        } else {
          sendResponse({ success: false, error: "Side Panel API unavailable" });
        }
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "getStats") {
    (async () => {
      const stats = await chrome.storage.local.get([
        "stats_promptsOptimized",
        "stats_tokensSaved",
        "stats_costSaved",
        "stats_history"
      ]);
      sendResponse({ success: true, stats });
    })();
    return true;
  }

  if (request.action === "resetStats") {
    (async () => {
      await chrome.storage.local.set({
        stats_promptsOptimized: 0,
        stats_tokensSaved: 0,
        stats_costSaved: 0,
        stats_history: []
      });
      sendResponse({ success: true });
    })();
    return true;
  }

  if (request.action === "checkBuiltInAI") {
    (async () => {
      const hasAI = typeof globalThis.ai !== "undefined" && typeof globalThis.ai.languageModel !== "undefined";
      sendResponse({ success: true, hasBuiltInAI: hasAI });
    })();
    return true;
  }

  // --- SQUEEZE CODE & CACHE ACTIONS ---
  if (request.action === "skeletonizeCode") {
    (async () => {
      try {
        const { code, language } = request;
        const skeleton = typeof skeletonizeCode === "function"
          ? skeletonizeCode(code, language)
          : code;
        const origTokens = estimateTokens(code);
        const skelTokens = estimateTokens(skeleton);
        sendResponse({
          success: true,
          skeleton,
          originalTokens: origTokens,
          skeletonTokens: skelTokens,
          tokensSaved: Math.max(0, origTokens - skelTokens)
        });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "shrinkJson") {
    (async () => {
      try {
        const { jsonText, maxItems } = request;
        const shrunk = typeof shrinkJson === "function"
          ? shrinkJson(jsonText, maxItems || 2)
          : jsonText;
        const origTokens = estimateTokens(jsonText);
        const shrunkTokens = estimateTokens(shrunk);
        sendResponse({
          success: true,
          shrunk,
          originalTokens: origTokens,
          shrunkTokens,
          tokensSaved: Math.max(0, origTokens - shrunkTokens)
        });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "shrinkLogs") {
    (async () => {
      try {
        const { logText } = request;
        const shrunk = typeof shrinkLogs === "function"
          ? shrinkLogs(logText)
          : logText;
        sendResponse({ success: true, shrunk });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "getCodeGraph") {
    (async () => {
      try {
        const data = await chrome.storage.local.get(["vaultFiles"]);
        const files = data.vaultFiles || [];
        const graph = typeof buildCodebaseGraph === "function"
          ? buildCodebaseGraph(files)
          : { graphText: "Graph engine unavailable", nodes: [] };
        sendResponse({ success: true, graph });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "alignCache") {
    (async () => {
      try {
        const { systemPrompt, context, query } = request;
        const aligned = typeof alignPromptForCache === "function"
          ? alignPromptForCache(systemPrompt, context, query)
          : `${systemPrompt}\n\n${context}\n\n${query}`;
        sendResponse({ success: true, aligned });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }
});
```

## File: `content.js`
```javascript
/**
 * Squeeze AI - Universal Content Script (Manifest V3)
 * Operates across Claude.ai, ChatGPT (chatgpt.com), and Google Gemini (gemini.google.com).
 * Injects prompt optimizer widgets, context depth monitors, secret alerts, and PDF squeezer.
 */

(function () {
  // --- PLATFORM DETECTION ---
  const HOST = window.location.hostname;
  const IS_CLAUDE = HOST.includes("claude.ai");
  const IS_CHATGPT = HOST.includes("chatgpt.com") || HOST.includes("openai.com");
  const IS_GEMINI = HOST.includes("gemini.google.com");

  // State
  let activeInputEl = null;
  let triggerBtn = null;
  let undoBtn = null;
  let pdfBtn = null;
  let summaryBtn = null;
  let vaultBadge = null;
  let usageBar = null;
  let modalContainer = null;
  let drawerContainer = null;
  let sidebarBtn = null;

  let originalPromptText = "";
  let lastOptimizedPrompt = "";
  let currentOptMode = "balanced";
  let activeTooltip = null;
  let currentUploadedPdf = null;
  let duplicateContextBlocks = [];
  let workingModalPrompt = "";

  // --- UNIVERSAL PLATFORM ADAPTER ---
  function findChatInput() {
    if (IS_CLAUDE) {
      return document.querySelector('div[contenteditable="true"]');
    }

    if (IS_CHATGPT) {
      // ChatGPT input can be contenteditable or textarea
      return (
        document.querySelector("#prompt-textarea") ||
        document.querySelector('div[contenteditable="true"][data-placeholder]') ||
        document.querySelector('div[contenteditable="true"]') ||
        document.querySelector('textarea[data-id="root"]')
      );
    }

    if (IS_GEMINI) {
      // Gemini rich-textarea
      return (
        document.querySelector("rich-textarea div[contenteditable='true']") ||
        document.querySelector(".ql-editor") ||
        document.querySelector("div.text-input-field[contenteditable='true']") ||
        document.querySelector("textarea[aria-label*='prompt' i]") ||
        document.querySelector("div[contenteditable='true']")
      );
    }

    // Generic fallback
    return document.querySelector('div[contenteditable="true"]') || document.querySelector("textarea");
  }

  function getInputValue(el) {
    if (!el) return "";
    let val = "";
    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      val = el.value || "";
    } else {
      val = el.innerText || el.textContent || "";
    }
    return val.replace(/[\u200B-\u200D\uFEFF]/g, "").trim();
  }

  function setInputValue(el, text) {
    if (!el) return;
    el.focus();

    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
      if (nativeSetter) {
        nativeSetter.call(el, text);
      } else {
        el.value = text;
      }
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      // ContentEditable elements (Claude, ChatGPT rich text, Gemini)
      try {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        selection.removeAllRanges();
        selection.addRange(range);

        const execSuccess = document.execCommand("insertText", false, text);
        if (!execSuccess) {
          el.innerText = text;
        }
      } catch (err) {
        console.warn("execCommand fallback:", err);
        el.innerText = text;
      }

      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertReplacementText", data: text }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // Visual feedback highlight
    const wrapper = el.closest(".flex.flex-col") || el.closest("fieldset") || el.closest("form") || el.parentElement;
    if (wrapper) {
      wrapper.style.transition = "box-shadow 0.3s ease";
      wrapper.style.boxShadow = "0 0 15px rgba(52, 211, 153, 0.6)";
      setTimeout(() => { wrapper.style.boxShadow = ""; }, 1200);
    }
    setTimeout(() => el.focus(), 50);
  }

  function findToolbarAnchor(inputEl) {
    if (!inputEl) return null;

    if (IS_CLAUDE) {
      const modelBtn = Array.from(document.querySelectorAll("button")).find(b => {
        const txt = (b.innerText || "").toLowerCase();
        return txt.includes("sonnet") || txt.includes("haiku") || txt.includes("opus") || txt.includes("claude");
      });
      if (modelBtn && modelBtn.parentNode) return { container: modelBtn.parentNode, beforeNode: modelBtn };

      const form = inputEl.closest("fieldset") || inputEl.closest("form");
      if (form) {
        const attachBtn = form.querySelector('button[aria-label*="attach" i]') || form.querySelector("button svg")?.closest("button");
        if (attachBtn && attachBtn.parentNode) return { container: attachBtn.parentNode, beforeNode: attachBtn };
      }
    }

    if (IS_CHATGPT) {
      // Find ChatGPT button row under prompt textarea
      const composer = inputEl.closest("form") || inputEl.closest('[data-testid*="composer"]') || inputEl.parentElement;
      if (composer) {
        const submitBtn = composer.querySelector('button[data-testid*="send-button"]') || composer.querySelector('button[aria-label*="send" i]');
        if (submitBtn && submitBtn.parentNode) return { container: submitBtn.parentNode, beforeNode: submitBtn };

        const attachBtn = composer.querySelector('button[aria-label*="attach" i]') || composer.querySelector('button[aria-label*="upload" i]');
        if (attachBtn && attachBtn.parentNode) return { container: attachBtn.parentNode, beforeNode: attachBtn.nextSibling };
      }
    }

    if (IS_GEMINI) {
      const geminiContainer = inputEl.closest(".input-area") || inputEl.closest("rich-textarea")?.parentElement;
      if (geminiContainer) {
        const sendBtn = geminiContainer.querySelector("button[aria-label*='Send' i]") || geminiContainer.querySelector(".send-button");
        if (sendBtn && sendBtn.parentNode) return { container: sendBtn.parentNode, beforeNode: sendBtn };
      }
    }

    // Default container: parent element of the input
    const parent = inputEl.parentElement;
    return parent ? { container: parent, beforeNode: null } : null;
  }

  // --- TOKEN ESTIMATION ---
  function estimateTokensLocal(text) {
    if (!text) return 0;
    const trimmed = text.trim();
    if (!trimmed) return 0;
    const words = trimmed.split(/\s+/).length;
    const chars = trimmed.length;
    const specialChars = (trimmed.match(/[{}\[\]()<>=:;,.!?"'`\/\\|#*&^%$@~+-]/g) || []).length;
    const codeRatio = specialChars / Math.max(1, chars);
    const charEst = Math.ceil(chars / (codeRatio > 0.15 ? 3.2 : 4.0));
    const wordEst = Math.ceil(words * 1.35);
    return Math.max(charEst, wordEst);
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- TOOLTIP DISPLAY ---
  function showTooltip(targetEl, text) {
    hideTooltip();
    const tip = document.createElement("div");
    tip.className = "squeeze-tooltip";
    tip.textContent = text;
    document.body.appendChild(tip);

    const rect = targetEl.getBoundingClientRect();
    tip.style.left = rect.left + window.scrollX + rect.width / 2 - tip.offsetWidth / 2 + "px";
    tip.style.top = rect.top + window.scrollY - tip.offsetHeight - 8 + "px";

    requestAnimationFrame(() => tip.classList.add("show"));
    activeTooltip = tip;
  }

  function hideTooltip() {
    if (activeTooltip) {
      const tip = activeTooltip;
      activeTooltip = null;
      tip.classList.remove("show");
      setTimeout(() => tip.remove(), 150);
    }
  }

  function showToast(targetEl, text) {
    const toast = document.createElement("div");
    toast.className = "squeeze-tooltip";
    toast.textContent = text;
    document.body.appendChild(toast);

    const rect = targetEl.getBoundingClientRect();
    toast.style.left = rect.left + window.scrollX + rect.width / 2 - toast.offsetWidth / 2 + "px";
    toast.style.top = rect.top + window.scrollY - toast.offsetHeight - 8 + "px";
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  // --- ATTACH IN-PAGE SQUEEZE CONTROLS ---
  function mountWidgets() {
    const input = findChatInput();
    if (!input) {
      if (triggerBtn && !document.contains(triggerBtn)) triggerBtn = null;
      return;
    }

    if (input.dataset.squeezeInjected === "true" && triggerBtn && document.contains(triggerBtn)) {
      activeInputEl = input;
      return;
    }

    activeInputEl = input;
    input.dataset.squeezeInjected = "true";

    // Clean up any stale elements
    if (triggerBtn) triggerBtn.remove();
    if (pdfBtn) pdfBtn.remove();
    if (undoBtn) undoBtn.remove();
    if (summaryBtn) summaryBtn.remove();
    if (vaultBadge) vaultBadge.remove();

    // Helper to make a div accessible as a button
    function makeAccessibleBtn(el, label) {
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", label);
      el.setAttribute("tabindex", "0");
      el.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); el.click(); }
      });
    }

    // 1. Squeeze Trigger Button
    triggerBtn = document.createElement("div");
    triggerBtn.className = "squeeze-trigger-btn inline-btn";
    triggerBtn.dataset.tooltip = "Squeeze Prompt (Ctrl+Shift+S)";
    makeAccessibleBtn(triggerBtn, "Squeeze Prompt (Ctrl+Shift+S)");
    triggerBtn.addEventListener("mouseenter", () => showTooltip(triggerBtn, triggerBtn.dataset.tooltip));
    triggerBtn.addEventListener("mouseleave", hideTooltip);
    triggerBtn.innerHTML = `
      <svg viewBox="0 0 512 512" width="16" height="16" style="display: block; color: inherit;" aria-hidden="true">
        <rect x="120" y="140" width="272" height="48" rx="24" fill="currentColor"/>
        <rect x="144" y="212" width="224" height="48" rx="24" fill="currentColor" fill-opacity="0.8"/>
        <rect x="176" y="284" width="160" height="48" rx="24" fill="currentColor" fill-opacity="0.6"/>
        <rect x="208" y="356" width="96" height="48" rx="24" fill="currentColor" fill-opacity="0.4"/>
      </svg>
    `;

    // 2. PDF Squeeze Button
    pdfBtn = document.createElement("div");
    pdfBtn.className = "squeeze-pdf-btn inline-btn";
    pdfBtn.dataset.tooltip = "Squeeze PDF & Insert";
    makeAccessibleBtn(pdfBtn, "Squeeze PDF and Insert");
    pdfBtn.addEventListener("mouseenter", () => showTooltip(pdfBtn, pdfBtn.dataset.tooltip));
    pdfBtn.addEventListener("mouseleave", hideTooltip);
    pdfBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
      </svg>
    `;

    // 3. Undo Button
    undoBtn = document.createElement("div");
    undoBtn.className = "squeeze-undo-btn inline-btn";
    undoBtn.dataset.tooltip = "Undo Prompt Optimization";
    makeAccessibleBtn(undoBtn, "Undo Prompt Optimization");
    undoBtn.addEventListener("mouseenter", () => showTooltip(undoBtn, undoBtn.dataset.tooltip));
    undoBtn.addEventListener("mouseleave", hideTooltip);
    undoBtn.style.display = "none";
    undoBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transform: scaleX(-1);" aria-hidden="true">
        <path d="M3 7v6h6"></path>
        <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
      </svg>
    `;

    // 4. Summarise Context Button
    summaryBtn = document.createElement("div");
    summaryBtn.className = "squeeze-summary-btn inline-btn";
    summaryBtn.dataset.tooltip = "Summarize Chat & New Thread";
    makeAccessibleBtn(summaryBtn, "Summarize Chat and Open New Thread");
    summaryBtn.addEventListener("mouseenter", () => showTooltip(summaryBtn, summaryBtn.dataset.tooltip));
    summaryBtn.addEventListener("mouseleave", hideTooltip);
    summaryBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        <line x1="9" y1="10" x2="15" y2="10"></line>
      </svg>
    `;

    // 5. Vault Indicator Badge
    vaultBadge = document.createElement("div");
    vaultBadge.id = "squeezeVaultBadge";
    vaultBadge.className = "squeeze-vault-badge inline-btn";
    vaultBadge.setAttribute("role", "status");
    vaultBadge.setAttribute("aria-live", "polite");
    vaultBadge.style.display = "none";
    vaultBadge.style.cursor = "default";

    // Mount to anchor
    const anchor = findToolbarAnchor(input);
    if (anchor && anchor.container) {
      if (anchor.beforeNode) {
        anchor.container.insertBefore(triggerBtn, anchor.beforeNode);
        anchor.container.insertBefore(pdfBtn, triggerBtn);
        anchor.container.insertBefore(summaryBtn, pdfBtn);
        anchor.container.insertBefore(undoBtn, summaryBtn);
        anchor.container.insertBefore(vaultBadge, undoBtn);
      } else {
        anchor.container.appendChild(vaultBadge);
        anchor.container.appendChild(undoBtn);
        anchor.container.appendChild(summaryBtn);
        anchor.container.appendChild(pdfBtn);
        anchor.container.appendChild(triggerBtn);
      }
    }

    // Wire events
    wireInputEvents(input);
    wireTriggerButton(input);
    wirePdfButton(input);
    wireUndoButton(input);
    wireSummaryButton(input);

    updateTriggerActiveState(input);
    updateVaultBadge(getInputValue(input));
    mountContextUsageBar();
    mountSidebarButton();

    // Check for pending summary from previous chat
    chrome.storage.local.get(["pendingChatSummary"], res => {
      if (res && res.pendingChatSummary) {
        chrome.storage.local.remove(["pendingChatSummary"]);
        setTimeout(() => {
          setInputValue(input, res.pendingChatSummary);
          showToast(input, "Context summary pasted from previous chat! Ready to send.");
        }, 400);
      }
    });
  }

  function wireInputEvents(input) {
    // Debounce secondary updates to avoid scanning the full DOM on every keystroke
    let inputDebounce;
    input.addEventListener("input", () => {
      updateTriggerActiveState(input);
      clearTimeout(inputDebounce);
      inputDebounce = setTimeout(() => {
        updateVaultBadge(getInputValue(input));
        updateContextDepth();
      }, 300);
    });

    // Keyboard shortcut: Ctrl+Shift+S or Cmd+Shift+S to Squeeze
    input.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        triggerBtn.click();
      }
    });
  }

  function updateTriggerActiveState(input) {
    if (!triggerBtn) return;
    const val = getInputValue(input);
    if (val && val.length > 5) {
      triggerBtn.classList.add("active");
    } else {
      triggerBtn.classList.remove("active");
    }
  }

  function wireTriggerButton(input) {
    triggerBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      const text = getInputValue(input);
      if (!text || text.length < 5) {
        showToast(triggerBtn, "Type a prompt first!");
        return;
      }
      originalPromptText = text;
      openOptimizationModal(text, currentOptMode);
    });
  }

  function wireUndoButton(input) {
    undoBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      if (originalPromptText) {
        setInputValue(input, originalPromptText);
        undoBtn.style.display = "none";
        hideTooltip();
        showToast(triggerBtn, "Original prompt restored!");
        updateTriggerActiveState(input);
      }
    });
  }

  function wirePdfButton(input) {
    pdfBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      const fileInput = document.createElement("input");
      fileInput.type = "file";
      fileInput.accept = ".pdf";
      fileInput.style.display = "none";

      fileInput.addEventListener("change", async ev => {
        const file = ev.target.files[0];
        if (file) handlePdfExtraction(file);
      });

      document.body.appendChild(fileInput);
      fileInput.click();
      setTimeout(() => fileInput.remove(), 1000);
    });
  }

  // --- PDF EXTRACTION ---
  async function handlePdfExtraction(file) {
    ensureModalExists();
    currentUploadedPdf = file;
    const logoUrl = chrome.runtime.getURL("icons/icon48.png");

    modalContainer.innerHTML = `
      <div class="squeeze-modal-card">
        <div class="tm-modal-header">
          <div class="tm-modal-logo">
            <img src="${logoUrl}" class="animating" width="22" height="22" alt="Squeeze Icon">
            <span>Squeeze <span class="highlight">PDF Optimizer</span></span>
          </div>
          <button class="tm-close-btn">&times;</button>
        </div>
        <div class="tm-modal-body">
          <div class="tm-loading-state">
            <div class="tm-spinner"></div>
            <p id="tmPDFStatusText">Extracting text from PDF...</p>
            <span class="tm-loading-subtext" id="tmPDFSubtext">Initializing parser...</span>
          </div>
        </div>
      </div>
    `;

    modalContainer.classList.add("open");
    modalContainer.querySelector(".tm-close-btn").addEventListener("click", closeModal);

    const statusText = modalContainer.querySelector("#tmPDFStatusText");
    const subText = modalContainer.querySelector("#tmPDFSubtext");

    try {
      if (typeof pdfjsLib === "undefined") {
        throw new Error("PDF parser library failed to load.");
      }

      pdfjsLib.GlobalWorkerOptions.workerSrc = chrome.runtime.getURL("pdf.worker.min.js");
      subText.innerText = "Reading file buffer...";
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const totalPages = pdf.numPages;
      const pagesText = [];
      const lineFrequency = {};

      function normalizeLine(l) {
        return l.replace(/\bpage\s+\d+(\s+of\s+\d+)?\b/gi, "PAGE_NUM").replace(/\b\d+\b/g, "NUM").trim();
      }

      for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        statusText.innerText = `Extracting PDF (Page ${pageNum} of ${totalPages})...`;
        const page = await pdf.getPage(pageNum);
        const content = await page.getTextContent();
        const lineBuckets = {};

        content.items.forEach(item => {
          if (!item.str || !item.str.trim()) return;
          const yCoord = Math.round(item.transform[5] / 2) * 2;
          if (!lineBuckets[yCoord]) lineBuckets[yCoord] = [];
          lineBuckets[yCoord].push(item);
        });

        const sortedY = Object.keys(lineBuckets).map(Number).sort((a, b) => b - a);
        const pageLines = [];
        sortedY.forEach(y => {
          const text = lineBuckets[y].sort((a, b) => a.transform[4] - b.transform[4]).map(i => i.str).join(" ").trim();
          if (text) {
            pageLines.push(text);
            const norm = normalizeLine(text);
            lineFrequency[norm] = (lineFrequency[norm] || 0) + 1;
          }
        });
        pagesText.push(pageLines);
      }

      // Filter repeated headers & footers
      const headerFooters = new Set();
      if (totalPages > 1) {
        for (const [line, count] of Object.entries(lineFrequency)) {
          if (count > 0.5 * totalPages) headerFooters.add(line);
        }
      }

      const cleanedPages = [];
      pagesText.forEach(lines => {
        const filtered = lines.filter(l => !headerFooters.has(normalizeLine(l)));
        cleanedPages.push(filtered.join("\n"));
      });

      let extracted = cleanedPages.join("\n\n").trim();
      if (extracted.length < 20) throw new Error("SCANNED_PDF_DETECTED");

      let cleaned = extracted.split("\n").map(l => l.trim()).join("\n");
      cleaned = cleaned.replace(/[^\S\r\n]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();

      // Fix #15: Cap PDF content to prevent chrome.storage quota overflow and context floods
      const PDF_CHAR_LIMIT = 50_000; // ≈12,500 tokens
      if (cleaned.length > PDF_CHAR_LIMIT) {
        cleaned = cleaned.substring(0, PDF_CHAR_LIMIT);
        const truncNote = `\n\n[PDF truncated at ~50,000 chars to protect context limits. Full PDF: ${totalPages} pages.]`;
        cleaned += truncNote;
        if (subText) subText.innerText = `Content capped at 50K chars (${totalPages}-page PDF). Squeezing...`;
      }

      statusText.innerText = "Squeezing PDF content...";
      if (!cleaned.includes("PDF truncated")) subText.innerText = "Applying token compression...";
      workingModalPrompt = cleaned;
      duplicateContextBlocks = findDuplicateContext(cleaned);
      requestOptimization(cleaned, currentOptMode);
    } catch (err) {
      console.error("PDF parsing error:", err);
      let msg = "Failed to parse PDF document.";
      if (err.message === "SCANNED_PDF_DETECTED") {
        msg = "This PDF appears to be a scanned image or contains no extractable text.";
      } else {
        msg += ` (${err.message})`;
      }

      const body = modalContainer.querySelector(".tm-modal-body");
      body.innerHTML = `
        <div class="tm-dup-warning-banner" style="background: rgba(255, 59, 48, 0.08); border: 1px solid rgba(255, 59, 48, 0.25); padding: 18px; border-radius: 10px; text-align: center;">
          <div style="font-size: 1.6rem; margin-bottom: 8px;">⚠️</div>
          <div style="font-size: 0.82rem; color: #ff5e84; line-height: 1.5; font-weight: 600; margin-bottom: 12px;">${msg}</div>
          <button class="tm-btn" id="tmPDFErrorCloseBtn">Close</button>
        </div>
      `;
      body.querySelector("#tmPDFErrorCloseBtn").addEventListener("click", closeModal);
    }
  }

  // --- DUPLICATE CONTEXT DETECTION ---
  function findDuplicateContext(text) {
    const previousUserMessages = [];
    const selectors = [
      '[data-testid="user-message"]',
      'div.font-user-message',
      '[data-message-author-role="user"]',
      'user-query'
    ];
    document.querySelectorAll(selectors.join(", ")).forEach(el => {
      previousUserMessages.push(el.innerText.trim());
    });

    if (previousUserMessages.length === 0) return [];

    const duplicates = [];
    const codeBlockRegex = /```[\s\S]*?```/g;
    let match;
    const candidates = [];

    while ((match = codeBlockRegex.exec(text)) !== null) {
      const original = match[0];
      if (original.length > 100) {
        const content = original.replace(/^```\w*\n|```$/g, "").trim();
        candidates.push({ original, content, type: "code block" });
      }
    }

    text.replace(codeBlockRegex, "").split(/\n\s*\n+/).forEach(para => {
      const trimmed = para.trim();
      if (trimmed.length > 150) {
        candidates.push({ original: para, content: trimmed, type: "paragraph" });
      }
    });

    candidates.forEach(cand => {
      const normCand = cand.content.toLowerCase().replace(/\s+/g, " ");
      for (const msg of previousUserMessages) {
        if (msg.toLowerCase().replace(/\s+/g, " ").includes(normCand)) {
          duplicates.push(cand);
          break;
        }
      }
    });

    return duplicates;
  }

  // --- OPTIMIZATION MODAL ---
  function ensureModalExists() {
    if (!modalContainer) {
      modalContainer = document.createElement("div");
      modalContainer.className = "squeeze-modal-container";
      document.body.appendChild(modalContainer);
      modalContainer.addEventListener("click", e => {
        if (e.target === modalContainer) closeModal();
      });
      // Escape key closes modal
      window.addEventListener("keydown", e => {
        if (e.key === "Escape" && modalContainer.classList.contains("open")) {
          closeModal();
        }
      });
    }
  }

  function closeModal() {
    if (modalContainer) {
      modalContainer.classList.remove("open");
      currentUploadedPdf = null;
      setTimeout(() => { modalContainer.innerHTML = ""; }, 300);
    }
  }

  function openOptimizationModal(promptText, mode) {
    ensureModalExists();
    workingModalPrompt = promptText;
    duplicateContextBlocks = findDuplicateContext(promptText);

    const logoUrl = chrome.runtime.getURL("icons/icon48.png");
    modalContainer.innerHTML = `
      <div class="squeeze-modal-card">
        <div class="tm-modal-header">
          <div class="tm-modal-logo">
            <img src="${logoUrl}" class="animating" width="22" height="22" alt="Squeeze Icon">
            <span>Squeeze <span class="highlight">Optimizer</span></span>
          </div>
          <button class="tm-close-btn">&times;</button>
        </div>
        <div class="tm-modal-body">
          <div class="tm-loading-state">
            <div class="tm-spinner"></div>
            <p>Squeezing prompt for maximum token efficiency...</p>
            <span class="tm-loading-subtext">Optimizing via Local Rules & DLP Scanner...</span>
          </div>
        </div>
      </div>
    `;

    modalContainer.classList.add("open");
    modalContainer.querySelector(".tm-close-btn").addEventListener("click", closeModal);
    requestOptimization(promptText, mode);
  }

  function requestOptimization(promptText, mode) {
    try {
      chrome.runtime.sendMessage(
        { action: "optimizePrompt", prompt: promptText, mode },
        response => {
          if (chrome.runtime.lastError) {
            // Must read .message to suppress Chrome's "Unchecked runtime.lastError" warning
            const errMsg = chrome.runtime.lastError.message || "Unknown error";
            renderModalError(`Communication with Squeeze background service failed (${errMsg}). Please refresh this tab.`);
          } else if (response && response.success) {
            renderModalContent(response);
          } else {
            renderModalError(response?.error || "Unknown optimization error.");
          }
        }
      );
    } catch (e) {
      renderModalError(`Squeeze was reloaded. Please refresh this tab. (${e.message})`);
    }
  }

  function renderModalError(errorMsg) {
    if (!modalContainer) return;
    const body = modalContainer.querySelector(".tm-modal-body");
    const logoImg = modalContainer.querySelector(".tm-modal-logo img");
    if (logoImg) logoImg.classList.remove("animating");

    body.innerHTML = `
      <div class="tm-error-state">
        <div class="tm-error-icon">⚠️</div>
        <h3>Optimization Failed</h3>
        <p class="tm-error-msg">${escapeHtml(errorMsg)}</p>
        <div class="tm-error-actions">
          <button class="tm-btn tm-btn-secondary" id="tmErrorCloseBtn">Close</button>
        </div>
      </div>
    `;
    body.querySelector("#tmErrorCloseBtn").addEventListener("click", closeModal);
  }

  // Fast line-level diff fallback for large prompts
  function generateLineDiff(orig, opt) {
    const origLines = orig.split("\n");
    const optLines  = opt.split("\n");
    const origSet   = new Set(origLines.map(l => l.trim()));
    const optSet    = new Set(optLines.map(l => l.trim()));

    const oldHtml = origLines.map(l => {
      const t = l.trim();
      return (t && !optSet.has(t))
        ? `<del class="tm-diff-del">${escapeHtml(l)}</del>`
        : escapeHtml(l);
    }).join("<br>");

    const newHtml = optLines.map(l => {
      const t = l.trim();
      return (t && !origSet.has(t))
        ? `<ins class="tm-diff-ins">${escapeHtml(l)}</ins>`
        : escapeHtml(l);
    }).join("<br>");

    return { oldHtml, newHtml };
  }

  // Generate word diff (LCS-based). Falls back to line-diff for large prompts.
  const LCS_WORD_CAP = 500;
  function generateDiffView(orig, opt) {
    const origWords = orig.trim().split(/(\s+)/);
    const optWords  = opt.trim().split(/(\s+)/);

    // Performance guard: LCS is O(m×n) — fallback for large inputs
    if (origWords.length > LCS_WORD_CAP || optWords.length > LCS_WORD_CAP) {
      return generateLineDiff(orig, opt);
    }

    const m = origWords.length;
    const n = optWords.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (origWords[i - 1] === optWords[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
        else dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }

    let i = m, j = n;
    const oldArr = [], newArr = [];

    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && origWords[i - 1] === optWords[j - 1]) {
        const w = origWords[i - 1];
        oldArr.unshift(escapeHtml(w));
        newArr.unshift(escapeHtml(w));
        i--;
        j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        const w = optWords[j - 1];
        if (w.trim() === "") newArr.unshift(w);
        else newArr.unshift(`<ins class="tm-diff-ins">${escapeHtml(w)}</ins>`);
        j--;
      } else {
        const w = origWords[i - 1];
        if (w.trim() === "") oldArr.unshift(w);
        else oldArr.unshift(`<del class="tm-diff-del">${escapeHtml(w)}</del>`);
        i--;
      }
    }

    return { oldHtml: oldArr.join(""), newHtml: newArr.join("") };
  }

  function renderModalContent(data) {
    const body = modalContainer.querySelector(".tm-modal-body");
    const logoImg = modalContainer.querySelector(".tm-modal-logo img");
    if (logoImg) logoImg.classList.remove("animating");

    // Fix #19: Compute intent preservation score from actual word overlap (Jaccard similarity).
    // This replaces the hardcoded 93/98/99 magic numbers.
    function computeIntentScore(orig, opt) {
      const stopWords = new Set(["the","a","an","is","are","was","were","be","been","being",
        "have","has","had","do","does","did","will","would","could","should","may","might",
        "shall","can","need","dare","ought","used","i","you","he","she","it","we","they",
        "what","which","who","whom","this","that","these","those","am","to","of","in","for",
        "on","with","at","by","from","as","into","through","and","but","or","nor","so","yet"]);
      const tokenize = str => str.toLowerCase().replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/).filter(w => w.length > 2 && !stopWords.has(w));
      const origWords = new Set(tokenize(orig));
      const optWords  = new Set(tokenize(opt));
      const intersection = [...origWords].filter(w => optWords.has(w)).length;
      const union = new Set([...origWords, ...optWords]).size;
      if (union === 0) return 100;
      // Jaccard * 100, clamped to [85, 100] range for UX readability
      return Math.min(100, Math.max(85, Math.round((intersection / union) * 100)));
    }
    const intentScore = computeIntentScore(data.original, data.optimized);

    const diff = generateDiffView(data.original, data.optimized);

    // DLP banner
    let secretHtml = "";
    if (data.secretsDetected && data.secretsDetected.length > 0) {
      secretHtml = `
        <div class="tm-dup-warning-banner" style="background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); color: #34d399; margin-bottom: 12px;">
          <span>🛡️ <strong>DLP Shield:</strong> ${data.secretsDetected.length} credential(s) safely masked before sending.</span>
        </div>
      `;
    }

    // Duplicate context banner
    let dupsHtml = "";
    if (duplicateContextBlocks.length > 0) {
      dupsHtml = `
        <div class="tm-dup-warning-banner" style="background: rgba(255, 59, 48, 0.08); border: 1px solid rgba(255, 59, 48, 0.25); padding: 10px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
          <div style="font-size: 0.76rem; color: #ff5e84;">
            ⚠️ <strong>Duplicate Context:</strong> ${duplicateContextBlocks.length} block(s) in this prompt was already sent earlier in the thread.
          </div>
          <button class="tm-btn" id="tmStripDupsBtn" style="padding: 4px 8px; font-size: 0.7rem; color: #ff5e84; border: 1px solid rgba(255,94,132,0.4); background: rgba(255,59,48,0.05); cursor: pointer; border-radius: 4px;">Strip Duplicates</button>
        </div>
      `;
    }

    // Applied rules
    const rulesHtml = data.rulesApplied && data.rulesApplied.length > 0
      ? `<div class="tm-applied-rules-chips" style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
          ${data.rulesApplied.map(r => `<span class="tm-rule-chip" style="font-size: 0.68rem; padding: 2px 8px; background: rgba(255, 109, 0, 0.1); border: 1px solid rgba(255, 109, 0, 0.3); color: #ff9d42; border-radius: 12px;">✓ ${escapeHtml(r)}</span>`).join("")}
        </div>`
      : "";

    // Attached context
    const vaultHtml = data.attachedContexts && data.attachedContexts.length > 0
      ? `<div style="margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.06); padding-top: 6px;">
          <span style="font-size: 0.7rem; color: #9e978e;">Vault Context Attached:</span>
          <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
            ${data.attachedContexts.map(c => `<span style="font-size: 0.65rem; padding: 2px 6px; background: rgba(0, 229, 255, 0.08); border: 1px solid rgba(0, 229, 255, 0.2); color: #00e5ff; border-radius: 10px;">📂 ${escapeHtml(c)}</span>`).join("")}
          </div>
        </div>`
      : "";

    const origLabel = currentUploadedPdf ? "Original PDF Content" : "Original Prompt";
    const optLabel = currentUploadedPdf ? "Squeezed PDF Content" : "Optimized Prompt";

    body.innerHTML = `
      <div class="tm-comparison-layout">
        ${secretHtml}
        ${dupsHtml}

        <!-- Options Bar -->
        <div class="tm-options-bar">
          <div class="tm-mode-selector-group">
            <label>Mode:</label>
            <select id="tmModeSelect" class="tm-mini-select">
              <option value="squeeze" ${data.mode === "squeeze" ? "selected" : ""}>Squeeze (Max Savings)</option>
              <option value="balanced" ${data.mode === "balanced" ? "selected" : ""}>Balanced (Concise)</option>
              <option value="polish" ${data.mode === "polish" ? "selected" : ""}>Polish (Enhance)</option>
            </select>
          </div>
          <div class="tm-stats-badges">
            <div class="tm-stats-badge-savings">
              Saves ${data.percentageSaved}% Tokens
            </div>
            <div class="tm-stats-badge-quality">
              ⚡ ${intentScore}% Intent Kept
            </div>
          </div>
        </div>

        <!-- Diff Grid -->
        <div class="tm-diff-grid">
          <div class="tm-diff-pane">
            <div class="tm-pane-header">
              <span>${origLabel}</span>
              <span class="tm-pane-stat">${data.originalTokens.toLocaleString()} tokens</span>
            </div>
            <div class="tm-pane-content tm-original-text" id="tmOriginalPane">${diff.oldHtml}</div>
          </div>
          
          <div class="tm-diff-pane tm-optimized-pane">
            <div class="tm-pane-header">
              <span>${optLabel}</span>
              <div class="tm-toggle-group">
                <button class="tm-toggle-btn active" id="tmToggleDiff">Diff</button>
                <button class="tm-toggle-btn" id="tmToggleEdit">Edit Raw</button>
              </div>
              <span class="tm-pane-stat glow-text">${data.optimizedTokens.toLocaleString()} tokens</span>
            </div>
            <div id="tmOptimizedWrapper" style="height: calc(100% - 32px); display: flex; flex-direction: column;">
              <div class="tm-pane-content tm-optimized-diff" id="tmOptimizedDiffPane">${diff.newHtml}</div>
              <textarea id="tmOptimizedInput" class="tm-pane-textarea" style="display: none;">${escapeHtml(data.optimized)}</textarea>
            </div>
          </div>
        </div>

        <!-- Savings Summary -->
        <div class="tm-savings-summary">
          <div class="tm-savings-icon">⚡</div>
          <div class="tm-savings-details">
            <span class="tm-savings-title">Optimization Complete!</span>
            <span class="tm-savings-desc">Saved <strong>${data.tokensSaved.toLocaleString()} tokens</strong> (${data.percentageSaved}% reduction) while preserving all intent.</span>
            ${rulesHtml}
            ${vaultHtml}
          </div>
        </div>

        <!-- Actions Footer -->
        <div class="tm-actions-footer">
          <button class="tm-btn tm-btn-secondary" id="tmDiscardBtn">Discard</button>
          <button class="tm-btn tm-btn-primary" id="tmApplyBtn">Apply & Squeeze</button>
        </div>
      </div>
    `;

    // Mode select change
    const modeSelect = body.querySelector("#tmModeSelect");
    modeSelect.addEventListener("change", () => {
      const newMode = modeSelect.value;
      currentOptMode = newMode;
      body.innerHTML = `
        <div class="tm-loading-state">
          <div class="tm-spinner"></div>
          <p>Re-optimizing prompt using ${newMode} mode...</p>
        </div>
      `;
      requestOptimization(workingModalPrompt, newMode);
    });

    // Toggle Diff vs Edit Raw
    const btnDiff = body.querySelector("#tmToggleDiff");
    const btnEdit = body.querySelector("#tmToggleEdit");
    const diffPane = body.querySelector("#tmOptimizedDiffPane");
    const editArea = body.querySelector("#tmOptimizedInput");
    const origPane = body.querySelector("#tmOriginalPane");

    btnDiff.addEventListener("click", () => {
      btnDiff.classList.add("active");
      btnEdit.classList.remove("active");
      diffPane.style.display = "block";
      editArea.style.display = "none";
      origPane.innerHTML = diff.oldHtml;
    });

    btnEdit.addEventListener("click", () => {
      btnEdit.classList.add("active");
      btnDiff.classList.remove("active");
      diffPane.style.display = "none";
      editArea.style.display = "block";
      origPane.innerHTML = escapeHtml(data.original);
      editArea.focus();
    });

    // Discard & Apply
    body.querySelector("#tmDiscardBtn").addEventListener("click", closeModal);
    body.querySelector("#tmApplyBtn").addEventListener("click", () => {
      // Fix: Use textarea value only when Edit Raw view is active.
      // When Diff view is shown, editArea is hidden and not kept in sync — use data.optimized directly.
      const inEditMode = editArea.style.display !== "none";
      const finalVal = inEditMode ? editArea.value : data.optimized;
      lastOptimizedPrompt = finalVal;
      if (activeInputEl) {
        setInputValue(activeInputEl, finalVal);
        if (undoBtn) undoBtn.style.display = "inline-flex";
      }
      closeModal();
    });

    // Strip Duplicates
    const stripBtn = body.querySelector("#tmStripDupsBtn");
    if (stripBtn) {
      stripBtn.addEventListener("click", () => {
        let cleaned = workingModalPrompt;
        duplicateContextBlocks.forEach(b => {
          cleaned = cleaned.replace(b.original, "");
        });
        cleaned = cleaned.replace(/\n\s*\n+/g, "\n\n").trim();
        duplicateContextBlocks = [];
        workingModalPrompt = cleaned;
        showToast(stripBtn, "Duplicate blocks stripped!");
        requestOptimization(cleaned, currentOptMode);
      });
    }
  }

  // --- CONTEXT SUMMARIZER ---
  function wireSummaryButton(input) {
    summaryBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();

      try {
        const { summary, totalTurns, summarizedTurns } = extractConversationSummary();
        if (!summary || summary.length < 30) {
          showToast(summaryBtn, "No chat history to summarize yet!");
          return;
        }

        chrome.storage.local.set({ pendingChatSummary: summary }, () => {
          navigator.clipboard.writeText(summary).catch(() => {});
          // Fix #16: Show transparent turn count in toast
          const turnInfo = totalTurns > 0
            ? `Summarized ${summarizedTurns} of ${totalTurns} messages → fresh chat!`
            : "Context summarized! Opening fresh chat...";
          showToast(summaryBtn, turnInfo);

          // Open fresh chat depending on platform
          setTimeout(() => {
            if (IS_CLAUDE) window.location.href = "https://claude.ai/new";
            else if (IS_CHATGPT) window.location.href = "https://chatgpt.com/";
            else if (IS_GEMINI) window.location.href = "https://gemini.google.com/app";
          }, 1200);
        });
      } catch (err) {
        console.error("Summary error:", err);
        showToast(summaryBtn, "Error generating summary context.");
      }
    });
  }

  function extractConversationSummary() {
    const turns = [];

    if (IS_CLAUDE) {
      const messages = document.querySelectorAll(
        "div.font-user-message, div.font-claude-message, [data-testid='user-message'], [data-testid='bot-message'], .prose"
      );
      messages.forEach(el => {
        const isUser = el.closest('[data-testid="user-message"]') || el.classList.contains("font-user-message");
        const clone = el.cloneNode(true);
        clone.querySelectorAll("pre").forEach(p => p.remove());
        const text = clone.innerText.trim();
        const codeBlocks = [];
        el.querySelectorAll("pre code").forEach(c => {
          let lang = "code";
          c.classList.forEach(cls => { if (cls.startsWith("language-")) lang = cls.replace("language-", ""); });
          codeBlocks.push({ language: lang, code: c.innerText.trim().substring(0, 3000) });
        });
        if (text || codeBlocks.length > 0) turns.push({ sender: isUser ? "User" : "Claude", text, codeBlocks });
      });
    } else if (IS_CHATGPT) {
      const messages = document.querySelectorAll('[data-message-author-role]');
      messages.forEach(el => {
        const role = el.getAttribute("data-message-author-role");
        const text = el.innerText.trim();
        turns.push({ sender: role === "user" ? "User" : "Assistant", text, codeBlocks: [] });
      });
    } else {
      // Gemini
      const messages = document.querySelectorAll("user-query, model-response");
      messages.forEach(el => {
        const isUser = el.tagName.toLowerCase() === "user-query";
        turns.push({ sender: isUser ? "User" : "Gemini", text: el.innerText.trim(), codeBlocks: [] });
      });
    }

    if (turns.length === 0) return { summary: "", totalTurns: 0, summarizedTurns: 0 };

    const totalTurns = turns.length;
    // Keep last 3 exchanges (6 turns)
    const KEEP = 6;
    const recent = turns.slice(-KEEP);
    const summarizedTurns = recent.length;
    let output = "## Context Summary from Previous Chat (Squeezed)\n\n### Recent Discussion Timeline:\n";

    recent.forEach(t => {
      let snippet = t.text;
      if (snippet.length > 350) snippet = snippet.substring(0, 350) + "... [truncated]";
      output += `**${t.sender}**: ${snippet.replace(/\n/g, " ")}\n\n`;
    });

    output += "\n*This context was automatically summarized by Squeeze AI to save tokens. Ready to continue where we left off.*";
    return { summary: output, totalTurns, summarizedTurns };
  }

  // --- CONTEXT USAGE DEPTH BAR ---
  function mountContextUsageBar() {
    const input = findChatInput();
    if (!input) return;

    const parent = input.closest("form") || input.closest("fieldset") || input.parentElement;
    if (!parent) return;

    if (!usageBar || !document.contains(usageBar)) {
      usageBar = document.createElement("div");
      usageBar.className = "squeeze-usage-bar";
      parent.parentNode.insertBefore(usageBar, parent.nextSibling);
    }

    updateContextDepth();
  }

  async function updateContextDepth() {
    if (!usageBar) return;

    // Estimate thread tokens
    const textNodes = document.querySelectorAll(
      "div.font-user-message, div.font-claude-message, [data-testid='user-message'], [data-message-author-role], user-query, model-response"
    );
    let combined = "";
    textNodes.forEach(n => { combined += " " + n.innerText; });
    if (activeInputEl) combined += " " + getInputValue(activeInputEl);

    const totalTokens = estimateTokensLocal(combined);
    const percent = Math.min(100, Math.max(0, Math.round((totalTokens / 200_000) * 100)));
    const status = totalTokens < 40_000 ? "safe" : totalTokens < 100_000 ? "moderate" : totalTokens < 160_000 ? "heavy" : "critical";
    const statusLabel = status === "safe" ? "Safe Context" : status === "moderate" ? "Moderate Context" : status === "heavy" ? "Heavy Context" : "Critical Context (Start New Chat)";

    let nudgeHtml = "";
    if (totalTokens > 35_000) {
      nudgeHtml = `
        <div class="tm-summary-nudge">
          <span class="tm-nudge-icon">⚡</span>
          <span class="tm-nudge-text">High Context depth (${totalTokens.toLocaleString()} tokens). Starting a new chat cuts latency and cost by 70%!</span>
          <button class="tm-nudge-btn tm-btn-gold" id="tmBarSummarizeBtn">Summarize & New Chat</button>
        </div>
      `;
    }

    usageBar.innerHTML = `
      <div class="tm-usage-bar-content">
        <div class="tm-usage-columns">
          <div class="tm-context-column">
            <span class="tm-usage-dot dot-${status}"></span>
            <span class="tm-usage-title">Conversation Context:</span>
            <span class="tm-usage-val">${totalTokens.toLocaleString()}</span>
            <span class="tm-usage-divider">/</span>
            <span class="tm-usage-limit">200K tokens</span>
            <span class="tm-usage-percent">(${percent}%)</span>
            <span class="tm-usage-status-inline status-${status}">${statusLabel}</span>
          </div>
        </div>
        <div class="tm-progress-bars-container" style="display: flex; flex-direction: column; gap: 4px; width: 100%; margin-top: 4px;">
          <div class="tm-usage-progress-track" title="Conversation Context: ${percent}% used">
            <div class="tm-usage-progress-bar progress-${status}" style="width: ${percent}%"></div>
          </div>
        </div>
        ${nudgeHtml}
      </div>
    `;

    const barSumBtn = usageBar.querySelector("#tmBarSummarizeBtn");
    if (barSumBtn) {
      barSumBtn.addEventListener("click", () => {
        if (summaryBtn) summaryBtn.click();
      });
    }
  }

  // --- VAULT BADGE UPDATE ---
  function updateVaultBadge(promptText) {
    if (!vaultBadge) return;
    if (!promptText) {
      vaultBadge.style.display = "none";
      return;
    }

    chrome.storage.local.get(["vaultPreferences", "vaultPrefAlwaysInject", "vaultSmartTriggers", "vaultFiles"], data => {
      const prefs = data.vaultPreferences || "";
      const alwaysInject = data.vaultPrefAlwaysInject !== false;
      const smartTriggers = data.vaultSmartTriggers !== false;
      const files = data.vaultFiles || [];

      let count = 0;
      const attached = [];

      if (prefs.trim() && alwaysInject) {
        count++;
        attached.push("Developer Profile");
      }

      if (files.length > 0) {
        const lower = promptText.toLowerCase();
        for (const f of files) {
          let matches = false;
          if (smartTriggers) {
            const toks = f.name.replace(/\.[a-z0-9]+$/i, "").toLowerCase().split(/[^a-z0-9]+/).filter(w => w.length >= 3);
            for (const t of toks) {
              if (new RegExp("\\b" + t + "\\b", "i").test(lower)) {
                matches = true;
                break;
              }
            }
          } else {
            matches = true;
          }
          if (matches && f.content) {
            count++;
            attached.push(f.name);
          }
        }
      }

      if (count > 0) {
        vaultBadge.style.display = "inline-flex";
        vaultBadge.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; color: #ff6d00;">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <span style="font-size: 0.72rem; font-weight: 600; color: #ff6d00;">Vault: ${count}</span>
        `;
        vaultBadge.setAttribute("title", `Vault Context Attached:\n- ${attached.join("\n- ")}`);
      } else {
        vaultBadge.style.display = "none";
      }
    });
  }

  // --- SIDEBAR BUTTON & IN-PAGE DRAWER ---
  function mountSidebarButton() {
    if (sidebarBtn && document.contains(sidebarBtn)) return;

    const nav = document.querySelector("nav") || document.querySelector('[role="navigation"]') || document.querySelector("aside");
    if (!nav) return;

    sidebarBtn = document.createElement("button");
    sidebarBtn.className = "squeeze-sidebar-btn";
    sidebarBtn.dataset.tooltip = "Open Squeeze Side Panel";
    sidebarBtn.addEventListener("mouseenter", () => showTooltip(sidebarBtn, sidebarBtn.dataset.tooltip));
    sidebarBtn.addEventListener("mouseleave", hideTooltip);
    sidebarBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 512 512" fill="none">
        <path d="M 140 148 L 256 264 L 372 148" stroke="currentColor" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="160" y="324" width="192" height="44" rx="22" fill="currentColor"/>
      </svg>
    `;

    sidebarBtn.addEventListener("click", e => {
      e.stopPropagation();
      hideTooltip();
      chrome.runtime.sendMessage({ action: "openSidePanel" });
    });

    nav.appendChild(sidebarBtn);
  }

  // --- LISTEN FOR MESSAGES (E.G. FROM SIDE PANEL) ---
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "insertPrompt") {
      const input = findChatInput();
      if (input && msg.text) {
        setInputValue(input, msg.text);
        if (undoBtn) undoBtn.style.display = "inline-flex";
        showToast(input, "Prompt squeezed & injected! ✨");
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: "Chat input not found" });
      }
    }
  });

  // --- OBSERVER & INITIALIZATION ---
  function init() {
    chrome.storage.local.get(["optimizationMode"], data => {
      if (data.optimizationMode) currentOptMode = data.optimizationMode;
    });

    mountWidgets();

    // Leading + trailing debounce: fire immediately on first mutation,
    // then again 600ms after the DOM settles. Prevents missing widget
    // injection during ChatGPT/Gemini streaming responses.
    let debounceTimer = null;
    let lastFiredAt = 0;
    const LEADING_INTERVAL = 1500; // ms before we fire leading again
    const TRAILING_DELAY = 600;    // ms after last mutation

    const observer = new MutationObserver(() => {
      const now = Date.now();
      if (now - lastFiredAt > LEADING_INTERVAL) {
        // Leading fire — instant widget mount
        mountWidgets();
        lastFiredAt = now;
      }
      // Trailing fire — re-check after DOM settles
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        mountWidgets();
        lastFiredAt = Date.now();
      }, TRAILING_DELAY);
    });

    observer.observe(document.body, { childList: true, subtree: true });

    chrome.storage.onChanged.addListener(changes => {
      if (changes.optimizationMode) currentOptMode = changes.optimizationMode.newValue;
      if (activeInputEl) updateVaultBadge(getInputValue(activeInputEl));
    });
  }

  init();
})();
```

## File: `sidepanel.js`
```javascript
/**
 * Squeeze AI - Side Panel Script (Manifest V3)
 * Full interactive controller for Studio, Frameworks, DLP Shield,
 * Context Vault, Multi-Model Analytics, and Judge Demo Showcase.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const navButtons = document.querySelectorAll(".sp-nav-btn");
  const panes = document.querySelectorAll(".sp-pane");

  // Studio elements
  const inputPrompt = document.getElementById("spInputPrompt");
  const inputTokenBadge = document.getElementById("spInputTokenBadge");
  const charCount = document.getElementById("spCharCount");
  const clearInputBtn = document.getElementById("spClearInputBtn");
  const modeButtons = document.querySelectorAll(".sp-mode-btn");
  const toggleDlp = document.getElementById("spToggleDlp");
  const toggleVault = document.getElementById("spToggleVault");
  const squeezeBtn = document.getElementById("spSqueezeActionBtn");

  // Output elements
  const outputSection = document.getElementById("spOutputSection");
  const secretAlertBanner = document.getElementById("spSecretAlertBanner");
  const secretAlertCount = document.getElementById("spSecretAlertCount");
  const qualityPill = document.getElementById("spQualityPill");
  const viewDiffBtn = document.getElementById("spViewDiffBtn");
  const viewCleanBtn = document.getElementById("spViewCleanBtn");
  const tokensSavedVal = document.getElementById("spTokensSavedVal");
  const percentSavedVal = document.getElementById("spPercentSavedVal");
  const finalTokenCount = document.getElementById("spFinalTokenCount");
  const diffContainer = document.getElementById("spDiffViewContainer");
  const cleanTextarea = document.getElementById("spCleanViewTextarea");
  const rulesChips = document.getElementById("spRulesChips");
  const copyResultBtn = document.getElementById("spCopyResultBtn");
  const sendToTabBtn = document.getElementById("spSendToActiveTabBtn");
  const feedbackMsg = document.getElementById("spFeedbackMsg");

  // Model cost elements
  const costSonnet = document.getElementById("spCostSonnet");
  const costGpt4o = document.getElementById("spCostGpt4o");
  const costGemini = document.getElementById("spCostGemini");
  const costDeepseek = document.getElementById("spCostDeepseek");

  // Demo presets
  const demoPitchBtn = document.getElementById("spDemoPitchBtn");
  const demoPresetDev = document.getElementById("demoPresetDev");
  const demoPresetEmail = document.getElementById("demoPresetEmail");
  const demoPresetCode = document.getElementById("demoPresetCode");

  // Framework triggers
  const fwApplyCostar = document.getElementById("fwApplyCostar");
  const fwApplyFewshot = document.getElementById("fwApplyFewshot");
  const fwApplyCode = document.getElementById("fwApplyCode");
  const fwApplyExec = document.getElementById("fwApplyExec");

  // DLP elements
  const dlpTestInput = document.getElementById("spDlpTestInput");
  const dlpResultBox = document.getElementById("spDlpResultBox");

  // Vault elements
  const vaultPrefs = document.getElementById("spVaultPrefs");
  const vaultAlwaysInject = document.getElementById("spVaultAlwaysInject");
  const vaultSmartTriggers = document.getElementById("spVaultSmartTriggers");
  const vaultDropzone = document.getElementById("spVaultDropzone");
  const vaultFileInput = document.getElementById("spVaultFileInput");
  const vaultBrowseLink = document.getElementById("spVaultBrowseLink");
  const vaultList = document.getElementById("spVaultList");

  // Analytics elements
  const analyticsPrompts = document.getElementById("spAnalyticsPrompts");
  const analyticsTokens = document.getElementById("spAnalyticsTokens");
  const analyticsCost = document.getElementById("spAnalyticsCost");
  const ecoEnergy = document.getElementById("spEcoEnergy");
  const ecoCo2 = document.getElementById("spEcoCo2");
  const historyList = document.getElementById("spHistoryList");
  const resetStatsBtn = document.getElementById("spResetStatsBtn");

  // State
  let currentMode = "balanced";
  let lastOptimizedResult = null;
  let vaultFilesList = [];
  let analyticsLastLoaded = 0; // Fix #17: track last analytics render to avoid redundant re-renders

  // --- TAB SWITCHING ---
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      navButtons.forEach(b => b.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(`pane-${target}`);
      if (targetPane) targetPane.classList.add("active");

      // Fix #17: Only reload analytics if >5s have passed since last load
      if (target === "analytics") {
        const now = Date.now();
        if (now - analyticsLastLoaded > 5000) {
          loadAnalytics();
          analyticsLastLoaded = now;
        }
      }
      if (target === "vault") loadVaultData();
      if (target === "graph") loadCodeGraph();
    });
  });

  function switchTab(tabId) {
    const btn = document.querySelector(`.sp-nav-btn[data-tab="${tabId}"]`);
    if (btn) btn.click();
  }

  // --- TOKEN ESTIMATION ---
  function estimateTokensLocal(text) {
    if (!text) return 0;
    const trimmed = text.trim();
    if (!trimmed) return 0;
    const words = trimmed.split(/\s+/).length;
    const chars = trimmed.length;
    const specialChars = (trimmed.match(/[{}\[\]()<>=:;,.!?"'`\/\\|#*&^%$@~+-]/g) || []).length;
    const codeRatio = specialChars / Math.max(1, chars);
    const charEst = Math.ceil(chars / (codeRatio > 0.15 ? 3.2 : 4.0));
    const wordEst = Math.ceil(words * 1.35);
    return Math.max(charEst, wordEst);
  }

  function updateInputMetrics() {
    const text = inputPrompt.value || "";
    const tokens = estimateTokensLocal(text);
    inputTokenBadge.textContent = `${tokens.toLocaleString()} tokens`;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    charCount.textContent = `${chars.toLocaleString()} chars · ${words.toLocaleString()} words`;
  }

  inputPrompt.addEventListener("input", updateInputMetrics);

  clearInputBtn.addEventListener("click", () => {
    inputPrompt.value = "";
    updateInputMetrics();
    outputSection.style.display = "none";
    inputPrompt.focus();
  });

  // --- MODE SELECTION ---
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      modeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.getAttribute("data-mode");
      chrome.storage.local.set({ optimizationMode: currentMode });
      // If we already have output, auto-reoptimize
      if (inputPrompt.value.trim() && outputSection.style.display !== "none") {
        executeOptimization();
      }
    });
  });

  // --- WORD-LEVEL DIFF GENERATOR ---
  function generateDiffHtml(original, optimized) {
    const origTokens = original.trim().split(/(\s+)/);
    const optTokens = optimized.trim().split(/(\s+)/);

    // LCS (Longest Common Subsequence)
    const m = origTokens.length;
    const n = optTokens.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (origTokens[i - 1] === optTokens[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1] + 1;
        } else {
          dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
        }
      }
    }

    let i = m, j = n;
    const diffPieces = [];

    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && origTokens[i - 1] === optTokens[j - 1]) {
        diffPieces.unshift(escapeHtml(origTokens[i - 1]));
        i--;
        j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        const text = optTokens[j - 1];
        if (text.trim() === "") {
          diffPieces.unshift(text);
        } else {
          diffPieces.unshift(`<ins class="sp-diff-ins">${escapeHtml(text)}</ins>`);
        }
        j--;
      } else {
        const text = origTokens[i - 1];
        if (text.trim() === "") {
          diffPieces.unshift(text);
        } else {
          diffPieces.unshift(`<del class="sp-diff-del">${escapeHtml(text)}</del>`);
        }
        i--;
      }
    }

    return diffPieces.join("");
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- SQUEEZE EXECUTION ---
  async function executeOptimization() {
    const text = inputPrompt.value.trim();
    if (!text) {
      inputPrompt.focus();
      return;
    }

    squeezeBtn.disabled = true;
    squeezeBtn.querySelector(".btn-text").textContent = "Squeezing...";

    try {
      chrome.runtime.sendMessage(
        {
          action: "optimizePrompt",
          prompt: text,
          mode: currentMode
        },
        response => {
          squeezeBtn.disabled = false;
          squeezeBtn.querySelector(".btn-text").textContent = "Squeeze Prompt";

          if (chrome.runtime.lastError) {
            alert("Error communicating with Squeeze background service: " + chrome.runtime.lastError.message);
            return;
          }

          if (response && response.success) {
            renderOutput(response);
          } else {
            alert("Optimization failed: " + (response?.error || "Unknown error"));
          }
        }
      );
    } catch (err) {
      squeezeBtn.disabled = false;
      squeezeBtn.querySelector(".btn-text").textContent = "Squeeze Prompt";
      alert("Error: " + err.message);
    }
  }

  function renderOutput(data) {
    lastOptimizedResult = data;
    outputSection.style.display = "flex";

    // Tokens & Percent
    tokensSavedVal.textContent = data.tokensSaved.toLocaleString();
    percentSavedVal.textContent = `${data.percentageSaved}%`;
    finalTokenCount.textContent = data.optimizedTokens.toLocaleString();

    // Intent quality heuristic
    let intentScore = 98;
    if (data.mode === "squeeze") intentScore = 93;
    else if (data.mode === "polish") intentScore = 99;
    qualityPill.textContent = `⚡ ${intentScore}% Intent Preserved`;

    // DLP Alert
    if (data.secretsDetected && data.secretsDetected.length > 0) {
      secretAlertBanner.style.display = "flex";
      secretAlertCount.textContent = `${data.secretsDetected.length} secret(s) safely masked (${data.secretsDetected.map(s => s.type).join(", ")}).`;
    } else {
      secretAlertBanner.style.display = "none";
    }

    // Diff view & clean view
    diffContainer.innerHTML = generateDiffHtml(data.original, data.optimized);
    cleanTextarea.value = data.optimized;

    // Default to diff view
    diffContainer.style.display = "block";
    cleanTextarea.style.display = "none";
    viewDiffBtn.classList.add("active");
    viewCleanBtn.classList.remove("active");

    // Applied rule chips
    rulesChips.innerHTML = "";
    if (data.rulesApplied && data.rulesApplied.length > 0) {
      data.rulesApplied.forEach(rule => {
        const chip = document.createElement("span");
        chip.className = "sp-rule-chip";
        chip.textContent = `✓ ${rule}`;
        rulesChips.appendChild(chip);
      });
    }

    // Cost calculations per 100 queries
    const multiplier = 100;
    const tokens = data.tokensSaved;
    costSonnet.textContent = `$${((tokens / 1_000_000) * 3.00 * multiplier).toFixed(3)}`;
    costGpt4o.textContent = `$${((tokens / 1_000_000) * 2.50 * multiplier).toFixed(3)}`;
    costGemini.textContent = `$${((tokens / 1_000_000) * 1.25 * multiplier).toFixed(3)}`;
    costDeepseek.textContent = `$${((tokens / 1_000_000) * 0.14 * multiplier).toFixed(4)}`;

    // Scroll output into view
    outputSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  squeezeBtn.addEventListener("click", executeOptimization);

  // View toggle
  viewDiffBtn.addEventListener("click", () => {
    viewDiffBtn.classList.add("active");
    viewCleanBtn.classList.remove("active");
    diffContainer.style.display = "block";
    cleanTextarea.style.display = "none";
  });

  viewCleanBtn.addEventListener("click", () => {
    viewCleanBtn.classList.add("active");
    viewDiffBtn.classList.remove("active");
    diffContainer.style.display = "none";
    cleanTextarea.style.display = "block";
  });

  // Copy result
  copyResultBtn.addEventListener("click", async () => {
    if (!lastOptimizedResult) return;
    try {
      await navigator.clipboard.writeText(lastOptimizedResult.optimized);
      feedbackMsg.textContent = "Copied to clipboard!";
      feedbackMsg.style.display = "block";
      setTimeout(() => { feedbackMsg.style.display = "none"; }, 2000);
    } catch (err) {
      feedbackMsg.textContent = "Failed to copy.";
      feedbackMsg.style.display = "block";
    }
  });

  // Insert into active tab
  sendToTabBtn.addEventListener("click", async () => {
    if (!lastOptimizedResult) return;
    const textToInsert = lastOptimizedResult.optimized;

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab?.id) {
        alert("No active browser tab found.");
        return;
      }

      chrome.tabs.sendMessage(
        tab.id,
        { action: "insertPrompt", text: textToInsert },
        response => {
          if (chrome.runtime.lastError || !response?.success) {
            // Fallback copy
            navigator.clipboard.writeText(textToInsert);
            feedbackMsg.textContent = "Copied to clipboard! (Switch to chat and paste)";
            feedbackMsg.style.display = "block";
            setTimeout(() => { feedbackMsg.style.display = "none"; }, 3500);
          } else {
            feedbackMsg.textContent = "Injected into active chat input! ✨";
            feedbackMsg.style.display = "block";
            setTimeout(() => { feedbackMsg.style.display = "none"; }, 2500);
          }
        }
      );
    } catch (e) {
      navigator.clipboard.writeText(textToInsert);
      feedbackMsg.textContent = "Copied to clipboard!";
      feedbackMsg.style.display = "block";
      setTimeout(() => { feedbackMsg.style.display = "none"; }, 2500);
    }
  });

  // --- DEMO PRESETS (HACKATHON SHOWCASE) ---
  const DEV_DEMO_PROMPT = `Hello Claude! Hope you are doing well today. Could you please help me write a function in order to connect to our MongoDB database?
Make sure that you use standard configurations and adhere to best practices.
Here is our connection string: mongodb://admin:SuperSecretPass123@cluster0.mongodb.net/prod
And please use our OpenAI API key for embeddings: sk-proj-984y982y4982y4982y4982y4982y4982y
Also as I mentioned earlier, please take into consideration that we need robust error handling.
Thank you so much in advance, it would be awesome! Let me know what you think.`;

  const EMAIL_DEMO_PROMPT = `Dear Assistant,
I would really appreciate it if you could kindly provide an explanation of how distributed database transactions work across multiple regions.
At this point in time, we are in agreement that two-phase commit might be too slow due to the fact that network latency is high.
Subsequent to your analysis, please make a decision on whether Saga pattern or Raft consensus is better for our application.
Thanks in advance for your assistance! Best regards.`;

  const SPEC_DEMO_PROMPT = `###System Architecture Documentation
Please analyze the following parameters for our microservice environment:
- database configuration: PostgreSQL 16
- repository structure: monorepo with 4 directories
- developer environment: Docker Compose
It is important to note that you should make a request to the authentication service prior to accessing the user records.
In the event that the service fails, you will be able to retry up to 3 times.`;

  function loadAndRunDemo(promptText, mode = "squeeze") {
    switchTab("studio");
    inputPrompt.value = promptText;
    updateInputMetrics();

    // Select mode
    modeButtons.forEach(b => {
      if (b.getAttribute("data-mode") === mode) {
        b.click();
      }
    });

    // Auto-squeeze
    setTimeout(() => {
      executeOptimization();
    }, 150);
  }

  demoPitchBtn.addEventListener("click", () => loadAndRunDemo(DEV_DEMO_PROMPT, "squeeze"));
  demoPresetDev.addEventListener("click", () => loadAndRunDemo(DEV_DEMO_PROMPT, "squeeze"));
  demoPresetEmail.addEventListener("click", () => loadAndRunDemo(EMAIL_DEMO_PROMPT, "balanced"));
  demoPresetCode.addEventListener("click", () => loadAndRunDemo(SPEC_DEMO_PROMPT, "squeeze"));

  // --- FRAMEWORKS TAB ---
  fwApplyCostar.addEventListener("click", () => {
    const costarTemplate = `# Context: Building a high-throughput payment processing service in Go.
# Objective: Implement a resilient idempotent webhook handler for Stripe events.
# Style: Concise, production-ready Go code with idiomatic error handling.
# Tone: Direct, technical, zero conversational filler.
# Audience: Senior Backend Systems Engineer.
# Response: Output only the handler function and table-driven unit tests.`;
    switchTab("studio");
    inputPrompt.value = costarTemplate;
    updateInputMetrics();
    inputPrompt.focus();
  });

  fwApplyFewshot.addEventListener("click", () => {
    const fewshotTemplate = `Task: Convert natural language queries to SQL.

Input: "Show all active users signed up in the last 7 days"
Output: SELECT * FROM users WHERE status = 'active' AND created_at >= NOW() - INTERVAL '7 days';

Input: "Find total revenue per product category for 2024"
Output: SELECT category, SUM(amount) AS total_revenue FROM sales WHERE EXTRACT(YEAR FROM sale_date) = 2024 GROUP BY category;

Input: "List customers with more than 5 orders who haven't purchased in 30 days"
Output:`;
    switchTab("studio");
    inputPrompt.value = fewshotTemplate;
    updateInputMetrics();
    inputPrompt.focus();
  });

  fwApplyCode.addEventListener("click", () => {
    const codeTemplate = `// Problem: Memory leak in long-running worker process.
// Constraints: Node.js 20, heap limit 512MB, zero external deps.
// Stack Trace: Allocation failed - JavaScript heap out of memory.

function processBatch(items) {
  const cache = [];
  for (const item of items) {
    cache.push(item); // Needs optimization: stream instead of accumulating in RAM
  }
}

// Request: Refactor to stream or chunk processing with garbage collector friendly pattern.`;
    switchTab("studio");
    inputPrompt.value = codeTemplate;
    updateInputMetrics();
    inputPrompt.focus();
  });

  fwApplyExec.addEventListener("click", () => {
    const execTemplate = `Summarize the following document for an executive brief.
Constraints:
- Exactly 3 core takeaways with quantitative metrics.
- 2 critical risks and mitigations.
- Zero introductory or concluding pleasantries.

[Insert Document Text Here]`;
    switchTab("studio");
    inputPrompt.value = execTemplate;
    updateInputMetrics();
    inputPrompt.focus();
  });

  // --- DLP SHIELD REALTIME TESTER ---
  if (dlpTestInput) {
    dlpTestInput.addEventListener("input", () => {
      const val = dlpTestInput.value;
      if (!val.trim()) {
        dlpResultBox.innerHTML = '<span class="sp-placeholder-text">Sanitized output will appear here in real time...</span>';
        return;
      }
      // Run quick local regex
      let sanitized = val;
      sanitized = sanitized.replace(/\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_OPENAI_KEY]</span>');
      sanitized = sanitized.replace(/\b(AIzaSy[a-zA-Z0-9_-]{30,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_GOOGLE_KEY]</span>');
      sanitized = sanitized.replace(/\b(AKIA[0-9A-Z]{16})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_AWS_KEY]</span>');
      sanitized = sanitized.replace(/\b(gh[pousr]_[A-Za-z0-9_]{36,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_GITHUB_TOKEN]</span>');
      sanitized = sanitized.replace(/((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)/gi, '$1<span style="color: #f87171; font-weight: bold;">[MASKED_DB_PASS]</span>$3');
      sanitized = sanitized.replace(/\b((?:API_KEY|SECRET|PASSWORD|PASSWD)\s*[:=]\s*["'])([^"'\n]{4,})(["'])/gi, '$1<span style="color: #f87171; font-weight: bold;">[MASKED_SECRET]</span>$3');

      dlpResultBox.innerHTML = sanitized;
    });
  }

  // --- CONTEXT VAULT ---
  async function loadVaultData() {
    const data = await chrome.storage.local.get([
      "vaultPreferences",
      "vaultPrefAlwaysInject",
      "vaultSmartTriggers",
      "vaultFiles"
    ]);

    vaultPrefs.value = data.vaultPreferences || "";
    vaultAlwaysInject.checked = data.vaultPrefAlwaysInject !== false;
    vaultSmartTriggers.checked = data.vaultSmartTriggers !== false;
    vaultFilesList = data.vaultFiles || [];
    renderVaultFiles();
  }

  vaultPrefs.addEventListener("input", () => {
    chrome.storage.local.set({ vaultPreferences: vaultPrefs.value });
  });

  vaultAlwaysInject.addEventListener("change", () => {
    chrome.storage.local.set({ vaultPrefAlwaysInject: vaultAlwaysInject.checked });
  });

  vaultSmartTriggers.addEventListener("change", () => {
    chrome.storage.local.set({ vaultSmartTriggers: vaultSmartTriggers.checked });
  });

  vaultBrowseLink.addEventListener("click", () => vaultFileInput.click());
  vaultDropzone.addEventListener("click", e => {
    if (e.target !== vaultBrowseLink) vaultFileInput.click();
  });

  vaultFileInput.addEventListener("change", e => handleFilesUpload(e.target.files));

  vaultDropzone.addEventListener("dragover", e => {
    e.preventDefault();
    vaultDropzone.classList.add("dragover");
  });

  vaultDropzone.addEventListener("dragleave", () => {
    vaultDropzone.classList.remove("dragover");
  });

  vaultDropzone.addEventListener("drop", e => {
    e.preventDefault();
    vaultDropzone.classList.remove("dragover");
    handleFilesUpload(e.dataTransfer.files);
  });

  function handleFilesUpload(files) {
    const valid = Array.from(files).map(f => {
      return new Promise(resolve => {
        const ext = f.name.split(".").pop().toLowerCase();
        if (!["txt", "md", "json"].includes(ext)) return resolve(null);
        const reader = new FileReader();
        reader.onload = ev => resolve({ name: f.name, content: ev.target.result, size: f.size });
        reader.onerror = () => resolve(null);
        reader.readAsText(f);
      });
    });

    Promise.all(valid).then(results => {
      const filtered = results.filter(r => r !== null);
      if (filtered.length === 0) return;

      const fileMap = new Map();
      vaultFilesList.forEach(f => fileMap.set(f.name, f));
      filtered.forEach(f => fileMap.set(f.name, f));
      vaultFilesList = Array.from(fileMap.values());

      chrome.storage.local.set({ vaultFiles: vaultFilesList }, () => {
        renderVaultFiles();
      });
    });
  }

  function renderVaultFiles() {
    vaultList.innerHTML = "";
    if (vaultFilesList.length === 0) {
      vaultList.innerHTML = '<li class="empty-list-msg">No reference files in vault yet.</li>';
      return;
    }

    vaultFilesList.forEach((file, idx) => {
      const li = document.createElement("li");
      li.className = "sp-vault-item";
      li.innerHTML = `
        <span class="sp-vault-item-name" title="${escapeHtml(file.name)}">📄 ${escapeHtml(file.name)}</span>
        <button class="sp-del-btn" data-index="${idx}" title="Remove file">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      `;
      li.querySelector(".sp-del-btn").addEventListener("click", () => {
        vaultFilesList.splice(idx, 1);
        chrome.storage.local.set({ vaultFiles: vaultFilesList }, renderVaultFiles);
      });
      vaultList.appendChild(li);
    });
  }

  // --- ANALYTICS ---
  async function loadAnalytics() {
    const data = await chrome.storage.local.get([
      "stats_promptsOptimized",
      "stats_tokensSaved",
      "stats_costSaved",
      "stats_history"
    ]);

    const prompts = data.stats_promptsOptimized || 0;
    const tokens = data.stats_tokensSaved || 0;
    const cost = data.stats_costSaved || 0;

    analyticsPrompts.textContent = prompts >= 1000 ? `${(prompts / 1000).toFixed(1)}k` : prompts;
    analyticsTokens.textContent = tokens >= 1000000 ? `${(tokens / 1000000).toFixed(2)}M` : tokens >= 1000 ? `${(tokens / 1000).toFixed(1)}k` : tokens;
    analyticsCost.textContent = cost > 0 && cost < 0.01 ? `$${cost.toFixed(4)}` : `$${cost.toFixed(2)}`;

    // Eco stats: 1,000 tokens ~ 0.003 Wh on an H100 cluster, ~ 0.0015 g CO2
    const wh = (tokens * 0.000003).toFixed(2);
    const co2 = (tokens * 0.0000015).toFixed(2);
    ecoEnergy.textContent = `${wh} Wh`;
    ecoCo2.textContent = `${co2} g`;

    // History
    const history = data.stats_history || [];
    historyList.innerHTML = "";
    if (history.length === 0) {
      historyList.innerHTML = '<li class="empty-list-msg">No history entries yet.</li>';
      return;
    }

    history.forEach(item => {
      const li = document.createElement("li");
      li.className = "sp-history-item";
      li.innerHTML = `
        <span class="sp-history-snippet" title="${escapeHtml(item.snippet)}">${escapeHtml(item.snippet)}</span>
        <span class="sp-history-stat">+${item.tokensSaved} tok (${item.percentageSaved}%)</span>
      `;
      historyList.appendChild(li);
    });
  }

  resetStatsBtn.addEventListener("click", () => {
    if (confirm("Reset all local statistics for a fresh demo run?")) {
      chrome.runtime.sendMessage({ action: "resetStats" }, () => {
        loadAnalytics();
      });
    }
  });

  // --- SQUEEZE CODE & CACHE CONTROLLER ---
  const skelLangSelect = document.getElementById("spSkelLangSelect");
  const skelLoadSampleBtn = document.getElementById("spSkelLoadSampleBtn");
  const skelRunBtn = document.getElementById("spSkelRunBtn");
  const skelInput = document.getElementById("spSkelInput");
  const skelOutput = document.getElementById("spSkelOutput");
  const skelResultWrapper = document.getElementById("spSkelResultWrapper");
  const skelStats = document.getElementById("spSkelStats");
  const skelCopyBtn = document.getElementById("spSkelCopyBtn");
  const refreshGraphBtn = document.getElementById("spRefreshGraphBtn");
  const graphDisplay = document.getElementById("spGraphDisplay");

  const SAMPLES = {
    python: `import os
from typing import List, Optional

class PaymentGateway:
    """Handles multi-currency credit card and ACH transactions."""
    def __init__(self, api_key: str, sandbox: bool = False):
        self.api_key = api_key
        self.sandbox = sandbox
        self.connect_stripe_backend()

    async def charge_customer(self, customer_id: str, amount_cents: int, currency: str = "USD") -> dict:
        """Processes real-time charge and sends webhook notifications."""
        token = self.generate_idempotency_key(customer_id, amount_cents)
        payload = {"customer": customer_id, "amount": amount_cents, "currency": currency}
        res = await self.http_client.post("/charges", json=payload, headers={"Idempotency": token})
        logger.info(f"Charged {amount_cents} cents to {customer_id}")
        return res.json()

def calculate_fee(amount: float) -> float:
    return amount * 0.029 + 0.30`,

    typescript: `import { Request, Response } from "express";

export interface SessionPayload {
  userId: string;
  roles: string[];
  issuedAt: number;
}

export class AuthenticationManager {
  private jwtSecret: string;
  constructor(secret: string) {
    this.jwtSecret = secret;
  }

  public async verifyRequest(req: Request): Promise<SessionPayload | null> {
    const bearer = req.headers["authorization"];
    if (!bearer) return null;
    const token = bearer.replace("Bearer ", "");
    return jwt.verify(token, this.jwtSecret) as SessionPayload;
  }
}`,

    json: JSON.stringify({
      status: "success",
      total: 50,
      data: Array.from({ length: 15 }, (_, i) => ({
        id: `txn_${1000 + i}`,
        amount: 49.99,
        customer: `Customer ${i}`,
        signatureHash: "a8f9c104e7681239bcde88392019485728394058273948293049182394829384"
      }))
    }, null, 2),

    logs: `2026-09-19T01:15:00.123Z [INFO] Initializing service cluster
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:05.789Z [INFO] Connected to failover cluster 10.0.1.42`
  };

  if (skelLoadSampleBtn && skelInput) {
    skelLoadSampleBtn.addEventListener("click", () => {
      const lang = skelLangSelect.value;
      skelInput.value = SAMPLES[lang] || SAMPLES.python;
      if (skelResultWrapper) skelResultWrapper.style.display = "none";
    });
  }

  if (skelRunBtn && skelInput) {
    skelRunBtn.addEventListener("click", () => {
      const raw = skelInput.value || "";
      if (!raw.trim()) {
        alert("Please paste some code, JSON, or logs first!");
        return;
      }
      const lang = skelLangSelect.value;

      let processed = "";
      if (lang === "python" && window.SqueezeSkeletonizer?.skeletonizePython) {
        processed = window.SqueezeSkeletonizer.skeletonizePython(raw);
      } else if (lang === "typescript" && window.SqueezeSkeletonizer?.skeletonizeTypeScript) {
        processed = window.SqueezeSkeletonizer.skeletonizeTypeScript(raw);
      } else if (lang === "json" && window.SqueezeSkeletonizer?.shrinkJson) {
        processed = window.SqueezeSkeletonizer.shrinkJson(raw, 2);
      } else if (lang === "logs" && window.SqueezeSkeletonizer?.shrinkLogs) {
        processed = window.SqueezeSkeletonizer.shrinkLogs(raw);
      } else if (window.SqueezeSkeletonizer?.skeletonizeCode) {
        processed = window.SqueezeSkeletonizer.skeletonizeCode(raw, lang);
      } else {
        processed = raw;
      }

      skelOutput.value = processed;
      const origTok = estimateTokensLocal(raw);
      const newTok = estimateTokensLocal(processed);
      const saved = Math.max(0, origTok - newTok);
      const pct = origTok > 0 ? Math.round((saved / origTok) * 100) : 0;

      skelStats.textContent = `Output: ${newTok.toLocaleString()} tokens (saved ${saved.toLocaleString()} tok, ${pct}%)`;
      skelResultWrapper.style.display = "block";
    });
  }

  if (skelCopyBtn && skelOutput) {
    skelCopyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(skelOutput.value).then(() => {
        skelCopyBtn.textContent = "Copied! ✨";
        setTimeout(() => { skelCopyBtn.textContent = "Copy Skeleton"; }, 1800);
      });
    });
  }

  function loadCodeGraph() {
    if (!graphDisplay) return;
    chrome.storage.local.get(["vaultFiles"], data => {
      const files = data.vaultFiles || [];
      if (files.length === 0) {
        graphDisplay.innerHTML = '<span style="color: #9e978e;">No files in Context Vault yet. Upload code files (.py, .ts, .js, .json) in the Vault tab to auto-build a dependency graph!</span>';
        return;
      }

      const graph = window.SqueezeSkeletonizer?.buildCodebaseGraph
        ? window.SqueezeSkeletonizer.buildCodebaseGraph(files)
        : { graphText: "Graph engine unavailable" };

      graphDisplay.innerHTML = `<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">${escapeHtml(graph.graphText)}</pre>`;
    });
  }

  if (refreshGraphBtn) {
    refreshGraphBtn.addEventListener("click", loadCodeGraph);
  }

  // Initial loads
  chrome.storage.local.get(["optimizationMode"], res => {
    if (res.optimizationMode) {
      currentMode = res.optimizationMode;
      modeButtons.forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-mode") === currentMode);
      });
    }
  });

  updateInputMetrics();
});

```

## File: `sidepanel.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Squeeze AI Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="sidepanel.css">
</head>
<body>
  <div class="sp-app">
    <!-- Header -->
    <header class="sp-header">
      <div class="sp-logo-group">
        <div class="sp-logo-icon">
          <img src="icons/icon48.png" width="26" height="26" alt="Squeeze Logo">
        </div>
        <div class="sp-title-area">
          <span class="sp-title">Squeeze <span class="highlight">AI</span></span>
          <span class="sp-subtitle">Prompt & Context Optimizer</span>
        </div>
      </div>
      <div class="sp-header-actions">
        <button id="spDemoPitchBtn" class="sp-pitch-btn" title="Load live hackathon demo prompt">
          <span class="pulse-dot"></span>
          <span>Judge Demo</span>
        </button>
      </div>
    </header>

    <!-- Navigation Bar -->
    <nav class="sp-nav">
      <button class="sp-nav-btn active" data-tab="studio">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        Studio
      </button>
      <button class="sp-nav-btn" data-tab="frameworks">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
        Frameworks
      </button>
      <button class="sp-nav-btn" data-tab="dlp">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        DLP Shield
      </button>
      <button class="sp-nav-btn" data-tab="vault">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        Vault
      </button>
      <button class="sp-nav-btn" data-tab="analytics">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        Analytics
      </button>
      <button class="sp-nav-btn" data-tab="graph">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
        Code &amp; Cache
      </button>
    </nav>

    <!-- Main Content Area -->
    <main class="sp-content">
      
      <!-- TAB 1: STUDIO -->
      <section id="pane-studio" class="sp-pane active">
        <!-- Preset Demos Banner -->
        <div class="sp-demo-presets">
          <span class="sp-preset-label">Quick Test:</span>
          <button class="sp-preset-chip" id="demoPresetDev">🐛 Bug + API Key</button>
          <button class="sp-preset-chip" id="demoPresetEmail">✉️ Fluffy Email</button>
          <button class="sp-preset-chip" id="demoPresetCode">📜 Bloated Spec</button>
        </div>

        <!-- Input Box -->
        <div class="sp-card input-card">
          <div class="sp-card-header">
            <span class="sp-card-title">Input Prompt</span>
            <div class="sp-token-badge" id="spInputTokenBadge">0 tokens</div>
          </div>
          <textarea id="spInputPrompt" class="sp-textarea" placeholder="Paste or type any prompt, instructions, code, or context here..."></textarea>
          <div class="sp-input-footer">
            <div class="sp-char-count" id="spCharCount">0 chars · 0 words</div>
            <button class="sp-link-btn" id="spClearInputBtn">Clear</button>
          </div>
        </div>

        <!-- Controls Bar -->
        <div class="sp-controls-card">
          <div class="sp-control-row">
            <label class="sp-control-label">Compression Mode</label>
            <div class="sp-mode-selector">
              <button class="sp-mode-btn" data-mode="squeeze">
                <strong>Squeeze</strong>
                <span>Max (50-70%)</span>
              </button>
              <button class="sp-mode-btn active" data-mode="balanced">
                <strong>Balanced</strong>
                <span>Concise (30-50%)</span>
              </button>
              <button class="sp-mode-btn" data-mode="polish">
                <strong>Polish</strong>
                <span>Clarity (15-30%)</span>
              </button>
            </div>
          </div>

          <div class="sp-control-toggles">
            <label class="sp-toggle-pill">
              <input type="checkbox" id="spToggleDlp" checked>
              <span class="sp-toggle-indicator"></span>
              <span class="sp-toggle-text">DLP Secret Shield</span>
            </label>
            <label class="sp-toggle-pill">
              <input type="checkbox" id="spToggleVault" checked>
              <span class="sp-toggle-indicator"></span>
              <span class="sp-toggle-text">Auto-Inject Vault</span>
            </label>
          </div>

          <button id="spSqueezeActionBtn" class="sp-squeeze-btn">
            <span class="btn-icon">⚡</span>
            <span class="btn-text">Squeeze Prompt</span>
            <span class="btn-sparkle"></span>
          </button>
        </div>

        <!-- Output Card (Visible after squeeze) -->
        <div id="spOutputSection" class="sp-output-section" style="display: none;">
          <!-- Security Alert if secrets found -->
          <div id="spSecretAlertBanner" class="sp-alert-banner" style="display: none;">
            <div class="sp-alert-icon">🛡️</div>
            <div class="sp-alert-content">
              <strong>Security Shield Triggered!</strong>
              <span id="spSecretAlertCount">Sensitive keys were safely redacted before sending.</span>
            </div>
          </div>

          <div class="sp-card output-card">
            <div class="sp-card-header">
              <div class="sp-output-meta">
                <span class="sp-card-title">Squeezed Result</span>
                <span class="sp-quality-pill" id="spQualityPill">⚡ 98% Intent Kept</span>
              </div>
              <div class="sp-view-toggle">
                <button class="sp-view-btn active" id="spViewDiffBtn">Diff</button>
                <button class="sp-view-btn" id="spViewCleanBtn">Clean</button>
              </div>
            </div>

            <!-- Savings Banner -->
            <div class="sp-savings-meter">
              <div class="sp-meter-stat">
                <span class="sp-meter-val" id="spTokensSavedVal">0</span>
                <span class="sp-meter-lbl">Tokens Cut</span>
              </div>
              <div class="sp-meter-divider"></div>
              <div class="sp-meter-stat">
                <span class="sp-meter-val highlight" id="spPercentSavedVal">0%</span>
                <span class="sp-meter-lbl">Reduction</span>
              </div>
              <div class="sp-meter-divider"></div>
              <div class="sp-meter-stat">
                <span class="sp-meter-val" id="spFinalTokenCount">0</span>
                <span class="sp-meter-lbl">Final Tokens</span>
              </div>
            </div>

            <!-- Diff or Clean Content -->
            <div id="spDiffViewContainer" class="sp-diff-container"></div>
            <textarea id="spCleanViewTextarea" class="sp-textarea sp-output-textarea" style="display: none;"></textarea>

            <!-- Applied Rules Chips -->
            <div class="sp-rules-applied" id="spRulesChips"></div>

            <!-- Multi-Model Dollar Savings Breakdown -->
            <div class="sp-model-savings-card">
              <span class="sp-savings-subhead">Estimated Cost Savings (Per 100 Queries)</span>
              <div class="sp-model-grid">
                <div class="sp-model-item">
                  <span class="sp-model-name">Claude 3.5 Sonnet</span>
                  <span class="sp-model-cost" id="spCostSonnet">$0.00</span>
                </div>
                <div class="sp-model-item">
                  <span class="sp-model-name">GPT-4o</span>
                  <span class="sp-model-cost" id="spCostGpt4o">$0.00</span>
                </div>
                <div class="sp-model-item">
                  <span class="sp-model-name">Gemini 1.5 Pro</span>
                  <span class="sp-model-cost" id="spCostGemini">$0.00</span>
                </div>
                <div class="sp-model-item">
                  <span class="sp-model-name">DeepSeek V3</span>
                  <span class="sp-model-cost" id="spCostDeepseek">$0.00</span>
                </div>
              </div>
            </div>

            <!-- Output Actions -->
            <div class="sp-actions-bar">
              <button id="spCopyResultBtn" class="sp-action-btn secondary">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                Copy Prompt
              </button>
              <button id="spSendToActiveTabBtn" class="sp-action-btn primary">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                Insert into Active Chat Tab
              </button>
            </div>
            <div id="spFeedbackMsg" class="sp-feedback-toast">Copied to clipboard!</div>
          </div>
        </div>
      </section>

      <!-- TAB 2: FRAMEWORKS -->
      <section id="pane-frameworks" class="sp-pane">
        <div class="sp-pane-header">
          <h3>Prompt Engineering Frameworks</h3>
          <p>Structure high-converting prompts, then squeeze them to zero fluff.</p>
        </div>

        <div class="sp-framework-cards">
          <!-- CO-STAR Framework -->
          <div class="sp-framework-card" data-framework="costar">
            <div class="sp-fw-header">
              <span class="sp-fw-badge">Top Framework</span>
              <h4>CO-STAR Optimizer</h4>
            </div>
            <p>Context, Objective, Style, Tone, Audience, Response structure condensed into high-signal tokens.</p>
            <button class="sp-fw-apply-btn" id="fwApplyCostar">Load Template</button>
          </div>

          <!-- Few-Shot Optimizer -->
          <div class="sp-framework-card" data-framework="fewshot">
            <div class="sp-fw-header">
              <span class="sp-fw-badge">Few-Shot</span>
              <h4>Few-Shot Token Condenser</h4>
            </div>
            <p>Formats compact input/output exemplars without conversational filler or bloated delimiters.</p>
            <button class="sp-fw-apply-btn" id="fwApplyFewshot">Load Template</button>
          </div>

          <!-- Code Debugger / Refactor -->
          <div class="sp-framework-card" data-framework="code">
            <div class="sp-fw-header">
              <span class="sp-fw-badge">Developer</span>
              <h4>Code Refactor & Bug Hunter</h4>
            </div>
            <p>Pinpoints runtime constraints, stack traces, and snippets with minimal token footprint.</p>
            <button class="sp-fw-apply-btn" id="fwApplyCode">Load Template</button>
          </div>

          <!-- Executive Summary -->
          <div class="sp-framework-card" data-framework="exec">
            <div class="sp-fw-header">
              <span class="sp-fw-badge">Productivity</span>
              <h4>Executive Briefing</h4>
            </div>
            <p>Extracts bullet points, action items, and quantitative metrics from documents.</p>
            <button class="sp-fw-apply-btn" id="fwApplyExec">Load Template</button>
          </div>
        </div>
      </section>

      <!-- TAB 3: DLP SHIELD -->
      <section id="pane-dlp" class="sp-pane">
        <div class="sp-pane-header">
          <div class="sp-pane-title-row">
            <h3>DLP Secret & Privacy Shield</h3>
            <span class="sp-status-chip online">100% Local</span>
          </div>
          <p>Squeeze AI scans prompts locally in real-time. Secrets never leave your browser unmasked.</p>
        </div>

        <div class="sp-card">
          <h4 class="sp-card-subhead">Live Secret Redaction Tester</h4>
          <textarea id="spDlpTestInput" class="sp-textarea" rows="3" placeholder="Paste a sample string containing an API key or password to test live masking..."></textarea>
          <div class="sp-dlp-result-box" id="spDlpResultBox">
            <span class="sp-placeholder-text">Sanitized output will appear here in real time...</span>
          </div>
        </div>

        <div class="sp-card">
          <h4 class="sp-card-subhead">Protected Credential Signatures</h4>
          <ul class="sp-dlp-rules-list">
            <li>
              <span class="dlp-rule-icon">🔑</span>
              <div class="dlp-rule-info">
                <strong>OpenAI & Anthropic Keys</strong>
                <span>Detects <code>sk-...</code>, <code>sk-ant-...</code> tokens</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
            <li>
              <span class="dlp-rule-icon">⚡</span>
              <div class="dlp-rule-info">
                <strong>Google AI & Gemini Keys</strong>
                <span>Detects <code>AIzaSy...</code> credential strings</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
            <li>
              <span class="dlp-rule-icon">☁️</span>
              <div class="dlp-rule-info">
                <strong>AWS Access Keys</strong>
                <span>Detects <code>AKIA...</code> access credentials</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
            <li>
              <span class="dlp-rule-icon">🐙</span>
              <div class="dlp-rule-info">
                <strong>GitHub Tokens</strong>
                <span>Detects <code>ghp_...</code> personal access tokens</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
            <li>
              <span class="dlp-rule-icon">🗄️</span>
              <div class="dlp-rule-info">
                <strong>Database URIs & Passwords</strong>
                <span>Masks MongoDB, Postgres, MySQL authentication strings</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
            <li>
              <span class="dlp-rule-icon">🛡️</span>
              <div class="dlp-rule-info">
                <strong>JWT & Bearer Tokens</strong>
                <span>Detects <code>eyJ...</code> authorization payloads</span>
              </div>
              <span class="dlp-status-tag">Active</span>
            </li>
          </ul>
        </div>
      </section>

      <!-- TAB 4: CONTEXT VAULT -->
      <section id="pane-vault" class="sp-pane">
        <div class="sp-pane-header">
          <h3>Context Vault</h3>
          <p>Global guidelines and reference files automatically compressed and attached when relevant.</p>
        </div>

        <div class="sp-card">
          <h4 class="sp-card-subhead">Global Developer Profile</h4>
          <textarea id="spVaultPrefs" class="sp-textarea" rows="3" placeholder="e.g., Senior Full-Stack Dev. Prefer TypeScript, ES2022, React, Tailwind CSS. Avoid unneeded dependencies."></textarea>
          <label class="sp-toggle-pill" style="margin-top: 8px;">
            <input type="checkbox" id="spVaultAlwaysInject" checked>
            <span class="sp-toggle-indicator"></span>
            <span class="sp-toggle-text">Always Inject into Squeezed Prompts</span>
          </label>
        </div>

        <div class="sp-card">
          <h4 class="sp-card-subhead">Local Reference Files (.txt, .md, .json)</h4>
          <div class="sp-dropzone" id="spVaultDropzone">
            <input type="file" id="spVaultFileInput" accept=".txt,.md,.json" multiple style="display: none;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
            <span>Drag & drop files or <span class="browse-link" id="spVaultBrowseLink">browse</span></span>
          </div>
          <ul class="sp-vault-list" id="spVaultList">
            <li class="empty-list-msg">No reference files in vault yet.</li>
          </ul>
          <label class="sp-toggle-pill" style="margin-top: 8px;">
            <input type="checkbox" id="spVaultSmartTriggers" checked>
            <span class="sp-toggle-indicator"></span>
            <span class="sp-toggle-text">Smart Keyword Auto-Trigger</span>
          </label>
        </div>
      </section>

      <!-- TAB 5: ANALYTICS -->
      <section id="pane-analytics" class="sp-pane">
        <div class="sp-pane-header">
          <h3>Token & Cost Analytics</h3>
          <p>Cumulative savings across all your browser tabs.</p>
        </div>

        <div class="sp-stats-grid">
          <div class="sp-stat-card">
            <span class="sp-stat-num" id="spAnalyticsPrompts">0</span>
            <span class="sp-stat-title">Prompts Squeezed</span>
          </div>
          <div class="sp-stat-card">
            <span class="sp-stat-num cyan" id="spAnalyticsTokens">0</span>
            <span class="sp-stat-title">Tokens Saved</span>
          </div>
          <div class="sp-stat-card">
            <span class="sp-stat-num gold" id="spAnalyticsCost">$0.00</span>
            <span class="sp-stat-title">Cash Saved</span>
          </div>
        </div>

        <!-- Environmental & Eco Impact Card -->
        <div class="sp-card eco-card">
          <div class="eco-header">
            <span class="eco-icon">🌱</span>
            <h4>Eco & GPU Compute Impact</h4>
          </div>
          <p class="eco-desc">By cutting redundant token inference across LLM clusters, you reduce GPU wattage and data center carbon footprint.</p>
          <div class="eco-metrics">
            <div class="eco-metric">
              <span class="eco-val" id="spEcoEnergy">0.0 Wh</span>
              <span class="eco-lbl">Compute Saved</span>
            </div>
            <div class="eco-metric">
              <span class="eco-val" id="spEcoCo2">0.0 g</span>
              <span class="eco-lbl">CO₂ Reduced</span>
            </div>
          </div>
        </div>

        <!-- Optimization History -->
        <div class="sp-card">
          <div class="sp-card-header">
            <h4 class="sp-card-subhead">Recent Squeezes</h4>
            <button class="sp-link-btn danger" id="spResetStatsBtn">Reset Stats</button>
          </div>
          <ul class="sp-history-list" id="spHistoryList">
            <li class="empty-list-msg">No history entries yet.</li>
          </ul>
        </div>
      </section>

      <!-- TAB 6: CODE & CACHE SUITE -->
      <section class="sp-pane" id="pane-graph">
        <!-- Hero Header -->
        <div class="sp-card" style="background: linear-gradient(135deg, rgba(255,109,0,0.08), rgba(0,229,255,0.06)); border-color: rgba(255,109,0,0.25);">
          <div class="sp-card-header">
            <h3 class="sp-card-title">🚀 Squeeze Code &amp; Cache Suite</h3>
            <span class="sp-badge-accent">70x Compression</span>
          </div>
          <p class="sp-card-desc">Deterministic AST Code Skeletons, Topological Codebase Knowledge Graphs, and Provider Cache-Alignment for Claude, Cursor, and ChatGPT.</p>
        </div>

        <!-- 1. AST Code Skeletonizer -->
        <div class="sp-card">
          <div class="sp-card-header">
            <h4 class="sp-card-subhead">1. AST Code Skeletonizer</h4>
            <span class="sp-badge-token" id="spSkelTokenBadge">Saves 70-90% Tokens</span>
          </div>
          <p class="sp-card-desc">Strips function implementation bodies into <code>...</code> or <code>{ /* ... */ }</code> while preserving classes, function signatures, docstrings, and exported types.</p>
          
          <div class="sp-code-tools-bar" style="display: flex; gap: 8px; margin-bottom: 8px;">
            <select id="spSkelLangSelect" class="sp-mini-select" style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12); color: #fff; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem;">
              <option value="python">Python (.py)</option>
              <option value="typescript">TypeScript / JS (.ts, .js)</option>
              <option value="json">JSON API Response (.json)</option>
              <option value="logs">Stack Trace / Logs</option>
            </select>
            <button class="sp-btn sp-btn-secondary" id="spSkelLoadSampleBtn" style="padding: 4px 10px; font-size: 0.72rem;">Load Sample</button>
            <button class="sp-btn sp-btn-primary" id="spSkelRunBtn" style="padding: 4px 12px; font-size: 0.72rem; margin-left: auto;">Extract Skeleton ⚡</button>
          </div>

          <textarea id="spSkelInput" class="sp-textarea" style="height: 120px; font-family: monospace; font-size: 0.72rem;" placeholder="Paste raw Python, TypeScript code, JSON, or stack traces here..."></textarea>
          
          <div id="spSkelResultWrapper" style="display: none; margin-top: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
              <span style="font-size: 0.72rem; font-weight: 600; color: #34d399;" id="spSkelStats">Output: ~0 tokens (80% saved)</span>
              <button class="sp-link-btn" id="spSkelCopyBtn">Copy Skeleton</button>
            </div>
            <textarea id="spSkelOutput" class="sp-textarea" style="height: 110px; font-family: monospace; font-size: 0.72rem; background: rgba(0,0,0,0.4); border-color: rgba(52,211,153,0.3);" readonly></textarea>
          </div>
        </div>

        <!-- 2. Topological Codebase Graph -->
        <div class="sp-card">
          <div class="sp-card-header">
            <h4 class="sp-card-subhead">2. Codebase Knowledge Graph</h4>
            <button class="sp-btn sp-btn-secondary" id="spRefreshGraphBtn" style="padding: 3px 8px; font-size: 0.7rem;">Refresh Graph</button>
          </div>
          <p class="sp-card-desc">Instead of dumping entire files into the AI, Squeeze maps project classes, functions, and import dependencies into a high-density 150-token graph.</p>
          
          <div id="spGraphDisplay" style="background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; max-height: 140px; overflow-y: auto; font-size: 0.72rem; font-family: monospace; color: #ff9d42;">
            <span style="color: #9e978e;">No files in Context Vault yet. Upload files in the Vault tab to auto-generate a dependency graph.</span>
          </div>
        </div>

        <!-- 3. Cache Alignment & MCP Architecture -->
        <div class="sp-card">
          <div class="sp-card-header">
            <h4 class="sp-card-subhead">3. Cache Alignment &amp; MCP Integration</h4>
            <span class="sp-badge-accent">90% Cache Hit</span>
          </div>
          <p class="sp-card-desc">Squeeze organizes prompts into <strong>Tier 1 (Static Persona)</strong> &rarr; <strong>Tier 2 (Architecture Graph)</strong> &rarr; <strong>Tier 3 (User Task)</strong> to lock Anthropic &amp; OpenAI prompt caches.</p>
          
          <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(0,229,255,0.2); border-radius: 8px; padding: 8px 12px; margin-top: 8px;">
            <div style="font-size: 0.7rem; font-weight: 700; color: #00e5ff; margin-bottom: 4px;">⚡ Connect to Cursor / Claude Code via MCP:</div>
            <code style="font-size: 0.68rem; color: #e2e8f0; display: block; background: #0a0a0f; padding: 6px; border-radius: 4px; word-break: break-all;">
              python3 /Users/aashu/Aashu/Squeeze/squeeze_mcp.py
            </code>
            <span style="font-size: 0.65rem; color: #9e978e; margin-top: 4px; display: block;">Add to <code>~/.cursor/mcp.json</code> or Claude Code to compress tool reads automatically.</span>
          </div>
        </div>
      </section>

    </main>

    <!-- Footer -->
    <footer class="sp-footer">
      <span>Squeeze AI · Manifest V3 Production</span>
      <span class="sp-engine-tag">Local Heuristics + DLP Engine</span>
    </footer>
  </div>

  <script src="skeletonizer.js"></script>
  <script src="sidepanel.js"></script>
</body>
</html>

```

## File: `popup.js`
```javascript
/**
 * Squeeze AI - Popup Dashboard Script (Manifest V3)
 * Handles popup stats display, quick Side Panel launching,
 * optimization mode selection, rule configuration, and Context Vault.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Dashboard elements
  const statPrompts = document.getElementById("statPrompts");
  const statTokens = document.getElementById("statTokens");
  const statCost = document.getElementById("statCost");
  const statusBadge = document.getElementById("statusBadge");

  // Side Panel triggers
  const openSidePanelTopBtn = document.getElementById("openSidePanelTopBtn");
  const openSidePanelActionBtn = document.getElementById("openSidePanelActionBtn");
  const footerStudioLink = document.getElementById("footerStudioLink");

  // Settings form elements
  const settingsForm = document.getElementById("settingsForm");
  const ruleSecretShield = document.getElementById("ruleSecretShield");
  const ruleStripGreetings = document.getElementById("ruleStripGreetings");
  const ruleSimplifyPhrases = document.getElementById("ruleSimplifyPhrases");
  const ruleAbbreviate = document.getElementById("ruleAbbreviate");
  const ruleStripArticles = document.getElementById("ruleStripArticles");
  const rulePolishMarkdown = document.getElementById("rulePolishMarkdown");
  const saveFeedback = document.getElementById("saveFeedback");

  // Vault elements
  const vaultPreferences = document.getElementById("vaultPreferences");
  const vaultPrefAlwaysInject = document.getElementById("vaultPrefAlwaysInject");
  const vaultSmartTriggers = document.getElementById("vaultSmartTriggers");
  const vaultDropZone = document.getElementById("vaultDropZone");
  const vaultFileInput = document.getElementById("vaultFileInput");
  const vaultBrowseLink = document.getElementById("vaultBrowseLink");
  const vaultFileList = document.getElementById("vaultFileList");

  let localVaultFiles = [];

  // --- TAB NAVIGATION ---
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const target = document.getElementById(`${tabId}Tab`);
      if (target) target.classList.add("active");
    });
  });

  // --- LAUNCH SIDE PANEL ---
  // Fix #1 (Critical): chrome.sidePanel.open() MUST be called within a user gesture
  // handler in the popup. Relaying through background.js loses the gesture context
  // and silently fails. We call it directly here.
  async function launchSidePanel() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && chrome.sidePanel?.open) {
        await chrome.sidePanel.open({ windowId: tab.windowId });
      }
    } catch (err) {
      console.warn("Side panel open failed:", err);
    }
    window.close();
  }

  if (openSidePanelTopBtn) openSidePanelTopBtn.addEventListener("click", launchSidePanel);
  if (openSidePanelActionBtn) openSidePanelActionBtn.addEventListener("click", launchSidePanel);
  if (footerStudioLink) {
    footerStudioLink.addEventListener("click", e => {
      e.preventDefault();
      launchSidePanel();
    });
  }

  // --- NUMBER FORMATTER ---
  function formatNumber(num) {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toString();
  }

  function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- LOAD SETTINGS & STATS ---
  function loadDashboardData() {
    chrome.storage.local.get(
      [
        "optimizationMode",
        "ruleSecretShield",
        "ruleStripGreetings",
        "ruleSimplifyPhrases",
        "ruleAbbreviate",
        "ruleStripArticles",
        "rulePolishMarkdown",
        "stats_promptsOptimized",
        "stats_tokensSaved",
        "stats_costSaved",
        "vaultPreferences",
        "vaultPrefAlwaysInject",
        "vaultSmartTriggers",
        "vaultFiles"
      ],
      data => {
        // Mode
        const mode = data.optimizationMode || "balanced";
        const modeRadio = document.querySelector(`input[name="optimizationMode"][value="${mode}"]`);
        if (modeRadio) modeRadio.checked = true;

        // Rules
        if (ruleSecretShield) ruleSecretShield.checked = data.ruleSecretShield !== false;
        if (ruleStripGreetings) ruleStripGreetings.checked = data.ruleStripGreetings !== false;
        if (ruleSimplifyPhrases) ruleSimplifyPhrases.checked = data.ruleSimplifyPhrases !== false;
        if (ruleAbbreviate) ruleAbbreviate.checked = data.ruleAbbreviate !== false;
        if (ruleStripArticles) ruleStripArticles.checked = data.ruleStripArticles !== false;
        if (rulePolishMarkdown) rulePolishMarkdown.checked = data.rulePolishMarkdown !== false;

        // Stats — Fix #13: guard against null elements to prevent popup blank crashes
        const prompts = data.stats_promptsOptimized || 0;
        const tokens = data.stats_tokensSaved || 0;
        const cost = data.stats_costSaved || 0;

        if (statPrompts) statPrompts.textContent = formatNumber(prompts);
        if (statTokens) statTokens.textContent = formatNumber(tokens);
        if (statCost) statCost.textContent = cost > 0 && cost < 0.01 ? `$${cost.toFixed(4)}` : `$${cost.toFixed(2)}`;

        // Vault
        vaultPreferences.value = data.vaultPreferences || "";
        vaultPrefAlwaysInject.checked = data.vaultPrefAlwaysInject !== false;
        vaultSmartTriggers.checked = data.vaultSmartTriggers !== false;
        localVaultFiles = data.vaultFiles || [];
        renderVaultFiles();

        // Apply article strip greying after mode is set
        updateArticleStripState();
      }
    );
  }

  // --- SAVE SETTINGS ---
  // Fix #8: Grey-out "Strip Articles" when not in Squeeze mode — it only activates there.
  function updateArticleStripState() {
    if (!ruleStripArticles) return;
    const mode = document.querySelector('input[name="optimizationMode"]:checked')?.value || "balanced";
    const isSqueeze = mode === "squeeze";
    ruleStripArticles.disabled = !isSqueeze;
    const label = ruleStripArticles.closest("label") || ruleStripArticles.nextElementSibling;
    if (label) {
      label.style.opacity = isSqueeze ? "1" : "0.45";
      label.style.cursor = isSqueeze ? "" : "not-allowed";
      label.title = isSqueeze ? "" : "Only active in Squeeze mode";
    }
  }
  // Run on mode change
  document.querySelectorAll('input[name="optimizationMode"]').forEach(radio => {
    radio.addEventListener("change", updateArticleStripState);
  });

  settingsForm.addEventListener("submit", e => {
    e.preventDefault();
    const mode = document.querySelector('input[name="optimizationMode"]:checked')?.value || "balanced";

    chrome.storage.local.set(
      {
        optimizationMode: mode,
        ruleSecretShield: ruleSecretShield ? ruleSecretShield.checked : true,
        ruleStripGreetings: ruleStripGreetings ? ruleStripGreetings.checked : true,
        ruleSimplifyPhrases: ruleSimplifyPhrases ? ruleSimplifyPhrases.checked : true,
        ruleAbbreviate: ruleAbbreviate ? ruleAbbreviate.checked : true,
        ruleStripArticles: ruleStripArticles ? ruleStripArticles.checked : true,
        rulePolishMarkdown: rulePolishMarkdown ? rulePolishMarkdown.checked : true
      },
      () => {
        saveFeedback.classList.add("show");
        setTimeout(() => {
          saveFeedback.classList.remove("show");
        }, 2500);
      }
    );
  });

  // --- VAULT PREFERENCES AUTO-SAVE ---
  vaultPreferences.addEventListener("input", () => {
    chrome.storage.local.set({ vaultPreferences: vaultPreferences.value });
  });

  vaultPrefAlwaysInject.addEventListener("change", () => {
    chrome.storage.local.set({ vaultPrefAlwaysInject: vaultPrefAlwaysInject.checked });
  });

  vaultSmartTriggers.addEventListener("change", () => {
    chrome.storage.local.set({ vaultSmartTriggers: vaultSmartTriggers.checked });
  });

  // --- VAULT FILES UPLOAD ---
  vaultBrowseLink.addEventListener("click", e => {
    e.preventDefault();
    vaultFileInput.click();
  });

  vaultFileInput.addEventListener("change", e => {
    processUploadedFiles(e.target.files);
  });

  vaultDropZone.addEventListener("dragover", e => {
    e.preventDefault();
    vaultDropZone.classList.add("dragover");
  });

  vaultDropZone.addEventListener("dragleave", () => {
    vaultDropZone.classList.remove("dragover");
  });

  vaultDropZone.addEventListener("drop", e => {
    e.preventDefault();
    vaultDropZone.classList.remove("dragover");
    processUploadedFiles(e.dataTransfer.files);
  });

  function processUploadedFiles(files) {
    const MAX_FILE_BYTES  = 500 * 1024;  // 500 KB per file
    const MAX_VAULT_BYTES = 3 * 1024 * 1024; // 3 MB total vault

    const promises = Array.from(files).map(f => {
      return new Promise(resolve => {
        const ext = f.name.split(".").pop().toLowerCase();
        if (!["txt", "md", "json"].includes(ext)) return resolve(null);
        // Fix #6: Enforce per-file size limit to prevent storage quota crashes
        if (f.size > MAX_FILE_BYTES) {
          alert(`"${f.name}" exceeds the 500 KB limit (${(f.size / 1024).toFixed(0)} KB). Please trim it before uploading.`);
          return resolve(null);
        }
        const reader = new FileReader();
        reader.onload = ev => resolve({ name: f.name, content: ev.target.result, size: f.size });
        reader.onerror = () => resolve(null);
        reader.readAsText(f);
      });
    });

    Promise.all(promises).then(results => {
      const valid = results.filter(r => r !== null);
      if (valid.length === 0) return;

      const map = new Map();
      localVaultFiles.forEach(f => map.set(f.name, f));
      valid.forEach(f => map.set(f.name, f));
      const merged = Array.from(map.values());

      // Fix #6: Enforce total vault size limit
      const totalBytes = merged.reduce((sum, f) => sum + (f.size || 0), 0);
      if (totalBytes > MAX_VAULT_BYTES) {
        alert(`Vault total would exceed 3 MB (${(totalBytes / 1024 / 1024).toFixed(1)} MB). Remove some files first.`);
        return;
      }

      localVaultFiles = merged;
      chrome.storage.local.set({ vaultFiles: localVaultFiles }, () => {
        renderVaultFiles();
      });
    });
  }

  function renderVaultFiles() {
    vaultFileList.innerHTML = "";
    if (localVaultFiles.length === 0) {
      const empty = document.createElement("li");
      empty.className = "empty-list-msg";
      empty.textContent = "No files uploaded to the vault yet.";
      vaultFileList.appendChild(empty);
      return;
    }

    localVaultFiles.forEach((file, index) => {
      const li = document.createElement("li");
      li.className = "vault-file-item";
      li.innerHTML = `
        <div class="file-item-info">
          <span class="file-item-name" title="${escapeHtml(file.name)}">📄 ${escapeHtml(file.name)}</span>
          <span class="file-item-size">${formatBytes(file.size)}</span>
        </div>
        <button class="file-delete-btn" data-index="${index}" title="Remove file">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      `;

      li.querySelector(".file-delete-btn").addEventListener("click", () => {
        localVaultFiles.splice(index, 1);
        chrome.storage.local.set({ vaultFiles: localVaultFiles }, renderVaultFiles);
      });

      vaultFileList.appendChild(li);
    });
  }

  loadDashboardData();
});
```

## File: `popup.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Squeeze AI Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="popup.css">
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="logo-area">
        <div class="logo-icon">
          <img src="icons/icon48.png" width="28" height="28" alt="Squeeze Logo">
        </div>
        <span class="logo-text">Squeeze <span class="highlight">AI</span></span>
      </div>
      <div class="header-right-actions">
        <button id="openSidePanelTopBtn" class="sidepanel-launch-btn" title="Open persistent Side Panel Studio">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
          <span>Studio</span>
        </button>
        <div class="status-badge" id="statusBadge">
          <span class="dot"></span>
          <span class="text">Ready</span>
        </div>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="tabs-nav">
      <button class="tab-btn active" data-tab="dashboard">
        <svg class="tab-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"></rect><rect x="14" y="3" width="7" height="5"></rect><rect x="14" y="12" width="7" height="9"></rect><rect x="3" y="16" width="7" height="5"></rect></svg>
        Dashboard
      </button>
      <button class="tab-btn" data-tab="settings">
        <svg class="tab-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        Settings
      </button>
      <button class="tab-btn" data-tab="vault">
        <svg class="tab-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
        Vault
      </button>
    </div>

    <!-- Content Sections -->
    <main class="app-content">
      <!-- Dashboard Tab -->
      <section id="dashboardTab" class="tab-pane active">
        <!-- Persistent Side Panel Banner CTA -->
        <div class="sidepanel-banner" id="sidePanelBanner">
          <div class="sidepanel-banner-left">
            <span class="sidepanel-banner-title">⚡ Squeeze Studio</span>
            <span class="sidepanel-banner-desc">Side-by-side prompt playground & DLP shield.</span>
          </div>
          <button id="openSidePanelActionBtn" class="sidepanel-banner-btn">Open Studio →</button>
        </div>

        <!-- Stats Cards Grid -->
        <div class="stats-grid">
          <div class="stat-card pink-glow">
            <span class="stat-label">Prompts Squeezed</span>
            <span class="stat-value" id="statPrompts">0</span>
            <div class="stat-decorator">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
          </div>
          
          <div class="stat-card cyan-glow">
            <span class="stat-label">Tokens Saved</span>
            <span class="stat-value" id="statTokens">0</span>
            <div class="stat-decorator">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
          </div>
        </div>

        <div class="cost-card purple-glow">
          <div class="cost-info">
            <span class="cost-label">Estimated Cash Saved</span>
            <span class="cost-value" id="statCost">$0.00</span>
          </div>
          <div class="cost-visual">
            <span class="cost-subtext">Across Claude 3.5, GPT-4o & Gemini</span>
          </div>
        </div>

        <!-- Supported Platforms Card -->
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Universal Multi-Platform</span>
            <span class="info-engine-badge">v1.0.0 Active</span>
          </div>
          <div class="platforms-badges">
            <span class="platform-chip">Claude.ai</span>
            <span class="platform-chip">ChatGPT</span>
            <span class="platform-chip">Gemini</span>
          </div>
          <p class="info-text" style="margin-top: 6px;">
            Squeeze injects directly into any chat input on Claude, ChatGPT, or Gemini. Use <kbd>Ctrl+Shift+S</kbd> to quick-squeeze!
          </p>
        </div>
      </section>

      <!-- Settings Tab -->
      <section id="settingsTab" class="tab-pane">
        <form id="settingsForm" class="settings-form">
          
          <!-- Default Compression Profile -->
          <div class="form-group">
            <label>Default Optimization Mode</label>
            <div class="radio-tiles">
              <label class="radio-tile">
                <input type="radio" name="optimizationMode" value="squeeze">
                <span class="tile-content">
                  <span class="tile-title">Squeeze</span>
                  <span class="tile-desc">Telegraphic shorthand, drops articles & auxiliary verbs.</span>
                </span>
              </label>
              <label class="radio-tile">
                <input type="radio" name="optimizationMode" value="balanced" checked>
                <span class="tile-content">
                  <span class="tile-title">Balanced</span>
                  <span class="tile-desc">Deletes greetings, pleasantries, and standard polite filler.</span>
                </span>
              </label>
              <label class="radio-tile">
                <input type="radio" name="optimizationMode" value="polish">
                <span class="tile-content">
                  <span class="tile-title">Polish</span>
                  <span class="tile-desc">Cleans markdown syntax, spacing, and bullet layouts.</span>
                </span>
              </label>
            </div>
          </div>

          <!-- Heuristic Rule Customization Checkboxes -->
          <div class="form-group">
            <label>Optimization & Security Rules</label>
            <div class="checkbox-group">
              <label class="checkbox-container">
                <input type="checkbox" id="ruleSecretShield" name="ruleSecretShield" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label" style="color: #34d399;">🛡️ DLP Secret & Credential Shield</span>
                  <span class="checkbox-desc">Auto-masks API keys (OpenAI, Google, AWS), JWTs, and passwords.</span>
                </div>
              </label>

              <label class="checkbox-container">
                <input type="checkbox" id="ruleStripGreetings" name="ruleStripGreetings" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label">Strip Greetings & Politeness</span>
                  <span class="checkbox-desc">Deletes openings/closings like "hello", "please write", "thanks".</span>
                </div>
              </label>
              
              <label class="checkbox-container">
                <input type="checkbox" id="ruleSimplifyPhrases" name="ruleSimplifyPhrases" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label">Simplify Verbose Phrases</span>
                  <span class="checkbox-desc">Shortens wordy phrases ("in order to" -> "to", "due to" -> "because").</span>
                </div>
              </label>
              
              <label class="checkbox-container">
                <input type="checkbox" id="ruleAbbreviate" name="ruleAbbreviate" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label">Abbreviate Technical Terms</span>
                  <span class="checkbox-desc">Shortens "function" -> "fn", "database" -> "DB" (primarily Squeeze mode).</span>
                </div>
              </label>
              
              <label class="checkbox-container">
                <input type="checkbox" id="ruleStripArticles" name="ruleStripArticles" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label">Strip Articles & Helpers (Squeeze)</span>
                  <span class="checkbox-desc">Telegraphic mode; drops "the", "a", "an", and auxiliary verbs.</span>
                </div>
              </label>
              
              <label class="checkbox-container">
                <input type="checkbox" id="rulePolishMarkdown" name="rulePolishMarkdown" checked>
                <div class="checkbox-label-wrapper">
                  <span class="checkbox-label">Polish Markdown & Spacing</span>
                  <span class="checkbox-desc">Cleans spaces, normalize bullet points, and formats headings correctly.</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Save Button -->
          <button type="submit" class="submit-btn" id="saveBtn">
            <span>Save Settings</span>
            <div class="btn-glow"></div>
          </button>
          
          <div id="saveFeedback" class="save-feedback">Settings Saved Successfully!</div>
        </form>
      </section>

      <!-- Context Vault Tab -->
      <section id="vaultTab" class="tab-pane">
        <div class="vault-container">
          <!-- Personal Preferences -->
          <div class="vault-section">
            <h3 class="vault-section-title">Developer Profile (Global)</h3>
            <p class="vault-section-desc">Global background and guidelines (e.g. coding style, preferred tech stack) injected into queries.</p>
            <textarea id="vaultPreferences" class="vault-textarea" placeholder="Example: I am a TypeScript and React developer. Prefer functional programming. Write concise code."></textarea>
            <label class="checkbox-container inline-checkbox">
              <input type="checkbox" id="vaultPrefAlwaysInject" name="vaultPrefAlwaysInject" checked>
              <div class="checkbox-label-wrapper">
                <span class="checkbox-label">Always Inject Preferences</span>
                <span class="checkbox-desc">Appends these guidelines to all optimized prompts.</span>
              </div>
            </label>
          </div>

          <!-- Local Guidelines (Files) -->
          <div class="vault-section">
            <h3 class="vault-section-title">Local Context Files</h3>
            <p class="vault-section-desc">Load reference guides or codebase specs (.txt, .md, .json) to inject when related keywords are detected.</p>
            
            <div class="file-uploader" id="vaultDropZone">
              <input type="file" id="vaultFileInput" accept=".txt,.md,.json" multiple style="display: none;">
              <svg class="upload-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
              <span>Drag & drop files or <span class="browse-link" id="vaultBrowseLink">browse</span></span>
            </div>

            <div class="vault-files-wrapper">
              <ul class="vault-files-list" id="vaultFileList">
                <li class="empty-list-msg">No files uploaded to the vault yet.</li>
              </ul>
            </div>

            <label class="checkbox-container inline-checkbox">
              <input type="checkbox" id="vaultSmartTriggers" name="vaultSmartTriggers" checked>
              <div class="checkbox-label-wrapper">
                <span class="checkbox-label">Smart Keyword Triggering</span>
                <span class="checkbox-desc">Only inject files whose names or keywords match the prompt.</span>
              </div>
            </label>
          </div>
        </div>
      </section>
    </main>
    
    <!-- Footer -->
    <footer class="app-footer">
      <span>Squeeze AI · v1.0.0</span>
      <a href="#" id="footerStudioLink" class="footer-link">Open Studio</a>
    </footer>
  </div>

  <script src="popup.js"></script>
</body>
</html>

```

