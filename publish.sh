#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$DIR/website"
DOMAIN="${1:-squeeze-ai.surge.sh}"

echo "=========================================="
echo "🚀 Publishing Squeeze AI to https://$DOMAIN"
echo "=========================================="

npx surge "$TARGET_DIR" "$DOMAIN"

echo ""
echo "🎉 Live at: https://$DOMAIN"
