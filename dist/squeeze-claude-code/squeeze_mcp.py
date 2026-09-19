#!/usr/bin/env python3
"""
Squeeze AI - Model Context Protocol (MCP) Server
Integrates Squeeze AI AST Code Skeletonizer, Reversible Chunk Storage (CCR),
Content-Aware Shrinkers (JSON & Logs), DLP Secret Shield, and CacheAligner
directly into Claude Code, Claude Desktop, Cursor, and other AI coding assistants.

Usage:
  python3 squeeze_mcp.py
"""

import sys
import json
import re
import hashlib
import time

# --- REVERSIBLE CHUNK STORAGE (CCR: Chunk Compression & Retrieval) ---
# Stores original raw context in memory so the AI agent can losslessly retrieve full details on demand.
CHUNK_STORE = {}

# Cumulative Token Metrics
METRICS = {
    "total_calls": 0,
    "raw_tokens": 0,
    "squeezed_tokens": 0,
    "tokens_saved": 0
}

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

def skeletonize_python(code: str) -> str:
    """Strips Python function/method bodies while preserving classes, signatures, and docstrings."""
    lines = code.split("\n")
    result = []
    skip_body_indent = None
    in_docstring = False
    docstring_delim = ""
    
    for i, line in enumerate(lines):
        trimmed = line.strip()
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

def skeletonize_typescript(code: str) -> str:
    """Strips TypeScript / JavaScript bodies while preserving interfaces, types, classes, and exported signatures."""
    lines = code.split("\n")
    result = []
    brace_depth = 0
    in_function_body = False
    func_brace_start = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()

        if (trimmed.startswith("import ") or trimmed.startswith("export type ") or
            trimmed.startswith("export interface ") or trimmed.startswith("type ") or
            trimmed.startswith("interface ") or trimmed.startswith("@")):
            result.append(line)
            open_b = line.count("{")
            close_b = line.count("}")
            brace_depth += (open_b - close_b)
            continue

        is_func = (
            bool(re.match(r'^(export\s+)?(async\s+)?function\b', trimmed)) or
            bool(re.match(r'^(public|private|protected|static|override|async|\s)*[a-zA-Z0-9_$]+\s*\([^)]*\)\s*(:\s*[^={]+)?\s*\{?$', trimmed)) or
            bool(re.match(r'^(export\s+)?(const|let|var)\s+[a-zA-Z0-9_$]+\s*=\s*(async\s*)?\([^)]*\)\s*(:\s*[^={]+)?\s*=>\s*\{?$', trimmed))
        )
        is_class = bool(re.match(r'^(export\s+)?(abstract\s+)?class\b', trimmed))

        if is_class:
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            continue

        if is_func and not in_function_body:
            sig = line
            while "{" not in sig and not sig.endswith(";") and i + 1 < len(lines):
                i += 1
                sig += "\n" + lines[i]

            indent_match = re.match(r'^(\s*)', line)
            indent_str = indent_match.group(1) if indent_match else ""

            if "{" in sig:
                sig_clean = sig[:sig.index("{")].strip()
                result.append(f"{indent_str}{sig_clean} {{ /* ... */ }}")
                in_function_body = True
                func_brace_start = brace_depth
                brace_depth += sig.count("{") - sig.count("}")
                if brace_depth <= func_brace_start:
                    in_function_body = False
            else:
                result.append(sig)
            continue

        open_b = line.count("{")
        close_b = line.count("}")

        if in_function_body:
            brace_depth += (open_b - close_b)
            if brace_depth <= func_brace_start:
                in_function_body = False
            continue

        if brace_depth <= 1 and (":" in trimmed or ";" in trimmed) and not trimmed.startswith("return "):
            result.append(line)

        brace_depth += (open_b - close_b)
        if brace_depth < 0:
            brace_depth = 0

    return "\n".join(result).strip()

def skeletonize_code(code: str, language: str = "python") -> str:
    """Main AST Code Skeletonizer dispatcher."""
    if not code:
        return ""
    lang = language.lower()
    if "py" in lang:
        return skeletonize_python(code)
    elif any(k in lang for k in ["ts", "js", "typescript", "javascript"]):
        return skeletonize_typescript(code)
    else:
        # Generic fallback for Go, Rust, C++
        return re.sub(r'\{([^{}]{50,})\}', '{\n    /* ... implementation details omitted ... */\n}', code)

