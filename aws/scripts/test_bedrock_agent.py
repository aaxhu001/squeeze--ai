#!/usr/bin/env python3
"""
Squeeze AI - Bedrock Agent Test Runner
Invokes the deployed Amazon Bedrock Agent, demonstrates mid-conversation tool execution
calling Squeeze Action Group, and displays the reasoning trace with token savings.
"""

import os
import sys
import json
import uuid
import argparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import boto3
except ImportError:
    boto3 = None

def invoke_agent(agent_id: str, agent_alias_id: str = "live", prompt: str = ""):
    print("=" * 65)
    print("🤖 SQUEEZE AI - BEDROCK AGENT INVOCATION TEST")
    print("=" * 65)

    if not boto3:
        print("⚠️ boto3 is not installed. Please run: pip install boto3")
        sys.exit(1)

    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent-runtime", region_name=region)

    session_id = f"sqz-test-{uuid.uuid4().hex[:8]}"

    if not prompt:
        log_sample_path = os.path.join(ROOT_DIR, "demo-data", "raw_cloudwatch_dump.log")
        with open(log_sample_path) as f:
            logs = f.read()
        prompt = (
            "You are our incident response lead. Please analyze these raw CloudWatch logs, "
            "identify the root cause of the outage, and state your remediation plan. "
            f"Here are the logs:\n\n{logs}"
        )

    print(f"• Target Bedrock Agent ID:       {agent_id}")
    print(f"• Target Bedrock Agent Alias ID: {agent_alias_id}")
    print(f"• Session ID:                    {session_id}")
    print(f"• Input Prompt Size:             {len(prompt):,} chars (~{len(prompt)//4:,} raw tokens)")
    print("-" * 65)
    print("⚡ Sending request to Bedrock Agent (watching for Squeeze tool call)...")

    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
            enableTrace=True
        )

        event_stream = response.get("completion")
        full_response = ""

        for event in event_stream:
            # Inspect agent reasoning trace
            if "trace" in event:
                trace_data = event["trace"]["trace"]
                if "orchestrationTrace" in trace_data:
                    orch = trace_data["orchestrationTrace"]
                    if "invocationInput" in orch:
                        inv = orch["invocationInput"]
                        ag_name = inv.get("actionGroupInvocationInput", {}).get("actionGroupName", "")
                        tool_path = inv.get("actionGroupInvocationInput", {}).get("apiPath", "")
                        print(f"   ↳ 🛠️ Bedrock Agent Triggered Squeeze Action: {ag_name} -> {tool_path}")
                    elif "observation" in orch:
                        obs = orch["observation"]
                        print("   ↳ ⚡ Squeeze Action Result received by Bedrock Agent.")

            # Capture streamed output tokens
            if "chunk" in event:
                chunk_bytes = event["chunk"]["bytes"]
                full_response += chunk_bytes.decode("utf-8")

        print("-" * 65)
        print("🎉 BEDROCK AGENT FINAL RESPONSE:")
        print(full_response)
        print("=" * 65)

    except Exception as e:
        print(f"⚠️ Error invoking Bedrock Agent: {e}")
        print("\nTroubleshooting tips:")
        print("1. Verify that the Bedrock Agent is prepared and in 'PREPARED' state.")
        print("2. Ensure Bedrock Model Access is enabled in your AWS console for Claude 3.5 Sonnet.")
        print("3. Check that the Agent IAM Role has lambda:InvokeFunction permission.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Bedrock Agent with Squeeze Action Group")
    parser.add_argument("--agent-id", required=True, help="Bedrock Agent ID from CDK output")
    parser.add_argument("--agent-alias-id", default="live", help="Bedrock Agent Alias ID (default: live)")
    parser.add_argument("--prompt", default="", help="Custom prompt to send to the agent")
    args = parser.parse_args()

    invoke_agent(args.agent_id, args.agent_alias_id, args.prompt)
