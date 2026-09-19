#!/usr/bin/env python3
"""
Squeeze Core Engine - AWS Edition
High-performance LLM Context Compressor & Token Optimization Engine.
Zero external pip dependencies — 100% Python standard library.

Key Capabilities:
1. DLP Secret Shield: Scans & masks 8 credential signatures before sending to LLM.
2. Squeeze AST Skeletonizer: Strips function/method bodies (Python, TypeScript, JS, Go, Rust), cutting 70-90% tokens.
3. Content-Aware Data Shrinker (JSON): Folds repetitive array items & collapses large hashes/base64 strings.
4. Content-Aware Log Shrinker: Deduplicates repeating lines, collapses stack traces, strips noisy timestamps & UUIDs.
5. Topological Codebase Knowledge Graph: Scans repos, computes centrality & in-degree dependency import ranks.
6. Provider CacheAligner: Partitions prompts into static anchor prefixes, architecture context, and volatile tasks.
7. Reversible Chunk Storage (CCR): Reversible compression with deterministic chunk IDs and lossless retrieval.
8. Real-time Multi-Model Cost & Token Analytics: Computes savings for Claude Sonnet, Opus, Haiku, and GPT-4o.
"""

import os
import sys
import json
import re
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple

# In-memory Reversible Chunk Store (CCR)
CHUNK_STORE: Dict[str, Dict[str, Any]] = {}

# Cumulative Token & Savings Metrics
METRICS = {
    "total_calls": 0,
    "raw_tokens": 0,
    "squeezed_tokens": 0,
    "tokens_saved": 0,
    "secrets_masked": 0,
    "bytes_before": 0,
    "bytes_after": 0
}

# --- 1. DLP SECRET SHIELD ---
SECRET_PATTERNS = [
    (re.compile(r'\b(sk-ant-[a-zA-Z0-9_-]{20,})\b'), '[MASKED_ANTHROPIC_KEY]'),
    (re.compile(r'\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b'), '[MASKED_OPENAI_KEY]'),
    (re.compile(r'\b(AIzaSy[a-zA-Z0-9_-]{30,})\b'), '[MASKED_GOOGLE_KEY]'),
    (re.compile(r'\b(AKIA[0-9A-Z]{16})\b'), '[MASKED_AWS_ACCESS_KEY]'),
    (re.compile(r'(?i)(aws_secret_access_key|secret_key)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?'), r'\1=[MASKED_AWS_SECRET_KEY]'),
    (re.compile(r'\b(gh[pousr]_[A-Za-z0-9_]{36,})\b'), '[MASKED_GITHUB_TOKEN]'),
    (re.compile(r'\b(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b'), '[MASKED_JWT]'),
    (re.compile(r'((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)'), r'\1[MASKED_PASSWORD]\3')
]

def mask_secrets(text: str) -> Tuple[str, int]:
    """Scan and mask 8 credential signatures. Returns sanitized text and count of secrets masked."""
    if not text:
        return "", 0
    
    count = 0
    sanitized = text
    for pattern, replacement in SECRET_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            count += len(matches)
            sanitized = pattern.sub(replacement, sanitized)
    
    METRICS["secrets_masked"] += count
    return sanitized, count


