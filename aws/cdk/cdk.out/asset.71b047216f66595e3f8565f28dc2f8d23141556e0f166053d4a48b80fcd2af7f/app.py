#!/usr/bin/env python3
"""
Squeeze MCP & REST Server - AWS Edition
Dual-Mode Server:
1. Native AWS Lambda Handler (Lambda Function URL & API Gateway v2)
2. Standalone HTTP / SSE / JSON-RPC Server (Docker / Fargate / Local)

Exposes:
- MCP JSON-RPC 2.0 (`POST /mcp` or `POST /`)
- MCP SSE Transport (`GET /sse`)
- REST Endpoints for Bedrock Agent Action Groups & direct HTTP clients
- Zero external pip dependencies — 100% Python standard library.
"""

import os
import sys
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Ensure squeeze_core is importable from current directory or path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import squeeze_core as engine

MCP_TOOLS = [
    {
        "name": "squeeze_shrink_logs",
        "description": "Deduplicate repetitive log lines, collapse stack traces, and strip timestamps/UUIDs from CloudWatch logs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "log_text": {"type": "string", "description": "Raw CloudWatch or application log text"}
            },
            "required": ["log_text"]
        }
    },
    {
        "name": "squeeze_shrink_json",
        "description": "Fold repetitive JSON arrays and collapse large hashes/base64 strings, saving 75%+ tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "json_text": {"type": "string", "description": "JSON string to shrink"},
                "max_array_items": {"type": "integer", "description": "Sample items per array (default 2)", "default": 2}
            },
            "required": ["json_text"]
        }
    },
    {
        "name": "squeeze_skeleton",
        "description": "Extract AST code skeletons (classes, methods, signatures) for Python, TypeScript, Go, or Rust.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code text"},
                "language": {"type": "string", "description": "python, typescript, javascript, go, rust", "default": "python"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "squeeze_compress",
        "description": "Compress prompt with DLP Secret Shield (masks 8 credential types) and reversible chunking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text or prompt to compress"},
                "mask_secrets": {"type": "boolean", "description": "Scan and mask credentials", "default": True}
            },
            "required": ["text"]
        }
    },
    {
        "name": "squeeze_codebase_graph",
        "description": "Scan repository and generate a topological dependency map with module centrality ranking.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Directory to scan (default .)", "default": "."},
                "max_files": {"type": "integer", "description": "Max files to index", "default": 100}
            }
        }
    },
    {
        "name": "squeeze_retrieve",
        "description": "Losslessly retrieve original full content for a previously compressed SQUEEZE_CHUNK ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chunk_id": {"type": "string", "description": "Deterministic chunk ID"}
            },
            "required": ["chunk_id"]
        }
    },
    {
        "name": "squeeze_cache_align",
        "description": "Partitions prompt into Static Persona -> Architecture Context -> Volatile Task for KV-cache reuse.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_prompt": {"type": "string", "description": "Static developer instructions"},
                "architecture_context": {"type": "string", "description": "Codebase graph or AST skeletons"},
                "user_task": {"type": "string", "description": "Volatile user question"}
            },
            "required": ["user_task"]
        }
    },
    {
        "name": "squeeze_stats",
        "description": "Returns cumulative tokens saved, compression ratio, and estimated multi-model dollar savings.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_mcp_jsonrpc(msg: Dict[str, Any]) -> Dict[str, Any]:
    """Processes MCP JSON-RPC 2.0 messages."""
    msg_id = msg.get("id")
    method = msg.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "squeeze-aws-mcp", "version": "1.3.0"}
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": MCP_TOOLS}
        }
    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "squeeze_shrink_logs":
                logs = args.get("log_text") or args.get("logs") or args.get("text") or ""
                orig_t = max(1, len(logs) // 4)
                shrunk = engine.shrink_logs_data(logs)
                new_t = max(1, len(shrunk) // 4)
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": shrunk}],
                        "meta": {"tokens_before": orig_t, "tokens_after": new_t, "tokens_saved": max(0, orig_t - new_t)}
                    }
                }
            elif tool_name == "squeeze_shrink_json":
                raw_json = args.get("json_text") or args.get("text") or "{}"
                orig_t = max(1, len(raw_json) // 4)
                shrunk = engine.shrink_json_data(raw_json, args.get("max_array_items", 2))
                new_t = max(1, len(shrunk) // 4)
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": shrunk}],
                        "meta": {"tokens_before": orig_t, "tokens_after": new_t, "tokens_saved": max(0, orig_t - new_t)}
                    }
                }
            elif tool_name == "squeeze_skeleton":
                code = args.get("code") or args.get("text") or ""
                lang = args.get("language") or "python"
                orig_t = max(1, len(code) // 4)
                skel = engine.skeletonize_code(code, lang)
                new_t = max(1, len(skel) // 4)
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": skel}],
                        "meta": {"tokens_before": orig_t, "tokens_after": new_t, "tokens_saved": max(0, orig_t - new_t)}
                    }
                }
            elif tool_name == "squeeze_compress":
                text = args.get("text") or ""
                res = engine.optimize_prompt(text, store_reversible=args.get("store_reversible", True))
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": res["optimized"]}],
                        "meta": res
                    }
                }
            elif tool_name == "squeeze_codebase_graph":
                path = args.get("directory_path", ".")
                max_f = args.get("max_files", 100)
                graph = engine.generate_codebase_graph(path, max_f)
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": graph}]}
                }
            elif tool_name == "squeeze_retrieve":
                cid = args.get("chunk_id", "")
                text = engine.retrieve_chunk(cid)
                if text is not None:
                    return {
                        "jsonrpc": "2.0", "id": msg_id,
                        "result": {"content": [{"type": "text", "text": text}], "isError": False}
                    }
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": f"Chunk {cid} not found"}], "isError": True}
                }
            elif tool_name == "squeeze_cache_align":
                aligned = engine.align_prompt_for_cache(
                    args.get("system_prompt", ""),
                    args.get("architecture_context", ""),
                    args.get("user_task", "")
                )
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": aligned}]}
                }
            elif tool_name == "squeeze_stats":
                stats = engine.get_stats()
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(stats, indent=2)}]}
                }
            else:
                return {
                    "jsonrpc": "2.0", "id": msg_id,
                    "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32000, "message": str(e)}
            }

    return {
        "jsonrpc": "2.0", "id": msg_id,
        "error": {"code": -32600, "message": f"Unsupported method '{method}'"}
    }