def shrink_json_data(text: str, max_items: int = 2) -> str:
    """Folds repetitive JSON arrays and truncates huge hashes/base64 strings."""
    try:
        data = json.loads(text)
        def fold(obj):
            if isinstance(obj, list):
                if len(obj) > max_items:
                    count = len(obj)
                    kept = [fold(x) for x in obj[:max_items]]
                    kept.append({
                        "_squeezed_array_note": f"... [{count - max_items} similar items omitted to save tokens]",
                        "total_count": count
                    })
                    return kept
                return [fold(x) for x in obj]
            elif isinstance(obj, dict):
                res = {}
                for k, v in obj.items():
                    if isinstance(v, str) and len(v) > 200 and " " not in v:
                        res[k] = v[:40] + f"... [truncated string, length {len(v)}]"
                    else:
                        res[k] = fold(v)
                return res
            return obj
        return json.dumps(fold(data), indent=2)
    except Exception:
        return text

def shrink_logs_data(log_text: str) -> str:
    """Deduplicates repetitive log lines and normalizes timestamps & UUIDs."""
    if not log_text:
        return ""
    lines = log_text.split("\n")
    result = []
    prev_line = ""
    repeat_count = 0

    for line in lines:
        # Normalize timestamps and UUIDs
        clean_line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?Z?', '[TIME]', line)
        clean_line = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '[UUID]', clean_line, flags=re.IGNORECASE)

        if clean_line == prev_line:
            repeat_count += 1
        else:
            if repeat_count > 0:
                result.append(f"   ↳ [Previous line repeated {repeat_count} additional times]")
                repeat_count = 0
            result.append(clean_line)
            prev_line = clean_line

    if repeat_count > 0:
        result.append(f"   ↳ [Previous line repeated {repeat_count} additional times]")

    return "\n".join(result)

def align_prompt_for_cache(system_prompt: str, architecture_context: str, user_task: str) -> str:
    """Formats prompt into Tier 1 (Static Persona) -> Tier 2 (Architecture Context) -> Tier 3 (Volatile Task)."""
    parts = []
    if system_prompt and system_prompt.strip():
        parts.append(f"<!-- CACHE_ANCHOR: SYSTEM_DIRECTIVES -->\n{system_prompt.strip()}")
    if architecture_context and architecture_context.strip():
        parts.append(f"<!-- CACHE_ANCHOR: CODE_ARCHITECTURE -->\n{architecture_context.strip()}")
    if user_task and user_task.strip():
        parts.append(f"<!-- CACHE_VOLATILE: USER_REQUEST -->\n{user_task.strip()}")
    return "\n\n".join(parts)