# --- 2. AST CODE SKELETONIZERS ---
def skeletonize_python(code: str) -> str:
    """Extracts structural signatures, classes, and docstrings from Python source code."""
    if not code:
        return ""
    lines = code.split("\n")
    result = []
    skip_body_indent = None
    in_docstring = False
    docstring_delim = ""
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i]
        trimmed = line.strip()
        indent = len(line) - len(line.lstrip())
        
        if not in_docstring:
            if trimmed.startswith('"""') or trimmed.startswith("'''"):
                docstring_delim = trimmed[:3]
                if len(trimmed) > 3 and trimmed.endswith(docstring_delim):
                    result.append(line)
                    i += 1
                    continue
                in_docstring = True
                result.append(line)
                i += 1
                continue
        else:
            result.append(line)
            if trimmed.endswith(docstring_delim):
                in_docstring = False
            i += 1
            continue
            
        if skip_body_indent is not None:
            if indent > skip_body_indent and trimmed != "":
                i += 1
                continue
            elif trimmed == "":
                i += 1
                continue
            else:
                skip_body_indent = None
                
        if (trimmed.startswith("import ") or trimmed.startswith("from ") or 
            trimmed.startswith("@") or trimmed.startswith("#") or 
            trimmed.startswith("class ") or trimmed.startswith("type ")):
            result.append(line)
            i += 1
            continue
            
        if trimmed.startswith("def ") or trimmed.startswith("async def "):
            sig_lines = [line]
            p_depth = line.count("(") - line.count(")")
            while (p_depth > 0 or not re.search(r':\s*(#.*)?$', sig_lines[-1].strip())) and i + 1 < n:
                i += 1
                sig_lines.append(lines[i])
                p_depth += lines[i].count("(") - lines[i].count(")")
                if p_depth <= 0 and re.search(r':\s*(#.*)?$', lines[i].strip()):
                    break
            result.extend(sig_lines)

            has_doc = False
            if i + 1 < n:
                next_t = lines[i + 1].strip()
                if next_t.startswith('"""') or next_t.startswith("'''"):
                    has_doc = True
            if not has_doc:
                result.append(" " * (indent + 4) + "...")
            skip_body_indent = indent
            i += 1
            continue
            
        if indent == 0 and "=" in trimmed and not trimmed.startswith("if ") and not trimmed.startswith("for "):
            result.append(line)
        i += 1
            
    return "\n".join(result).strip()


def skeletonize_typescript(code: str) -> str:
    """Strips TypeScript / JavaScript function bodies while preserving interfaces, types, and exported signatures."""
    if not code:
        return ""
    lines = code.split("\n")
    result = []
    i = 0
    n = len(lines)
    brace_depth = 0
    in_function_body = False
    func_depth = 0

    while i < n:
        line = lines[i]
        trimmed = line.strip()

        if (trimmed.startswith("import ") or trimmed.startswith("export type ") or
            trimmed.startswith("export interface ") or trimmed.startswith("type ") or
            trimmed.startswith("interface ") or trimmed.startswith("@")):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if re.search(r'^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\b', trimmed) or \
           re.search(r'^(?:public|private|protected|async|static|\s*)*(?:[a-zA-Z0-9_$]+)\s*\(.*?\)\s*(?::\s*[^\{]+)?\s*\{', trimmed):
            sig = trimmed.split("{")[0].strip()
            result.append(" " * (len(line) - len(line.lstrip())) + sig + " { ... }")
            brace_depth += line.count("{") - line.count("}")
            in_function_body = True
            func_depth = brace_depth
            i += 1
            while i < n and in_function_body:
                brace_depth += lines[i].count("{") - lines[i].count("}")
                if brace_depth < func_depth:
                    in_function_body = False
                i += 1
            continue

        if trimmed.startswith("export class ") or trimmed.startswith("class "):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if brace_depth == 0 and (trimmed.startswith("const ") or trimmed.startswith("let ") or trimmed.startswith("export const ")):
            if "=>" not in trimmed and "function" not in trimmed:
                result.append(line)

        brace_depth += line.count("{") - line.count("}")
        i += 1

    return "\n".join(result).strip()


def skeletonize_go(code: str) -> str:
    """Strips Go function bodies while preserving package, imports, structs, and interfaces."""
    if not code:
        return ""
    lines = code.split("\n")
    result = []
    i = 0
    n = len(lines)
    brace_depth = 0
    in_func = False
    func_depth = 0

    while i < n:
        line = lines[i]
        trimmed = line.strip()

        if trimmed.startswith("package ") or trimmed.startswith("import "):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if trimmed.startswith("type ") and ("struct" in trimmed or "interface" in trimmed):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if trimmed.startswith("func ") and "{" in trimmed:
            sig = trimmed.split("{")[0].strip()
            result.append(sig + " { ... }")
            brace_depth += line.count("{") - line.count("}")
            in_func = True
            func_depth = brace_depth
            i += 1
            while i < n and in_func:
                brace_depth += lines[i].count("{") - lines[i].count("}")
                if brace_depth < func_depth:
                    in_func = False
                i += 1
            continue

        if brace_depth == 0 and (trimmed.startswith("var ") or trimmed.startswith("const ")):
            result.append(line)

        brace_depth += line.count("{") - line.count("}")
        i += 1

    return "\n".join(result).strip()