def handle_rest_request(path: str, method: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Handles REST and Bedrock Action Group calls directly."""
    clean_path = path.rstrip("/")

    if clean_path in ["/health", ""]:
        return {"status": "ok", "service": "squeeze-aws-mcp", "timestamp": time.time()}

    elif clean_path == "/shrink-logs":
        log_text = body.get("log_text") or body.get("logs") or ""
        orig_t = max(1, len(log_text) // 4)
        shrunk = engine.shrink_logs_data(log_text)
        new_t = max(1, len(shrunk) // 4)
        return {
            "compressed_logs": shrunk,
            "original_tokens": orig_t,
            "compressed_tokens": new_t,
            "tokens_saved": max(0, orig_t - new_t),
            "ratio_saved": round((1.0 - (new_t / max(1, orig_t))) * 100, 1)
        }

    elif clean_path == "/shrink-json":
        json_text = body.get("json_text") or "{}"
        orig_t = max(1, len(json_text) // 4)
        shrunk = engine.shrink_json_data(json_text, body.get("max_array_items", 2))
        new_t = max(1, len(shrunk) // 4)
        return {
            "shrunk_json": shrunk,
            "original_tokens": orig_t,
            "shrunk_tokens": new_t,
            "tokens_saved": max(0, orig_t - new_t),
            "ratio_saved": round((1.0 - (new_t / max(1, orig_t))) * 100, 1)
        }

    elif clean_path == "/skeleton":
        code = body.get("code") or ""
        lang = body.get("language") or "python"
        orig_t = max(1, len(code) // 4)
        skel = engine.skeletonize_code(code, lang)
        new_t = max(1, len(skel) // 4)
        return {
            "skeleton": skel,
            "original_tokens": orig_t,
            "skeleton_tokens": new_t,
            "tokens_saved": max(0, orig_t - new_t),
            "ratio_saved": round((1.0 - (new_t / max(1, orig_t))) * 100, 1)
        }

    elif clean_path == "/compress":
        text = body.get("text") or ""
        return engine.optimize_prompt(text, store_reversible=body.get("store_reversible", True))

    elif clean_path == "/codebase-graph":
        target = body.get("directory_path") or "."
        max_f = body.get("max_files") or 100
        graph = engine.generate_codebase_graph(target, max_f)
        return {"graph_markdown": graph}

    elif clean_path == "/retrieve":
        cid = body.get("chunk_id") or ""
        text = engine.retrieve_chunk(cid)
        return {"original_text": text or "", "found": text is not None}

    elif clean_path == "/stats":
        return engine.get_stats()

    return {"error": f"Endpoint '{clean_path}' not found", "status": 404}


# --- AWS LAMBDA HANDLER (Function URL & API Gateway v2) ---
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Direct entrypoint for AWS Lambda executions."""
    # Check if this is a Bedrock Agent Action Group invocation
    if "actionGroup" in event and "apiPath" in event:
        api_path = event.get("apiPath", "")
        # Parse request body from Bedrock Action Group format
        req_body = {}
        if "requestBody" in event and "content" in event["requestBody"]:
            app_json = event["requestBody"]["content"].get("application/json", {})
            props = app_json.get("properties", [])
            for p in props:
                req_body[p.get("name")] = p.get("value")
        # Also check parameters list
        for param in event.get("parameters", []):
            req_body[param.get("name")] = param.get("value")

        res_data = handle_rest_request(api_path, "POST", req_body)

        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup"),
                "apiPath": api_path,
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": json.dumps(res_data)
                    }
                }
            }
        }

    # Standard Lambda Function URL / API Gateway HTTP event
    raw_path = event.get("rawPath") or event.get("path") or "/"
    http_method = (event.get("requestContext", {}).get("http", {}).get("method") or 
                   event.get("httpMethod") or "GET").upper()
    
    body = {}
    if "body" in event and event["body"]:
        try:
            body = json.loads(event["body"])
        except Exception:
            body = {"text": event["body"]}

    # Check for MCP JSON-RPC
    if (raw_path in ["/mcp", "/"] and http_method == "POST") and "jsonrpc" in body:
        mcp_res = handle_mcp_jsonrpc(body)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps(mcp_res)
        }

    # REST endpoint dispatch
    res = handle_rest_request(raw_path, http_method, body)
    status_code = res.get("status", 200) if isinstance(res, dict) and "error" in res else 200

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        },
        "body": json.dumps(res)
    }


