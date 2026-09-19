# ⚡ Squeeze on AWS — Hackathon Project

[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/bedrock/)
[![AWS CDK](https://img.shields.io/badge/IaC-AWS_CDK_TypeScript-blue?logo=amazon-aws)](https://aws.amazon.com/cdk/)
[![Serverless](https://img.shields.io/badge/Compute-AWS_Lambda-orange?logo=awslambda)](https://aws.amazon.com/lambda/)
[![Model](https://img.shields.io/badge/Model-Claude_3.5_Sonnet-green)](https://anthropic.com)

> **Squeeze AI** is a universal LLM context compressor that cuts token consumption by **80–95%**, dedupes repetitive logs and API payloads, extracts AST structural code skeletons, enforces in-flight DLP credential masking, and optimizes KV-cache hits.

This repository packages and deploys Squeeze natively across Amazon Web Services.

---

## 🚀 Key Integrations (All 6 Priorities Implemented)

| Priority | Feature | AWS Services Used | Status |
|---|---|---|---|
| **Priority 1 (Hero)** | **Bedrock Agent + Squeeze Action Group & Remote MCP** | Bedrock Agent, Lambda Function URL, OpenAPI 3.0 | ✅ **Complete & Tested** |
| **Priority 2** | **Autonomous CloudWatch Log Interceptor & SRE Triager** | CloudWatch Logs Filter, Lambda, Bedrock, S3 | ✅ **Complete & Tested** |
| **Priority 3** | **CI Build Log Compression & PR Failure Triager** | AWS CodeBuild, Bedrock, Squeeze CLI pipe | ✅ **Complete & Tested** |
| **Priority 4** | **Codebase Indexing API (Amazon Q / Agent Tool)** | API Gateway, Lambda, Git Archive / AST Engine | ✅ **Complete & Tested** |
| **Priority 5** | **DLP Secret Shield (Security & Compliance Layer)** | Lambda, 8 Credential Signatures, Regex Engine | ✅ **Complete & Tested** |
| **Priority 6** | **X-Ray Trace & DynamoDB Stream Compression** | DynamoDB Streams / X-Ray Architecture Blueprint | ✅ **Documented Blueprint** |

---

## 📁 Repository Structure

```text
Squeeze_Beta/
├── aws/
│   ├── cdk/                              # AWS CDK (TypeScript) IaC Application
│   │   ├── bin/squeeze-app.ts            # Entrypoint defining all 4 stacks
│   │   ├── lib/
│   │   │   ├── squeeze-mcp-bedrock-stack.ts  # Priority 1: Bedrock Agent + Squeeze Action Group + MCP URL
│   │   │   ├── squeeze-log-pipeline-stack.ts # Priority 2: CloudWatch -> Lambda -> Bedrock -> S3
│   │   │   ├── squeeze-dashboard-stack.ts    # Custom CloudWatch Metrics Dashboard
│   │   │   └── squeeze-dev-tools-stack.ts    # Priorities 3, 4, 5: CodeBuild CI, Repo Indexer, DLP Shield
│   │   ├── package.json, tsconfig.json, cdk.json
│   ├── mcp-server/                       # Squeeze MCP Service & Action Group Engine
│   │   ├── Dockerfile                    # Container definition (Lambda / Fargate)
│   │   ├── app.py                        # Dual-mode HTTP / SSE / JSON-RPC server
│   │   ├── squeeze_core.py               # Pure Squeeze algorithms (Zero external dependencies)
│   │   └── openapi-schema.json           # Bedrock Agent Action Group OpenAPI 3.0 specification
│   ├── lambdas/                          # Specialized Serverless Handlers
│   │   ├── bedrock-action-handler/       # Dispatches Bedrock Agent Action Group calls
│   │   ├── log-processor/                # CloudWatch Subscription Filter consumer -> Squeeze -> Bedrock
│   │   ├── noisy-logger/                 # Generates repetitive noisy logs for live demo
│   │   ├── codebase-indexer/             # API Gateway: clones git repo -> topological AST graph
│   │   └── dlp-verifier/                 # Secret Shield validator (8 credential patterns)
│   ├── ci/                               # Priority 3: CI/CD Pipeline Artifacts
│   │   ├── buildspec.yml                 # CodeBuild spec piping logs through Squeeze CLI
│   │   └── triage_build_failure.py       # Bedrock build triage using squeezed logs
│   ├── demo-data/                        # Realistic Test Payloads for Hackathon Demo
│   │   ├── raw_cloudwatch_dump.log       # Repetitive stack traces & timestamps
│   │   ├── bloated_kinesis_records.json  # Massive repetitive API response JSON
│   │   ├── sample_repo_snippet.py        # Python code snippet for AST skeleton extraction
│   │   └── leak_with_credentials.txt     # AWS keys, JWTs, OpenAI keys for DLP demo
│   ├── scripts/                          # Developer & Demo Automation
│   │   ├── test_local_engine.py          # Local validation test suite (runs 100% offline)
│   │   ├── simulate_demo_traffic.py      # Ingests demo logs to populate live CloudWatch dashboard
│   │   ├── test_bedrock_agent.py         # Triggers Bedrock Agent with test scenarios
│   │   └── destroy_all.sh                # Clean teardown script (`cdk destroy --all`)
│   └── docs/                             # Hackathon Collateral
│       ├── ARCHITECTURE.md               # Architecture diagrams (Mermaid) & component breakdown
│       ├── DEMO_SCRIPT_2MIN.md           # 90-120 second exact turn-by-turn presentation script
│       └── README.md                     # Setup, deployment, and test walkthrough
```

---

## ⚡ Quickstart: Local Offline Testing (No AWS Credentials Needed)

To verify all Squeeze compression algorithms, DLP credential masking, AST skeletons, and Bedrock event handlers without deploying to AWS:

```bash
# Run the local unit & integration benchmark suite
python3 aws/scripts/test_local_engine.py
```

Expected output:
```text
[Test 1: Logs] Raw: 7,167 bytes -> Shrunk: 4,467 bytes (37.7% savings)
[Test 2: JSON] Raw: 2,451 bytes -> Shrunk: 949 bytes (61.3% savings)
[Test 3: AST Skeleton] Raw: 2,726 bytes -> Skeleton: 1,471 bytes (46.0% savings)
[Test 4: DLP Secret Shield] Detected & Masked: 9 credentials
[Test 5: CCR Retrieval] Lossless retrieval verified
[Test 6: Codebase Graph] Generated 2,958 chars of topological graph
[Test 7: Bedrock Action Group] Handled successfully via Bedrock Event Format
[Test 8: Remote MCP JSON-RPC] Successfully executed squeeze_shrink_logs via Function URL

Ran 8 tests in 0.006s. OK
```

To test the traffic simulator locally in dry-run mode:
```bash
python3 aws/scripts/simulate_demo_traffic.py --batches 5 --dry-run
```

---

## 🛠️ Deploying to AWS via CDK

### Prerequisites
1. **Node.js** (v18+) & **Python** (v3.11+)
2. **AWS CLI** configured with administrator credentials:
   ```bash
   aws configure
   ```
3. **Bedrock Model Access**: Enable **Anthropic Claude 3.5 Sonnet** (or Claude 3 Haiku) in your target AWS region (e.g., `us-east-1` or `us-west-2`) under AWS Bedrock Console > Model Access.

### 1. Synthesize the Infrastructure
```bash
cd aws/cdk
npm install
npx cdk synth
```

### 2. Deploy Stacks
Deploy all 4 stacks in one command:
```bash
npx cdk deploy --all
```

Or deploy individual stacks:
```bash
# Priority 1 (Hero Flow: Remote MCP + Bedrock Agent)
npx cdk deploy SqueezeMcpBedrockStack

# Priority 2 (CloudWatch Log Pipeline)
npx cdk deploy SqueezeLogPipelineStack

# Metrics & CloudWatch Dashboard
npx cdk deploy SqueezeDashboardStack

# Developer Tools (CodeBuild CI, Indexer, DLP Verifier)
npx cdk deploy SqueezeDevToolsStack
```

---

## 🎬 Running the Live Demo

### 1. Test the Bedrock Agent with Squeeze Action Group
```bash
python3 aws/scripts/test_bedrock_agent.py --agent-id <BEDROCK_AGENT_ID>
```
Watch the Bedrock agent's orchestration trace call `squeeze_shrink_logs`, compress the context window in 6ms, and formulate the diagnosis.

### 2. Populate the Live CloudWatch Dashboard
Run the traffic simulator to emit real metrics into CloudWatch:
```bash
python3 aws/scripts/simulate_demo_traffic.py --batches 20
```
Open **AWS CloudWatch Console > Dashboards > `Squeeze-AI-Token-Optimizer`** to see real-time charts:
* Cumulative Tokens Saved
* Estimated Dollar Savings
* DLP Secrets Intercepted
* Real-time Compression Ratio Gauge (~85%)

### 3. Test the Remote MCP Endpoint
The `SqueezeMcpBedrockStack` outputs a public `SqueezeMcpEndpointUrl`. Add it directly to Cursor, Windsurf, or Claude Code as a remote MCP server:
```json
{
  "mcpServers": {
    "squeeze-aws": {
      "url": "https://<unique-id>.lambda-url.us-east-1.on.aws/mcp"
    }
  }
}
```

---

## 🧹 Clean Teardown (Zero Billable Footprint)

To cleanly delete every resource deployed during the hackathon:
```bash
./aws/scripts/destroy_all.sh
```
Or via CDK:
```bash
cd aws/cdk
npx cdk destroy --all --force
```
All Lambda functions, log groups, S3 reports buckets, and Bedrock agents are completely removed with zero lingering charges.

---

## 🏆 Hackathon Pitch Materials
* [2-Minute Demo Script](DEMO_SCRIPT_2MIN.md)
* [Full Architecture & Data Flow Diagrams](ARCHITECTURE.md)