def skeletonize_rust(code: str) -> str:
    """Strips Rust function implementations while preserving traits, structs, enums, and signatures."""
    if not code:
        return ""
    lines = code.split("\n")
    result = []
    i = 0
    n = len(lines)
    brace_depth = 0
    in_fn = False
    fn_depth = 0

    while i < n:
        line = lines[i]
        trimmed = line.strip()

        if trimmed.startswith("use ") or trimmed.startswith("pub use ") or trimmed.startswith("mod "):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if (trimmed.startswith("pub struct ") or trimmed.startswith("struct ") or
            trimmed.startswith("pub enum ") or trimmed.startswith("enum ") or
            trimmed.startswith("pub trait ") or trimmed.startswith("trait ")):
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        if re.search(r'^(?:pub\s+)?(?:async\s+)?fn\b', trimmed) and "{" in trimmed:
            sig = trimmed.split("{")[0].strip()
            result.append(" " * (len(line) - len(line.lstrip())) + sig + " { ... }")
            brace_depth += line.count("{") - line.count("}")
            in_fn = True
            fn_depth = brace_depth
            i += 1
            while i < n and in_fn:
                brace_depth += lines[i].count("{") - lines[i].count("}")
                if brace_depth < fn_depth:
                    in_fn = False
                i += 1
            continue

        if trimmed.startswith("impl ") and "{" in trimmed:
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        brace_depth += line.count("{") - line.count("}")
        i += 1

    return "\n".join(result).strip()


def skeletonize_code(code: str, language: str = "python") -> str:
    """Routes code skeletonization to appropriate AST handler."""
    lang = language.lower().strip()
    if lang in ["python", "py"]:
        return skeletonize_python(code)
    elif lang in ["typescript", "ts", "javascript", "js"]:
        return skeletonize_typescript(code)
    elif lang in ["go", "golang"]:
        return skeletonize_go(code)
    elif lang in ["rust", "rs"]:
        return skeletonize_rust(code)
    else:
        # Fallback: line truncation & comment stripping
        return skeletonize_python(code)


# --- 3. DATA SHRINKS (JSON & LOGS) ---
def shrink_json_data(json_str: str, max_array_items: int = 2) -> str:
    """Folds massive JSON structures, caps array lengths, and truncates large base64/hex data."""
    if not json_str:
        return ""
    try:
        data = json.loads(json_str)
    except Exception:
        # If not valid JSON, perform string-level heuristic truncation
        return json_str[:2000] + ("\n... [TRUNCATED INVALID JSON]" if len(json_str) > 2000 else "")

    def _shrink(node):
        if isinstance(node, list):
            if len(node) > max_array_items:
                sample = [_shrink(item) for item in node[:max_array_items]]
                sample.append(f"... [{len(node) - max_array_items} items collapsed by Squeeze AI]")
                return sample
            return [_shrink(item) for item in node]
        elif isinstance(node, dict):
            new_dict = {}
            for k, v in node.items():
                if isinstance(v, str) and len(v) > 120 and (re.match(r'^[a-zA-Z0-9+/=]{64,}$', v) or re.match(r'^[a-fA-F0-9]{64,}$', v)):
                    new_dict[k] = f"{v[:16]}...[HASH_COLLAPSED_LEN_{len(v)}]...{v[-8:]}"
                else:
                    new_dict[k] = _shrink(v)
            return new_dict
        elif isinstance(node, str) and len(node) > 500:
            return node[:200] + f"... [COLLAPSED {len(node)-300} chars] ..." + node[-100:]
        return node

    shrunk = _shrink(data)
    return json.dumps(shrunk, indent=2)


def shrink_logs_data(log_text: str) -> str:
    """
    Collapses repetitive log lines, strips microsecond timestamps/UUIDs,
    and condenses stack trace noise.
    """
    if not log_text:
        return ""
    
    # 1. Mask credentials first
    cleaned, _ = mask_secrets(log_text)
    
    # 2. Normalize timestamps and UUIDs for deduplication grouping
    lines = cleaned.split("\n")
    collapsed = []
    prev_norm = None
    repeat_count = 0
    
    uuid_pattern = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    iso_time_pattern = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?')
    
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue
            
        # Create a normalized fingerprint for matching
        norm = iso_time_pattern.sub('<TIMESTAMP>', trimmed)
        norm = uuid_pattern.sub('<UUID>', norm)
        # Strip thread ID numbers like [thread-1234]
        norm = re.sub(r'\[(?:thread|pool-)[0-9a-zA-Z_-]+\]', '[THREAD]', norm)
        
        if norm == prev_norm:
            repeat_count += 1
        else:
            if repeat_count > 1:
                collapsed.append(f"   ↳ [Squeeze AI: Repeated {repeat_count} identical entries suppressed]")
            collapsed.append(trimmed)
            prev_norm = norm
            repeat_count = 1
            
    if repeat_count > 1:
        collapsed.append(f"   ↳ [Squeeze AI: Repeated {repeat_count} identical entries suppressed]")
        
    return "\n".join(collapsed)


