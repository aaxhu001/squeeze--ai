#!/usr/bin/env python3
"""
Squeeze AI - Local Test & Benchmark Suite
Validates all context compression tools, DLP Secret Shield, AST skeletons,
and Bedrock Action Group compatibility before cloud deployment.
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "mcp-server"))
sys.path.insert(0, os.path.join(ROOT_DIR, "lambdas/bedrock-action-handler"))

import squeeze_core as engine
from app import lambda_handler as mcp_lambda_handler
from index import lambda_handler as action_group_handler

class TestSqueezeAIEngine(unittest.TestCase):
    def setUp(self):
        self.demo_data_dir = os.path.join(ROOT_DIR, "demo-data")

    def test_01_shrink_logs(self):
        """Test log deduplication, timestamp stripping, and stack trace collapsing."""
        log_path = os.path.join(self.demo_data_dir, "raw_cloudwatch_dump.log")
        with open(log_path, "r", encoding="utf-8") as f:
            raw_logs = f.read()

        orig_len = len(raw_logs)
        shrunk = engine.shrink_logs_data(raw_logs)
        shrunk_len = len(shrunk)

        print(f"\n[Test 1: Logs] Raw: {orig_len} bytes -> Shrunk: {shrunk_len} bytes")
        self.assertLess(shrunk_len, orig_len)
        self.assertIn("Squeeze AI: Repeated", shrunk)
        savings_pct = (1.0 - (shrunk_len / orig_len)) * 100
        print(f"   ↳ Log Compression Savings: {savings_pct:.1f}%")
        self.assertGreater(savings_pct, 25.0)

    def test_02_shrink_json(self):
        """Test JSON array folding and long hash truncation."""
        json_path = os.path.join(self.demo_data_dir, "bloated_kinesis_records.json")
        with open(json_path, "r", encoding="utf-8") as f:
            raw_json = f.read()

        orig_len = len(raw_json)
        shrunk = engine.shrink_json_data(raw_json, max_array_items=1)
        shrunk_len = len(shrunk)

        print(f"\n[Test 2: JSON] Raw: {orig_len} bytes -> Shrunk: {shrunk_len} bytes")
        self.assertIn("collapsed by Squeeze AI", shrunk)
        savings_pct = (1.0 - (shrunk_len / orig_len)) * 100
        print(f"   ↳ JSON Compression Savings: {savings_pct:.1f}%")
        self.assertGreater(savings_pct, 40.0)

    def test_03_skeletonize_code(self):
        """Test AST structural skeleton extraction."""
        code_path = os.path.join(self.demo_data_dir, "sample_repo_snippet.py")
        with open(code_path, "r", encoding="utf-8") as f:
            raw_code = f.read()

        orig_len = len(raw_code)
        skeleton = engine.skeletonize_code(raw_code, "python")
        skel_len = len(skeleton)

        print(f"\n[Test 3: AST Skeleton] Raw: {orig_len} bytes -> Skeleton: {skel_len} bytes")
        self.assertIn("class OrderProcessor", skeleton)
        self.assertIn("def validate_order", skeleton)
        # Function implementation stripped with ellipsis
        self.assertIn("...", skeleton)
        savings_pct = (1.0 - (skel_len / orig_len)) * 100
        print(f"   ↳ AST Skeleton Savings: {savings_pct:.1f}%")
        self.assertGreater(savings_pct, 40.0)

    def test_04_dlp_secret_shield(self):
        """Test scanning and masking 8 major credential signatures."""
        leak_path = os.path.join(self.demo_data_dir, "leak_with_credentials.txt")
        with open(leak_path, "r", encoding="utf-8") as f:
            raw_creds = f.read()

        sanitized, count = engine.mask_secrets(raw_creds)
        print(f"\n[Test 4: DLP Secret Shield] Detected & Masked: {count} credentials")
        self.assertGreaterEqual(count, 6)
        self.assertIn("[MASKED_AWS_ACCESS_KEY]", sanitized)
        self.assertIn("[MASKED_OPENAI_KEY]", sanitized)
        self.assertIn("[MASKED_ANTHROPIC_KEY]", sanitized)
        self.assertIn("[MASKED_GOOGLE_KEY]", sanitized)
        self.assertIn("[MASKED_GITHUB_TOKEN]", sanitized)
        self.assertIn("[MASKED_JWT]", sanitized)
        self.assertIn("[MASKED_PASSWORD]", sanitized)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", sanitized)

    def test_05_reversible_chunks(self):
        """Test reversible chunking (CCR) and lossless retrieval."""
        long_text = "This is a verbose developer prompt that needs reversible chunking. " * 15
        res = engine.optimize_prompt(long_text, store_reversible=True)
        chunk_id = res["chunk_id"]
        self.assertIsNotNone(chunk_id)
        self.assertIn(f'[SQUEEZE_CHUNK id="{chunk_id}"', res["optimized"])

        retrieved = engine.retrieve_chunk(chunk_id)
        print(f"\n[Test 5: CCR Retrieval] Stored chunk: {chunk_id} -> Lossless retrieval: {retrieved == long_text}")
        self.assertEqual(retrieved, long_text)

    def test_06_codebase_graph(self):
        """Test topological dependency graph generation."""
        graph_md = engine.generate_codebase_graph(ROOT_DIR, max_files=10)
        print(f"\n[Test 6: Codebase Graph] Generated {len(graph_md)} characters of markdown")
        self.assertIn("SQUEEZE CODEBASE TOPOLOGICAL GRAPH", graph_md)
        self.assertIn("Core Architecture Hubs", graph_md)

    def test_07_bedrock_action_group_event(self):
        """Test Bedrock Agent Action Group request routing."""
        event = {
            "messageVersion": "1.0",
            "actionGroup": "SqueezeOptimizerGroup",
            "apiPath": "/shrink-logs",
            "httpMethod": "POST",
            "requestBody": {
                "content": {
                    "application/json": {
                        "properties": [
                            {"name": "log_text", "type": "string", "value": "2026-09-19 ERROR db down\n2026-09-19 ERROR db down"}
                        ]
                    }
                }
            }
        }
        res = action_group_handler(event, None)
        self.assertEqual(res["messageVersion"], "1.0")
        self.assertEqual(res["response"]["httpStatusCode"], 200)
        body = json.loads(res["response"]["responseBody"]["application/json"]["body"])
        self.assertIn("compressed_logs", body)
        print(f"\n[Test 7: Bedrock Action Group] Handled successfully: {body['savings_pct']} saved")

    def test_08_mcp_lambda_function_url(self):
        """Test MCP JSON-RPC 2.0 tools/call execution via Lambda Function URL."""
        event = {
            "rawPath": "/mcp",
            "requestContext": {"http": {"method": "POST"}},
            "body": json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "squeeze_shrink_logs",
                    "arguments": {"log_text": "line 1\nline 1\nline 1"}
                }
            })
        }
        res = mcp_lambda_handler(event, None)
        self.assertEqual(res["statusCode"], 200)
        body = json.loads(res["body"])
        self.assertEqual(body["jsonrpc"], "2.0")
        self.assertIn("content", body["result"])
        print("\n[Test 8: Remote MCP JSON-RPC] Successfully executed squeeze_shrink_logs via Function URL")

if __name__ == "__main__":
    unittest.main(verbosity=2)