# --- STANDALONE HTTP SERVER (Docker / Fargate / Local) ---
class SqueezeHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/sse":
            # Basic MCP SSE endpoint initialization
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            endpoint_msg = f"event: endpoint\ndata: /mcp?sessionId=sqz-{int(time.time())}\n\n"
            self.wfile.write(endpoint_msg.encode("utf-8"))
            self.wfile.flush()
            return

        res = handle_rest_request(url.path, "GET", {})
        self._send_json(res, 200)

    def do_POST(self):
        url = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            body = json.loads(post_data)
        except Exception:
            body = {"text": post_data}

        # Check for MCP JSON-RPC
        if (url.path in ["/mcp", "/"]) and "jsonrpc" in body:
            mcp_res = handle_mcp_jsonrpc(body)
            self._send_json(mcp_res, 200)
            return

        res = handle_rest_request(url.path, "POST", body)
        self._send_json(res, 200)

    def log_message(self, format, *args):
        # Concise logging for Docker/cloud logs
        sys.stderr.write(f"[SQUEEZE-MCP] {args[0]} {args[1]} {args[2]}\n")


def run_standalone():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SqueezeHTTPRequestHandler)
    print(f"🚀 Squeeze MCP Server running at http://0.0.0.0:{port}")
    print(f"   • MCP JSON-RPC: POST http://0.0.0.0:{port}/mcp")
    print(f"   • MCP SSE:      GET  http://0.0.0.0:{port}/sse")
    print(f"   • REST API:     POST http://0.0.0.0:{port}/shrink-logs")
    server.serve_forever()


if __name__ == "__main__":
    run_standalone()