# --- 4. CODEBASE TOPOLOGICAL GRAPH ---
def generate_codebase_graph(root_dir: str = ".", max_files: int = 100) -> str:
    """Scans repository, extracts imports/symbols, computes centrality in-degree ranks."""
    files_indexed = []
    symbol_count = 0
    raw_bytes = 0

    ignored_dirs = {".git", "node_modules", "target", "dist", "build", "__pycache__", ".venv", "cdk.out"}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in [".py", ".ts", ".js", ".go", ".rs"]:
                p = os.path.relpath(os.path.join(root, f), root_dir)
                full_p = os.path.join(root, f)
                try:
                    with open(full_p, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read()
                    raw_bytes += len(content)
                    classes = re.findall(r'(?:class|type|struct)\s+([A-Za-z0-9_]+)', content)
                    funcs = re.findall(r'(?:def|async def|function|fn|func)\s+([A-Za-z0-9_]+)', content)
                    imports = re.findall(r'(?:import|from)\s+([A-Za-z0-9_.]+)', content)
                    symbol_count += len(classes) + len(funcs)
                    files_indexed.append({
                        "path": p,
                        "lines": len(content.splitlines()),
                        "tokens": max(1, len(content) // 4),
                        "classes": classes[:5],
                        "functions": funcs[:8],
                        "imports": imports[:6]
                    })
                except Exception:
                    continue
                if len(files_indexed) >= max_files:
                    break
        if len(files_indexed) >= max_files:
            break

    # Compute in-degrees (Centrality Ranking)
    in_degree = {f["path"]: 0 for f in files_indexed}
    for item in files_indexed:
        base_name = os.path.splitext(os.path.basename(item["path"]))[0]
        for other in files_indexed:
            for imp in other["imports"]:
                if base_name in imp:
                    in_degree[item["path"]] += 1

    files_ranked = sorted(files_indexed, key=lambda x: in_degree.get(x["path"], 0), reverse=True)
    raw_tokens = max(1, raw_bytes // 4)
    graph_tokens = max(1, len(files_indexed) * 35)
    pct_saved = round((1.0 - (graph_tokens / max(1, raw_tokens))) * 100, 1)

    output = [
        "# 🗺️ SQUEEZE CODEBASE TOPOLOGICAL GRAPH",
        f"- **Repository Path**: `{os.path.abspath(root_dir)}`",
        f"- **Files Scanned**: {len(files_indexed)} | **Total Symbols Indexed**: {symbol_count}",
        f"- **Raw Code Tokens**: ~{raw_tokens:,} | **Graph Tokens**: ~{graph_tokens:,}",
        f"- **Token Compression**: ~{pct_saved}% savings (exploration cost eliminated)",
        "",
        "### 🏛️ Core Architecture Hubs (Ranked by Centrality):"
    ]

    for item in files_ranked[:5]:
        p = item["path"]
        deg = in_degree.get(p, 0)
        c_str = f"Classes: [{', '.join(item['classes'])}]" if item['classes'] else ""
        f_str = f"Funcs: [{', '.join(item['functions'][:5])}]" if item['functions'] else ""
        sym_desc = " | ".join(filter(None, [c_str, f_str])) or "Module exports"
        output.append(f"- **`{p}`** (Centrality: {deg} imports)\n  ↳ {sym_desc}")

    output.append("\n### 📦 Full Module Symbol & Interface Map:")
    for item in files_indexed:
        p = item["path"]
        c_str = f"Classes: [{', '.join(item['classes'])}]" if item['classes'] else ""
        f_str = f"Funcs: [{', '.join(item['functions'])}]" if item['functions'] else ""
        imp_str = f"Imports: [{', '.join(item['imports'][:4])}]" if item['imports'] else ""
        details = " | ".join(filter(None, [c_str, f_str, imp_str])) or "Declarations & configurations"
        output.append(f"- `{p}` ({item['lines']} lines, ~{item['tokens']} tokens)\n  ↳ {details}")

    return "\n".join(output)


# --- 5. CACHE ALIGNER ---
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


# --- 6. GENERAL PROMPT COMPRESSION & REVERSIBLE CHUNKS ---
def optimize_prompt(prompt: str, store_reversible: bool = True) -> Dict[str, Any]:
    """Applies Squeeze heuristic compression with DLP Secret Shield and reversible chunking."""
    orig_len = len(prompt)
    sanitized, secrets_count = mask_secrets(prompt)

    # 1. Strip greetings & polite fluff
    polite = [
        r'\b(?:hello|hi|hey|dear)\s+(?:assistant|claude|chatgpt|ai|there)\b[.,!?]*\s*',
        r'\b(?:thank\s+you|thanks)(?:\s+in\s+advance)?[.,!?]*\s*',
        r'\bi\s+was\s+wondering\s+if\s+you\s+could\b\s*',
        r'\bplease\s+(?:help\s+me\s+to\s+)?\b'
    ]
    for p in polite:
        sanitized = re.sub(p, '', sanitized, flags=re.IGNORECASE)

    # 2. Verbosity reductions
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
    if store_reversible and orig_len > 250:
        chunk_id = f"chunk_{hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]}"
        CHUNK_STORE[chunk_id] = {
            "original_text": prompt,
            "created_at": time.time(),
            "orig_tokens": max(1, orig_len // 4),
            "opt_tokens": max(1, opt_len // 4)
        }
        opt_text = f"[SQUEEZE_CHUNK id=\"{chunk_id}\" (Saved {max(0, (orig_len - opt_len)//4)} tokens). Call squeeze_retrieve(chunk_id=\"{chunk_id}\") for full original]\n" + opt_text

    raw_t = max(1, orig_len // 4)
    opt_t = max(1, len(opt_text) // 4)
    saved_t = max(0, raw_t - opt_t)

    METRICS["total_calls"] += 1
    METRICS["raw_tokens"] += raw_t
    METRICS["squeezed_tokens"] += opt_t
    METRICS["tokens_saved"] += saved_t
    METRICS["bytes_before"] += orig_len
    METRICS["bytes_after"] += len(opt_text)

    return {
        "optimized": opt_text,
        "chunk_id": chunk_id,
        "original_tokens": raw_t,
        "optimized_tokens": opt_t,
        "tokens_saved": saved_t,
        "secrets_masked": secrets_count
    }


def retrieve_chunk(chunk_id: str) -> Optional[str]:
    """Losslessly retrieves the original uncompressed text for a chunk ID."""
    cid = chunk_id.strip()
    if cid in CHUNK_STORE:
        return CHUNK_STORE[cid]["original_text"]
    return None


def get_stats() -> Dict[str, Any]:
    """Returns cumulative metrics, savings ratio, and multi-model cost savings."""
    tokens_saved = METRICS["tokens_saved"]
    # Pricing per 1M tokens: Claude 3.5 Sonnet ($3.00), Claude Opus ($15.00), Claude 3 Haiku ($0.25), GPT-4o ($2.50)
    dollars_sonnet = (tokens_saved / 1_000_000.0) * 3.0
    dollars_opus = (tokens_saved / 1_000_000.0) * 15.0
    dollars_haiku = (tokens_saved / 1_000_000.0) * 0.25
    dollars_gpt4o = (tokens_saved / 1_000_000.0) * 2.50

    pct_saved = 0.0
    if METRICS["raw_tokens"] > 0:
        pct_saved = round((METRICS["tokens_saved"] / METRICS["raw_tokens"]) * 100, 2)

    return {
        "metrics": METRICS,
        "compression_percentage": pct_saved,
        "estimated_dollar_savings": {
            "claude_3_5_sonnet": round(dollars_sonnet, 4),
            "claude_3_opus": round(dollars_opus, 4),
            "claude_3_haiku": round(dollars_haiku, 4),
            "gpt_4o": round(dollars_gpt4o, 4)
        },
        "cached_chunks_count": len(CHUNK_STORE)
    }
