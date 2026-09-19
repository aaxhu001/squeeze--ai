#!/usr/bin/env python3
"""
Squeeze AI - DLP Secret Shield Verifier
Priority 5:
Demonstrates in-flight Data Loss Prevention (DLP) sanitization across 8 credential formats
before sensitive data reaches LLM provider prompts and third-party APIs.
"""

import os
import sys
import json
import boto3

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import squeeze_core as engine

SAMPLE_LEAKED_PAYLOAD = """
2026-09-19 14:02:11 [DEBUG] Initializing payment service clients:
- AWS Production Key: AKIAIOSFODNN7EXAMPLE (Secret: aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
- OpenAI Pipeline Key: sk-proj-abCDefGhIjKlMnOpQrStUvWxYz1234567890
- Anthropic Bedrock Mirror: sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890
- Google Vertex Key: AIzaSyD3xY_SAMPLE_KEY_GOOGLE_API_CREDENTIALS_12345
- GitHub Deploy Token: ghp_1234567890abcdefghijklmnopqrstuvwxyzAB
- User Authorization Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
- Primary PostgreSQL Cluster: postgresql://admin_user:SuperSecretP@ssw0rd123!@aurora-cluster.us-east-1.rds.amazonaws.com:5432/production_db
"""

def lambda_handler(event, context):
    input_text = ""
    if "body" in event and event["body"]:
        try:
            body = json.loads(event["body"])
            input_text = body.get("text", "")
        except Exception:
            input_text = event["body"]
    elif isinstance(event, dict) and "text" in event:
        input_text = event["text"]
    
    if not input_text:
        input_text = SAMPLE_LEAKED_PAYLOAD

    sanitized, secrets_count = engine.mask_secrets(input_text)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "status": "sanitized",
            "secrets_detected_and_masked": secrets_count,
            "credential_signatures_supported": [
                "AWS Access Keys & Secret Keys",
                "OpenAI Project & Live Keys",
                "Anthropic API Keys",
                "Google Cloud API Keys",
                "GitHub Personal Access & Deploy Tokens",
                "JSON Web Tokens (JWT)",
                "Database Connection Strings (Postgres, Mongo, MySQL)"
            ],
            "raw_input": input_text,
            "sanitized_output": sanitized
        }, indent=2)
    }

if __name__ == "__main__":
    res = lambda_handler({}, None)
    print(res["body"])
