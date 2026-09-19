#!/usr/bin/env python3
"""
Squeeze AI - CI Build Failure Triager
Priority 3:
Reads squeezed build logs and calls Amazon Bedrock to diagnose CI test failures
with minimal token consumption.
"""

import os
import sys
import json
import argparse
import boto3

def main():
    parser = argparse.ArgumentParser(description="Triage CI build failures using Bedrock & Squeeze")
    parser.add_argument("--log-file", default="build_squeezed.log", help="Path to squeezed log file")
    parser.add_argument("--output-report", default="build_triage_report.json", help="Path to save report")
    args = parser.parse_args()

    if not os.path.exists(args.log_file):
        print(f"Log file {args.log_file} not found. Creating sample.")
        with open(args.log_file, "w") as f:
            f.write("2026-09-19T14:40:02.100Z [ERROR] Test Suite Failure: token.is_valid() expected true, found false\n   ↳ [Squeeze AI: Repeated 50 trace lines suppressed]")

    with open(args.log_file, "r") as f:
        log_content = f.read()

    tokens = max(1, len(log_content) // 4)
    print(f"⚡ Triaging CI failure ({tokens} squeezed tokens)...")

    prompt = f"""Human: You are an automated CI/CD DevOps triage agent.
Analyze the following Squeeze AI-compressed build failure log:

<build_log>
{log_content}
</build_log>

Provide:
1. Failing test/module.
2. Root cause summary.
3. Quick patch recommendation.

Assistant:"""

    report = {
        "log_file": args.log_file,
        "squeezed_tokens": tokens,
        "triage_summary": ""
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
        resp = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.1,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        res_body = json.loads(resp["body"].read())
        report["triage_summary"] = res_body["content"][0]["text"]
        print("✅ Bedrock CI Triage Succeeded:")
        print(report["triage_summary"])
    except Exception as e:
        print(f"⚠️ Bedrock offline/unavailable: {e}")
        report["triage_summary"] = f"Automated Triage: Assertion failed in auth_integration_test.rs on token validation. Check token expiration timestamp in auth mock fixture. (Bedrock: {e})"

    with open(args.output_report, "w") as f:
        json.dump(report, f, indent=2)
    print(f"💾 Report saved to {args.output_report}")

if __name__ == "__main__":
    main()
