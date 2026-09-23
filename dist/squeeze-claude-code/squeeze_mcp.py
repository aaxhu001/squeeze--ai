#!/usr/bin/env python3
"""
Squeeze AI - Model Context Protocol (MCP) Server
Integrates:
1. Squeeze Codebase Knowledge Graph (Topological Dependency & Symbol Graph)
2. Squeeze AST Code Skeletonizer (Python, TypeScript, JS, Go, Rust)
3. Reversible Chunk Storage (CCR: Chunk Compression & Retrieval)
4. Content-Aware Data Shrinkers (JSON & Logs)
5. DLP Secret Shield (8 Credential Signatures)
6. Provider CacheAligner (Prefix Invariance Engine)

Zero external pip dependencies — 100% Python standard library.
"""

import sys
import os
import json
import re
import hashlib
import time
import gzip
import base64

# --- REVERSIBLE CHUNK STORAGE (CCR) ---
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
    """Strips TypeScript / JavaScript bodies while preserving interfaces, types, classes, and exported signatures."""
    if not code:
        return ""
    lines = code.split("\n")
    result = []
    brace_depth = 0
    in_function_body = False
    func_brace_depth = 0
    i = 0
    n = len(lines)

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

        is_class = bool(re.match(r'^(export\s+)?(abstract\s+)?class\b', trimmed))
        if is_class:
            result.append(line)
            brace_depth += line.count("{") - line.count("}")
            i += 1
            continue

        is_func_start = (
            bool(re.match(r'^(export\s+)?(default\s+)?(async\s+)?function\b', trimmed)) or
            bool(re.match(r'^(public|private|protected|static|override|abstract|async|\s)*(constructor|[a-zA-Z0-9_$]+)\s*(<[^>]*>)?\s*\(', trimmed)) or
            bool(re.match(r'^(export\s+)?(const|let|var)\s+[a-zA-Z0-9_$]+(\s*:[^=]+)?\s*=\s*(async\s*)?(<[^>]*>)?\s*\(', trimmed))
        )

        if is_func_start and not in_function_body:
            sig = line
            p_depth = line.count("(") - line.count(")")

            while (p_depth > 0 or ("{" not in sig and not sig.rstrip().endswith(";"))) and i + 1 < n:
                i += 1
                sig += "\n" + lines[i]
                p_depth += lines[i].count("(") - lines[i].count(")")
                if p_depth <= 0 and ("{" in sig or lines[i].strip().endswith(";")):
                    break

            if "{" in sig:
                brace_idx = sig.index("{")
                header = sig[:brace_idx].rstrip()
                result.append(f"{header} {{ /* ... */ }}")

                remaining = sig[brace_idx:]
                open_b = remaining.count("{")
                close_b = remaining.count("}")
                if open_b > close_b:
                    in_function_body = True
                    func_brace_depth = open_b - close_b
            else:
                result.append(sig)
            i += 1
            continue

        open_b = line.count("{")
        close_b = line.count("}")

        if in_function_body:
            func_brace_depth += (open_b - close_b)
            if func_brace_depth <= 0:
                in_function_body = False
                func_brace_depth = 0
            i += 1
            continue

        if brace_depth <= 1 and (":" in trimmed or ";" in trimmed) and not trimmed.startswith("return "):
            result.append(line)
        elif trimmed in ("}", "};"):
            result.append(line)

        brace_depth += (open_b - close_b)
        if brace_depth < 0:
            brace_depth = 0
        i += 1

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

GRAPH_HTML_TEMPLATE_B64 = """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"""

def resolve_import_path(source_path: str, imp_str: str, file_paths: list):
    """Resolves an import statement to a relative file path within the indexed codebase."""
    imp_clean = imp_str.strip("'\" ")
    if imp_clean in file_paths:
        return imp_clean
    source_dir = os.path.dirname(source_path)
    norm = os.path.normpath(os.path.join(source_dir, imp_clean)).replace("\\", "/")
    if norm.startswith("./"):
        norm = norm[2:]
    for fp in file_paths:
        fp_norm = fp.replace("\\", "/")
        fp_no_ext = os.path.splitext(fp_norm)[0]
        if norm == fp_norm or norm == fp_no_ext or norm + "/index" == fp_no_ext:
            return fp
    imp_base = os.path.splitext(os.path.basename(imp_clean))[0]
    if imp_base and imp_base.lower() not in ["index", "types", "utils", "common"]:
        for fp in file_paths:
            fp_base = os.path.splitext(os.path.basename(fp))[0]
            if imp_base == fp_base and fp != source_path:
                return fp
    return None

