#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
WEBSITE_DIR="$DIR/website"

echo "========================================================"
echo "⚡ AWS S3 & CloudFront Deployment for Squeeze AI"
echo "========================================================"

# 1. Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "⚠️ AWS CLI is not installed."
    echo "Installing AWS CLI via Homebrew / pip..."
    if command -v brew &> /dev/null; then
        brew install awscli
    else
        python3 -m pip install --user awscli
    fi
fi

# 2. Check AWS Credentials
echo "• Verifying AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️ No active AWS credentials found."
    echo "Please run: aws configure"
    echo "Enter your AWS Access Key ID, Secret Access Key, and Default Region (e.g. us-east-1)."
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
BUCKET_NAME="${1:-squeeze-ai-hackathon-$ACCOUNT_ID}"

echo "• Deploying to Bucket: $BUCKET_NAME in region $REGION"

# 3. Create S3 Bucket if it doesn't exist
if ! aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "• Creating bucket: $BUCKET_NAME..."
    if [ "$REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION"
    else
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION"
    fi
fi

# 4. Configure Public Access & Website Hosting
echo "• Configuring bucket for static website hosting..."
aws s3api delete-public-access-block --bucket "$BUCKET_NAME" || true

POLICY=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
        }
    ]
}
EOF
)

aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy "$POLICY"
aws s3api put-bucket-website --bucket "$BUCKET_NAME" --website-configuration '{"IndexDocument":{"Suffix":"index.html"},"ErrorDocument":{"Key":"index.html"}}'

# 5. Sync website assets
echo "• Syncing website files to S3..."
aws s3 sync "$WEBSITE_DIR" "s3://$BUCKET_NAME" --delete

# 6. Output URL
if [ "$REGION" = "us-east-1" ]; then
    ENDPOINT="http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
else
    ENDPOINT="http://$BUCKET_NAME.s3-website.$REGION.amazonaws.com"
fi

echo ""
echo "========================================================"
echo "🎉 AWS DEPLOYMENT COMPLETE!"
echo "• Live AWS S3 Website URL: $ENDPOINT"
echo "========================================================"
