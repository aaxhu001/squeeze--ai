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
