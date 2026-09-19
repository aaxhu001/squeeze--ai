#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SqueezeMcpBedrockStack } from '../lib/squeeze-mcp-bedrock-stack';
import { SqueezeLogPipelineStack } from '../lib/squeeze-log-pipeline-stack';
import { SqueezeDashboardStack } from '../lib/squeeze-dashboard-stack';
import { SqueezeDevToolsStack } from '../lib/squeeze-dev-tools-stack';

const app = new cdk.App();

// Target AWS account & region from environment or defaults
const env: cdk.Environment = {
  account: process.env.CDK_DEFAULT_ACCOUNT || process.env.AWS_ACCOUNT_ID,
  region: process.env.CDK_DEFAULT_REGION || process.env.AWS_REGION || 'us-east-1',
};

// Global Bedrock Foundation Model ID (Claude 3.5 Sonnet default)
const bedrockModelId = process.env.BEDROCK_MODEL_ID || 'anthropic.claude-3-5-sonnet-20241022-v2:0';

// 1. Priority 1 (Hero Flow): Bedrock Agent + Squeeze Action Group + Remote MCP URL
const mcpBedrockStack = new SqueezeMcpBedrockStack(app, 'SqueezeMcpBedrockStack', {
  env,
  bedrockModelId,
  description: 'Priority 1: Squeeze Remote MCP Server and Bedrock Agent Action Group',
});

// 2. Priority 2: CloudWatch Logs -> Squeeze -> Bedrock Summarizer -> S3
const logPipelineStack = new SqueezeLogPipelineStack(app, 'SqueezeLogPipelineStack', {
  env,
  bedrockModelId,
  description: 'Priority 2: CloudWatch Logs Subscription Filter to Squeeze and Bedrock',
});

// 3. Live Token & Cost Savings Dashboard
const dashboardStack = new SqueezeDashboardStack(app, 'SqueezeDashboardStack', {
  env,
  description: 'CloudWatch Dashboard for real-time Squeeze token savings and metrics',
});

// 4. Priorities 3, 4, 5 & 6: Developer Tools (CI, Codebase Indexer, DLP Secret Shield)
const devToolsStack = new SqueezeDevToolsStack(app, 'SqueezeDevToolsStack', {
  env,
  description: 'Priorities 3, 4, 5: CodeBuild CI, Codebase Indexer API, and DLP Secret Shield',
});

// Global resource tags for easy tracking and clean billing audit
cdk.Tags.of(app).add('Project', 'Squeeze-AI');
cdk.Tags.of(app).add('ManagedBy', 'AWS-CDK');
cdk.Tags.of(app).add('Hackathon', 'Bedrock-Context-Optimizer');

app.synth();