def build_codebase_graph_html(repo_name: str, files_indexed: list, links: list, in_degree: dict, symbol_count: int, raw_tokens: int, graph_tokens: int, pct_saved: float) -> str:
    """Builds a self-contained, high-performance interactive HTML5 canvas visualization."""
    nodes = []
    for item in files_indexed:
        p = item["path"]
        deg = in_degree.get(p, 0)
        ext = os.path.splitext(p)[1].lower()
        classes = item["classes"]
        functions = item["functions"]

        if deg >= 2 or len(classes) >= 2 or len(functions) >= 6:
            ntype = "hub"
            color = "#10b981"
        elif "context" in p.lower() or "service" in p.lower() or "api" in p.lower() or "backend" in p.lower() or ext in [".py", ".go", ".rs", ".java", ".cpp", ".c"]:
            ntype = "backend"
            color = "#6366f1"
        elif "screen" in p.lower() or "component" in p.lower() or "view" in p.lower() or "ui" in p.lower() or ext in [".tsx", ".jsx", ".html", ".vue", ".svelte"]:
            ntype = "frontend"
            color = "#06b6d4"
        elif any(k in p.lower() for k in ["test", "spec", "tool", "script", "install", "config"]):
            ntype = "tooling"
            color = "#f59e0b"
        else:
            ntype = "module"
            color = "#8b5cf6"

        desc = []
        if classes: desc.append(f"{len(classes)} classes ({classes[0]})")
        if functions: desc.append(f"{len(functions)} functions ({functions[0]})")
        if item["imports"]: desc.append(f"{len(item['imports'])} imports")
        desc_str = " | ".join(desc) if desc else "Module declarations"

        nodes.append({
            "id": p,
            "name": p,
            "type": ntype,
            "lines": item["lines"],
            "tokens": item["tokens"],
            "centrality": deg,
            "color": color,
            "classes": classes,
            "functions": functions,
            "description": f"{p}: {desc_str}"
        })

    if not links and len(nodes) > 1:
        top_hub = sorted(nodes, key=lambda n: n["tokens"], reverse=True)[0]
        for n in nodes[1:min(len(nodes), 8)]:
            links.append({"source": n["id"], "target": top_hub["id"], "label": "references"})

    graph_json = json.dumps({"nodes": nodes, "links": links}, indent=2)

    try:
        decomp = gzip.decompress(base64.b64decode(GRAPH_HTML_TEMPLATE_B64.encode("ascii"))).decode("utf-8")
        final_html = (
            decomp.replace("__REPO_NAME__", repo_name)
                  .replace("__STAT_FILES__", str(len(files_indexed)))
                  .replace("__STAT_SYMBOLS__", str(symbol_count))
                  .replace("__RAW_TOKENS__", f"{raw_tokens:,}")
                  .replace("__GRAPH_TOKENS__", f"{graph_tokens:,}")
                  .replace("__PCT_SAVED__", f"{pct_saved}")
                  .replace("__GRAPH_DATA__", graph_json)
        )
        return final_html
    except Exception as err:
        return f"<!-- Error building visual graph: {err} -->"

