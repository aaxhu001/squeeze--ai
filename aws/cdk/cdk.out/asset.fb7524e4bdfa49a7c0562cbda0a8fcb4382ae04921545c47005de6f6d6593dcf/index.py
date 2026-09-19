#!/usr/bin/env python3
"""
Amazon Bedrock Agent Action Group Handler for Squeeze AI
Translates Bedrock Agent tool calls to Squeeze context optimization routines.
"""

import json
import os
import sys


# Ensure squeeze_core is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    import squeeze_core as engine
except ImportError:
    # If deployed with root app
    sys.path.insert(0, os.path.join(CURRENT_DIR, "../../mcp-server"))
    import squeeze_core as engine

try:
    import boto3
    cloudwatch = boto3.client("cloudwatch")
except Exception:
    cloudwatch = None

def emit_metrics(tool_name: str, tokens_before: int, tokens_after: int, secrets_masked: int = 0):
    """Emits custom CloudWatch metrics for Squeeze usage."""
    if not cloudwatch:
        return
    try:
        tokens_saved = max(0, tokens_before - tokens_after)
        cloudwatch.put_metric_data(
            Namespace="SqueezeAI",
            MetricData=[
                {
                    "MetricName": "TokensBefore",
                    "Dimensions": [{"Name": "ToolName", "Value": tool_name}],
                    "Value": tokens_before,
                    "Unit": "Count"
                },
                {
                    "MetricName": "TokensAfter",
                    "Dimensions": [{"Name": "ToolName", "Value": tool_name}],
                    "Value": tokens_after,
                    "Unit": "Count"
                },
                {
                    "MetricName": "TokensSaved",
                    "Dimensions": [{"Name": "ToolName", "Value": tool_name}],
                    "Value": tokens_saved,
                    "Unit": "Count"
                },
                {
                    "MetricName": "SecretsMasked",
                    "Dimensions": [{"Name": "ToolName", "Value": tool_name}],
                    "Value": secrets_masked,
                    "Unit": "Count"
                }
            ]
        )
    except Exception as e:
        print(f"Warning: CloudWatch metric emission skipped: {e}")


def lambda_handler(event, context):
    print("Received Bedrock Agent Action Group Event:", json.dumps(event))

    action_group = event.get("actionGroup", "SqueezeOptimizer")
    api_path = event.get("apiPath", "")
    http_method = event.get("httpMethod", "POST")

    # Extract input arguments from requestBody and parameters
    args = {}
    if "requestBody" in event and "content" in event["requestBody"]:
        app_json = event["requestBody"]["content"].get("application/json", {})
        props = app_json.get("properties", [])
        for p in props:
            args[p.get("name")] = p.get("value")

    for param in event.get("parameters", []):
        args[param.get("name")] = param.get("value")

    result = {}
    tokens_before = 0
    tokens_after = 0
    secrets_masked = 0

    try:
        if api_path == "/shrink-logs" or api_path == "/squeeze_shrink_logs":
            log_text = args.get("log_text") or args.get("logs") or ""
            tokens_before = max(1, len(log_text) // 4)
            shrunk = engine.shrink_logs_data(log_text)
            tokens_after = max(1, len(shrunk) // 4)
            result = {
                "compressed_logs": shrunk,
                "original_tokens": tokens_before,
                "compressed_tokens": tokens_after,
                "tokens_saved": max(0, tokens_before - tokens_after),
                "savings_pct": f"{round((1 - tokens_after/tokens_before)*100, 1)}%"
            }
            emit_metrics("squeeze_shrink_logs", tokens_before, tokens_after)

        elif api_path == "/shrink-json" or api_path == "/squeeze_shrink_json":
            json_text = args.get("json_text") or "{}"
            max_items = int(args.get("max_array_items", 2))
            tokens_before = max(1, len(json_text) // 4)
            shrunk = engine.shrink_json_data(json_text, max_items)
            tokens_after = max(1, len(shrunk) // 4)
            result = {
                "shrunk_json": shrunk,
                "original_tokens": tokens_before,
                "shrunk_tokens": tokens_after,
                "tokens_saved": max(0, tokens_before - tokens_after),
                "savings_pct": f"{round((1 - tokens_after/tokens_before)*100, 1)}%"
            }
            emit_metrics("squeeze_shrink_json", tokens_before, tokens_after)

        elif api_path == "/skeleton" or api_path == "/squeeze_skeleton":
            code = args.get("code") or ""
            lang = args.get("language") or "python"
            tokens_before = max(1, len(code) // 4)
            skel = engine.skeletonize_code(code, lang)
            tokens_after = max(1, len(skel) // 4)
            result = {
                "skeleton": skel,
                "original_tokens": tokens_before,
                "skeleton_tokens": tokens_after,
                "tokens_saved": max(0, tokens_before - tokens_after),
                "savings_pct": f"{round((1 - tokens_after/tokens_before)*100, 1)}%"
            }
            emit_metrics("squeeze_skeleton", tokens_before, tokens_after)

        elif api_path == "/compress" or api_path == "/squeeze_compress":
            text = args.get("text") or ""
            opt_res = engine.optimize_prompt(text, store_reversible=True)
            result = opt_res
            emit_metrics("squeeze_compress", opt_res["original_tokens"], opt_res["optimized_tokens"], opt_res.get("secrets_masked", 0))

        elif api_path == "/codebase-graph" or api_path == "/squeeze_codebase_graph":
            target = args.get("directory_path", ".")
            max_f = int(args.get("max_files", 50))
            graph = engine.generate_codebase_graph(target, max_f)
            result = {"graph_markdown": graph}
            emit_metrics("squeeze_codebase_graph", 1000, 200)

        elif api_path == "/retrieve" or api_path == "/squeeze_retrieve":
            cid = args.get("chunk_id", "")
            orig = engine.retrieve_chunk(cid)
            result = {"original_text": orig or "", "found": orig is not None}

        elif api_path == "/stats" or api_path == "/squeeze_stats":
            result = engine.get_stats()

        else:
            result = {"error": f"Unknown tool apiPath: {api_path}"}

    except Exception as e:
        print(f"Error executing Squeeze action: {e}")
        result = {"error": str(e)}

    # Bedrock Agent Action Group response format
    response_body = {
        "application/json": {
            "body": json.dumps(result)
        }
    }

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpStatusCode": 200,
            "responseBody": response_body
        }
    }