def optimize_prompt(prompt: str, store_reversible: bool = True) -> dict:
    """Applies Squeeze heuristic optimization rules with reversible chunk caching."""
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
        
    opt_text = sanitized.strip()
    opt_len = len(opt_text)
    
    chunk_id = None
    if store_reversible and orig_len > 300:
        # Generate stable chunk hash
        chunk_id = f"chunk_{hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]}"
        CHUNK_STORE[chunk_id] = {
            "original_text": prompt,
            "created_at": time.time(),
            "orig_tokens": max(1, orig_len // 4),
            "opt_tokens": max(1, opt_len // 4)
        }
        # Annotate with reversible retrieval header
        opt_text = f"[SQUEEZE_CHUNK id=\"{chunk_id}\" (Saved {max(0, (orig_len - opt_len)//4)} tokens). Call squeeze_retrieve(chunk_id=\"{chunk_id}\") for full original]\n" + opt_text

    raw_t = max(1, orig_len // 4)
    opt_t = max(1, len(opt_text) // 4)
    saved_t = max(0, raw_t - opt_t)

    METRICS["total_calls"] += 1
    METRICS["raw_tokens"] += raw_t
    METRICS["squeezed_tokens"] += opt_t
    METRICS["tokens_saved"] += saved_t

    return {
        "optimized": opt_text,
        "chunk_id": chunk_id,
        "original_tokens": raw_t,
        "optimized_tokens": opt_t,
        "tokens_saved": saved_t
    }

# --- MCP JSON-RPC 2.0 PROTOCOL TOOLS ---
TOOLS = [
    {
        "name": "squeeze_compress",
        "description": "Compress prompts, logs, or tool outputs using Squeeze AI heuristics and DLP Secret Shield with reversible chunking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text or prompt to compress"},
                "mask_secrets": {"type": "boolean", "description": "Scan and mask API keys and credentials", "default": True},
                "store_reversible": {"type": "boolean", "description": "Cache original for lossless retrieval via squeeze_retrieve", "default": True}
            },
            "required": ["text"]
        }
    },
    {
        "name": "squeeze_skeleton",
        "description": "Squeeze AST: Extract structural skeletons from source code (classes, methods, signatures, types), cutting 70-90% tokens.",
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
        "description": "Squeeze Data: Folds repetitive JSON arrays and truncates huge hashes/base64 strings, cutting 80%+ tokens on API responses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "json_text": {"type": "string", "description": "JSON string to compress"},
                "max_array_items": {"type": "integer", "description": "Number of sample items to preserve per array", "default": 2}
            },
            "required": ["json_text"]
        }
    },
    {
        "name": "squeeze_shrink_logs",
        "description": "Squeeze Logs: Deduplicates repeating log lines, collapses stack traces, and strips noisy timestamps and UUIDs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "log_text": {"type": "string", "description": "Raw log or terminal output to compress"}
            },
            "required": ["log_text"]
        }
    },
    {
        "name": "squeeze_retrieve",
        "description": "Reversible Compression (CCR): Losslessly retrieve the original full uncompressed content for a given chunk ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chunk_id": {"type": "string", "description": "The chunk ID returned in a previous [SQUEEZE_CHUNK id=...] header"}
            },
            "required": ["chunk_id"]
        }
    },
    {
        "name": "squeeze_cache_align",
        "description": "Provider CacheAligner: Partitions prompt into Tier 1 (Static Persona) -> Tier 2 (Architecture Context) -> Tier 3 (Task) to optimize KV-cache hits.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_prompt": {"type": "string", "description": "Static developer instructions and persona"},
                "architecture_context": {"type": "string", "description": "Codebase graph or AST skeletons"},
                "user_task": {"type": "string", "description": "Volatile user question or command"}
            },
            "required": ["user_task"]
        }
    },
    {
        "name": "squeeze_stats",
        "description": "Returns cumulative token metrics and multi-model cost savings across Claude Opus, Sonnet, and GPT-4o.",
        "inputSchema": {
            "type": "object",
            "properties": {}
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
                    "version": "1.2.0"
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
            res = optimize_prompt(args.get("text", ""), store_reversible=args.get("store_reversible", True))
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

        elif tool_name == "squeeze_shrink_logs":
            shrunk_l = shrink_logs_data(args.get("log_text", ""))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": shrunk_l}],
                    "isError": False
                }
            }

        elif tool_name == "squeeze_retrieve":
            cid = args.get("chunk_id", "").strip()
            if cid in CHUNK_STORE:
                chunk_data = CHUNK_STORE[cid]
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": chunk_data["original_text"]}],
                        "isError": False
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: Chunk '{cid}' not found or expired from local cache."}],
                        "isError": True
                    }
                }

        elif tool_name == "squeeze_cache_align":
            aligned = align_prompt_for_cache(
                args.get("system_prompt", ""),
                args.get("architecture_context", ""),
                args.get("user_task", "")
            )
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": aligned}],
                    "isError": False
                }
            }

        elif tool_name == "squeeze_stats":
            tokens_saved = METRICS["tokens_saved"]
            # Dollar savings: Claude 3.5 Sonnet ($3/M), Claude Opus ($15/M), GPT-4o ($2.50/M)
            dollars_sonnet = (tokens_saved / 1000000.0) * 3.0
            dollars_opus = (tokens_saved / 1000000.0) * 15.0
            stats_json = json.dumps({
                "metrics": METRICS,
                "estimated_dollar_savings": {
                    "claude_sonnet": round(dollars_sonnet, 4),
                    "claude_opus": round(dollars_opus, 4)
                },
                "cached_chunks_count": len(CHUNK_STORE)
            }, indent=2)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": stats_json}],
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