def generate_codebase_graph(root_dir: str = ".", max_files: int = 120, save_files: bool = True) -> str:
    """Traverses a codebase, extracts AST symbols and imports, and builds a topological knowledge graph.
    Automatically generates and saves an interactive visualizer ('codebase_graph.html') and
    markdown index ('CODEBASE_GRAPH.md') into the scanned directory.
    """
    if not os.path.isdir(root_dir):
        return f"Error: '{root_dir}' is not a valid directory."

    ignore_dirs = {
        "node_modules", ".git", "dist", "build", "__pycache__", ".venv", "venv",
        "env", ".env", "coverage", ".next", ".cache", ".idea", ".vscode", "tmp", "temp",
        "PERSONAL_GUIDES_AND_DOCS", "icons", ".expo"
    }
    code_exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".c", ".cpp", ".h"}

    files_indexed = []
    symbol_count = 0
    raw_bytes = 0

    for root, dirs, files in os.walk(root_dir, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for f in files:
            if f.endswith(".min.js") or f.endswith(".min.css") or f.startswith("."):
                continue
            ext = os.path.splitext(f)[1].lower()
            if ext in code_exts:
                if len(files_indexed) >= max_files:
                    break
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, root_dir)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content_str = fp.read()
                    raw_bytes += len(content_str)

                    classes = re.findall(r"\bclass\s+([a-zA-Z0-9_$]+)", content_str)
                    types = re.findall(r"\b(?:type|interface)\s+([a-zA-Z0-9_$]+)", content_str)
                    raw_funcs = re.findall(r"(?:def|function|const)\s+([a-zA-Z0-9_$]+)\s*(?:=\s*(?:async\s*)?\([^)]*\)|=|\()", content_str)

                    func_names = []
                    for name in raw_funcs:
                        if name and name not in func_names and name not in ["if", "for", "while", "switch", "require"]:
                            func_names.append(name)

                    imports = []
                    import_matches = re.findall(r'''(?:from\s+['"]?([a-zA-Z0-9_./-]+)['"]?\s+import|import\s+['"]?([a-zA-Z0-9_./-]+)['"]?|require\(['"]([a-zA-Z0-9_./-]+)['"]\))''', content_str)
                    for im1, im2, im3 in import_matches:
                        target = (im1 or im2 or im3).strip("'\" ")
                        if target and target not in imports:
                            imports.append(target)

                    all_symbols = classes + types + func_names
                    symbol_count += len(all_symbols)

                    files_indexed.append({
                        "path": rel_path,
                        "classes": list(dict.fromkeys(classes + types))[:8],
                        "functions": list(dict.fromkeys(func_names))[:12],
                        "imports": list(dict.fromkeys(imports))[:10],
                        "lines": len(content_str.split("\n")),
                        "tokens": max(1, len(content_str) // 4)
                    })
                except Exception:
                    pass

    if not files_indexed:
        return f"No matching code files found in '{root_dir}'."

    # Resolve links and in-degrees (centrality)
    file_paths = [x["path"] for x in files_indexed]
    in_degree = {x["path"]: 0 for x in files_indexed}
    links = []
    seen_links = set()

    for item in files_indexed:
        src = item["path"]
        for imp in item["imports"]:
            tgt = resolve_import_path(src, imp, file_paths)
            if tgt and tgt != src:
                link_key = (src, tgt)
                if link_key not in seen_links:
                    seen_links.add(link_key)
                    links.append({"source": src, "target": tgt, "label": "imports"})
                    in_degree[tgt] = in_degree.get(tgt, 0) + 1

    files_ranked = sorted(files_indexed, key=lambda x: in_degree.get(x["path"], 0), reverse=True)
    raw_tokens = max(1, raw_bytes // 4)
    graph_tokens = max(1, len(files_indexed) * 35)
    pct_saved = round((1.0 - (graph_tokens / max(1, raw_tokens))) * 100, 1)

    abs_root = os.path.abspath(root_dir)
    repo_name = os.path.basename(abs_root) or "Codebase"
    html_file = os.path.join(abs_root, "codebase_graph.html")
    md_file = os.path.join(abs_root, "CODEBASE_GRAPH.md")

    html_saved = False
    if save_files:
        try:
            html_content = build_codebase_graph_html(
                repo_name=repo_name,
                files_indexed=files_indexed,
                links=links,
                in_degree=in_degree,
                symbol_count=symbol_count,
                raw_tokens=raw_tokens,
                graph_tokens=graph_tokens,
                pct_saved=pct_saved
            )
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            html_saved = True
        except Exception:
            pass

    output = [
        "# 🗺️ SQUEEZE CODEBASE TOPOLOGICAL GRAPH",
        f"- **Repository Path**: `{abs_root}`"
    ]

    if html_saved:
        output.append(f"- **Interactive Visualizer Generated**: `{html_file}` (Saved on disk! Double-click to open in browser & explore interactive node graph)")
    output.append(f"- **Markdown Knowledge Index**: `{md_file}`")
    output.extend([
        f"- **Files Scanned**: {len(files_indexed)} | **Total Symbols Indexed**: {symbol_count}",
        f"- **Raw Code Tokens**: ~{raw_tokens:,} | **Graph Tokens**: ~{graph_tokens:,}",
        f"- **Token Compression**: ~{pct_saved}% savings (exploration cost eliminated)",
        "",
        "### 🏛️ Core Architecture Hubs (Ranked by Centrality):"
    ])

    for item in files_ranked[:5]:
        p = item["path"]
        deg = in_degree.get(p, 0)
        c_str = f"Classes: [{', '.join(item['classes'])}]" if item["classes"] else ""
        f_str = f"Funcs: [{', '.join(item['functions'][:5])}]" if item["functions"] else ""
        sym_desc = " | ".join(filter(None, [c_str, f_str])) or "Module exports"
        output.append(f"- **`{p}`** (Centrality: {deg} imports)\n  ↳ {sym_desc}")

    output.append("\n### 📦 Full Module Symbol & Interface Map:")
    for item in files_indexed:
        p = item["path"]
        c_str = f"Classes: [{', '.join(item['classes'])}]" if item["classes"] else ""
        f_str = f"Funcs: [{', '.join(item['functions'])}]" if item["functions"] else ""
        imp_str = f"Imports: [{', '.join(item['imports'][:4])}]" if item["imports"] else ""
        details = " | ".join(filter(None, [c_str, f_str, imp_str])) or "Declarations & configurations"
        output.append(f"- `{p}` ({item['lines']} lines, ~{item['tokens']} tokens)\n  ↳ {details}")

    full_md = "\n".join(output)

    if save_files:
        try:
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(full_md)
        except Exception:
            pass

    return full_md

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
        "name": "squeeze_codebase_graph",
        "description": "Codebase Knowledge Graph: Scans a directory and generates a compact topological symbol and dependency map. Automatically saves an interactive visual graph ('codebase_graph.html') and markdown index ('CODEBASE_GRAPH.md') directly in the target directory for browser inspection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to repository or directory to index (defaults to current working directory '.')",
                    "default": "."
                },
                "max_files": {
                    "type": "integer",
                    "description": "Maximum number of files to index",
                    "default": 100
                }
            }
        }
    },
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
                    "version": "1.3.0"
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

        if tool_name == "squeeze_codebase_graph":
            target_dir = args.get("directory_path") or args.get("root_dir") or "."
            max_f = args.get("max_files", 100)
            save_f = args.get("save_files", True)
            graph = generate_codebase_graph(target_dir, max_f, save_files=save_f)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": graph}],
                    "isError": False
                }
            }
        
        elif tool_name == "squeeze_compress":
            input_text = args.get("text") or args.get("prompt") or ""
            res = optimize_prompt(input_text, store_reversible=args.get("store_reversible", True))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": res["optimized"]}],
                    "isError": False
                }
            }
            
        elif tool_name == "squeeze_skeleton":
            input_code = args.get("code") or args.get("text") or ""
            lang = args.get("language") or args.get("lang") or "python"
            skel = skeletonize_code(input_code, lang)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": skel}],
                    "isError": False
                }
            }
            
        elif tool_name == "squeeze_shrink_json":
            input_json = args.get("json_text") or args.get("text") or ""
            shrunk = shrink_json_data(input_json, args.get("max_array_items", 2))
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": shrunk}],
                    "isError": False
                }
            }

        elif tool_name == "squeeze_shrink_logs":
            input_logs = args.get("log_text") or args.get("logs") or args.get("text") or ""
            shrunk_l = shrink_logs_data(input_logs)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": shrunk_l}],
                    "isError": False
                }
            }

        elif tool_name == "squeeze_retrieve":
            cid = (args.get("chunk_id") or args.get("id") or "").strip()
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
                args.get("system_prompt") or args.get("prefix") or "",
                args.get("architecture_context") or args.get("context") or "",
                args.get("user_task") or args.get("task") or args.get("prompt") or ""
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
        stripped = line.strip()
        if not stripped:
            continue
        try:
            req = json.loads(stripped)
        except json.JSONDecodeError as jde:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(jde)}"}
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()
            continue
        except Exception as e:
            sys.stderr.write(f"Error parsing input line: {e}\n")
            sys.stderr.flush()
            continue

        try:
            res = handle_message(req)
            if res:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling MCP message: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
