#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
CDK_DIR="$DIR/../cdk"

echo "=========================================================="
echo "⚠️  SQUEEZE AI - COMPLETE AWS INFRASTRUCTURE TEARDOWN"
echo "=========================================================="
echo "This will destroy all 4 CDK stacks:"
echo " 1. SqueezeMcpBedrockStack (MCP Function URL & Bedrock Agent)"
echo " 2. SqueezeLogPipelineStack (Noisy Logger, CloudWatch Filter, S3 Reports Bucket)"
echo " 3. SqueezeDashboardStack (CloudWatch Metrics Dashboard)"
echo " 4. SqueezeDevToolsStack (CodeBuild CI, Indexer, DLP Verifier)"
echo ""
echo "All temporary S3 data and Lambda compute will be deleted with ZERO remaining charges."
echo "=========================================================="

read -p "Are you sure you want to delete all Squeeze AWS resources? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Teardown aborted."
    exit 0
fi

echo "• Destroying CDK stacks..."
cd "$CDK_DIR"
npx cdk destroy --all --force

echo ""
echo "=========================================================="
echo "🎉 TEARDOWN COMPLETE! All AWS resources have been cleanly removed."
echo "=========================================================="
