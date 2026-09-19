#!/usr/bin/env python3
"""
Squeeze AI - Demo Traffic & Metric Simulator
Simulates a burst of AWS log events, AST extractions, and JSON shrink operations,
pushing real metric points to the CloudWatch 'SqueezeAI' namespace to populate
the CloudWatch Dashboard with real-time graphs for hackathon judges.
"""

import os
import sys
import time
import random
import argparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "mcp-server"))
import squeeze_core as engine

try:
    import boto3
except ImportError:
    boto3 = None

def simulate_traffic(num_batches: int = 10, dry_run: bool = False):
    print("=" * 65)
    print("⚡ SQUEEZE AI - LIVE METRIC & TRAFFIC SIMULATOR")
    print("=" * 65)
    print(f"• Generating {num_batches} traffic iterations...")
    print(f"• Dry Run Mode: {dry_run}")

    cw = None
    if not dry_run and boto3:
        try:
            cw = boto3.client("cloudwatch", region_name=os.environ.get("AWS_REGION", "us-east-1"))
            print("• Connected to AWS CloudWatch client.")
        except Exception as e:
            print(f"⚠️ Could not initialize CloudWatch client ({e}). Falling back to dry run.")
            cw = None

    demo_data_dir = os.path.join(ROOT_DIR, "demo-data")
    with open(os.path.join(demo_data_dir, "raw_cloudwatch_dump.log")) as f:
        sample_logs = f.read()
    with open(os.path.join(demo_data_dir, "bloated_kinesis_records.json")) as f:
        sample_json = f.read()

    total_tokens_before = 0
    total_tokens_after = 0
    total_secrets_masked = 0

    for i in range(1, num_batches + 1):
        # 1. Log Shrinking Simulation
        log_multiplier = random.randint(2, 6)
        burst_logs = (sample_logs + "\n") * log_multiplier
        t_before_log = max(1, len(burst_logs) // 4)
        shrunk_logs = engine.shrink_logs_data(burst_logs)
        shrunk_logs, secrets = engine.mask_secrets(shrunk_logs)
        t_after_log = max(1, len(shrunk_logs) // 4)

        # 2. JSON Shrinking Simulation
        t_before_json = max(1, len(sample_json) // 4)
        shrunk_json = engine.shrink_json_data(sample_json, max_array_items=1)
        t_after_json = max(1, len(shrunk_json) // 4)

        batch_before = t_before_log + t_before_json
        batch_after = t_after_log + t_after_json
        batch_saved = batch_before - batch_after
        batch_secrets = secrets

        total_tokens_before += batch_before
        total_tokens_after += batch_after
        total_secrets_masked += batch_secrets

        cost_saved = (batch_saved / 1_000_000.0) * 3.00

        print(f"[{i:02d}/{num_batches:02d}] Ingested: {batch_before:,} tokens -> Squeezed: {batch_after:,} tokens | Saved: {batch_saved:,} ({(1-batch_after/batch_before)*100:.1f}%) | ${cost_saved:.4f}")

        if cw:
            try:
                cw.put_metric_data(
                    Namespace="SqueezeAI",
                    MetricData=[
                        {"MetricName": "TokensBefore", "Dimensions": [{"Name": "Pipeline", "Value": "CloudWatchLogs"}], "Value": batch_before, "Unit": "Count"},
                        {"MetricName": "TokensAfter", "Dimensions": [{"Name": "Pipeline", "Value": "CloudWatchLogs"}], "Value": batch_after, "Unit": "Count"},
                        {"MetricName": "TokensSaved", "Dimensions": [{"Name": "Pipeline", "Value": "CloudWatchLogs"}], "Value": batch_saved, "Unit": "Count"},
                        {"MetricName": "EstimatedCostSavedUSD", "Dimensions": [{"Name": "Pipeline", "Value": "CloudWatchLogs"}], "Value": cost_saved, "Unit": "None"},
                        {"MetricName": "SecretsMasked", "Dimensions": [{"Name": "Pipeline", "Value": "CloudWatchLogs"}], "Value": batch_secrets, "Unit": "Count"},
                    ]
                )
            except Exception as e:
                print(f"   ⚠️ CloudWatch write error: {e}")

        time.sleep(0.1)

    print("\n" + "=" * 65)
    print("🎉 TRAFFIC SIMULATION COMPLETE!")
    print(f"• Total Raw Tokens:      {total_tokens_before:,}")
    print(f"• Total Squeezed Tokens: {total_tokens_after:,}")
    total_saved = total_tokens_before - total_tokens_after
    pct = (total_saved / max(1, total_tokens_before)) * 100
    print(f"• Total Tokens Saved:    {total_saved:,} ({pct:.1f}% overall compression)")
    print(f"• Estimated USD Saved:   ${(total_saved/1_000_000.0)*3.00:.4f} (Claude Sonnet @ $3/M)")
    print(f"• Secrets Masked:        {total_secrets_masked}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate demo traffic to populate CloudWatch metrics")
    parser.add_argument("--batches", type=int, default=10, help="Number of traffic batches")
    parser.add_argument("--dry-run", action="store_true", help="Run locally without sending to AWS CloudWatch")
    args = parser.parse_args()
    simulate_traffic(args.batches, args.dry_run)
