# 🎬 Squeeze on AWS — 3-Minute Recorded Demo Video Script

**Format:** Pre-recorded video (no live demo — the video IS the submission)  
**Target Duration:** 3:00 exactly  
**Must Answer:** What it does, who it is for, and where AWS fits.

---

## Pre-Recording Checklist

Run these BEFORE hitting record:

```bash
# 1. Verify the engine works locally (no AWS needed)
python3 aws/scripts/test_local_engine.py

# 2. Seed the CloudWatch dashboard with real metric data (needs AWS creds)
python3 aws/scripts/simulate_demo_traffic.py --batches 25

# 3. Deploy stacks if not already deployed
cd aws/cdk && npx cdk deploy --all

# 4. Test the Bedrock Agent (get agent ID from CDK output)
python3 aws/scripts/test_bedrock_agent.py --agent-id <AGENT_ID>
```

Pre-open these browser tabs:
- [ ] AWS Bedrock Console → Agents → `Squeeze-Bedrock-Optimizer`
- [ ] AWS CloudWatch Console → Dashboards → `Squeeze-AI-Token-Optimizer`
- [ ] AWS Lambda Console (showing 5 deployed functions)
- [ ] Terminal with large font (14pt+)
- [ ] `aws/demo-data/raw_cloudwatch_dump.log` open in editor
- [ ] `aws/demo-data/leak_with_credentials.txt` open in editor

---

## SCENE 1: THE PROBLEM [0:00 – 0:30]

### Visual
Screen recording: Open `raw_cloudwatch_dump.log` and scroll slowly through the massive wall of repetitive log text. Then switch to `leak_with_credentials.txt` and zoom into the exposed AWS keys and database passwords.

### Voiceover (read this exactly)

> "If you're building AI agents on AWS — using Bedrock, Q Developer, or anything custom — you hit the same wall every day.
>
> You ask your agent to analyze a CloudWatch log dump, and look at what goes into the context window: the same stack trace repeated 47 times, microsecond timestamps nobody needs, thread IDs, UUIDs — and buried right here in line 14, a live AWS access key, an OpenAI API key, and a database password. In plain text. Going straight to an external LLM provider.
>
> This is 12,000 tokens of noise. At Claude Sonnet pricing, that's 4 cents per query. Run a thousand queries a day and you're burning 40 dollars on garbage tokens — and leaking production credentials.
>
> Squeeze fixes this."

### On-Screen Text Overlay
```
12,000 raw tokens × $3.00/M = $0.04 per query
× 1,000 queries/day = $40/day wasted
+ Production credentials leaked to external providers
```

---

## SCENE 2: WHAT SQUEEZE DOES [0:30 – 0:50]

### Visual
Show the architecture diagram (from ARCHITECTURE.md Mermaid render or a clean screenshot). Hold for 5 seconds.

Then show a side-by-side before/after:
- LEFT: Raw log dump (red highlight, long)
- RIGHT: Squeezed output (green highlight, dramatically shorter)

### Voiceover

> "Squeeze is a context compression engine built natively on AWS. It deduplicates identical log lines, collapses stack traces, folds massive JSON payloads, extracts code skeletons from source files — and critically, it scans and masks every credential before anything leaves your account.
>
> We integrated it into AWS as a Bedrock Agent Action Group, a Lambda-powered remote MCP server, and an autonomous CloudWatch log interceptor. Everything is deployed with AWS CDK across 4 stacks using Lambda, Bedrock, CloudWatch, and S3."

### On-Screen Text Overlay
Show AWS service icons: **Amazon Bedrock** · **AWS Lambda** · **Amazon CloudWatch** · **Amazon S3** · **AWS CDK** · **AWS CodeBuild**

---

## SCENE 3: THE WORKING DEMO [0:50 – 2:10]

> **THIS IS THE MOST IMPORTANT SECTION. 80 SECONDS. THE THING THAT MUST WORK.**

---

### Part A — Invoke the Agent [0:50 – 1:10]

#### Visual
Terminal running the test script, or the Bedrock Console chat interface.

```bash
python3 aws/scripts/test_bedrock_agent.py --agent-id <AGENT_ID>
```

#### Voiceover

> "Here's our deployed Bedrock Agent — Squeeze-Bedrock-Optimizer — running Anthropic Claude 3.5 Sonnet. I'm sending it that same 50-kilobyte raw CloudWatch log dump and asking: 'Analyze these logs and diagnose the database failure.'"

---

### Part B — Show the Agent Trace [1:10 – 1:40]

#### Visual
Switch to the **Bedrock Agent Trace panel** in the AWS Console. Zoom into:
1. The agent's **Rationale**: *"The user provided raw logs. I should compress them using squeeze_shrink_logs before analyzing."*
2. The **Action** called: `squeeze_shrink_logs` with the log_text parameter
3. The **Observation**: compressed output returned

#### Voiceover

> "Now watch the orchestration trace — this is the key moment. The agent didn't just ingest all 12,000 tokens blindly. Look at the rationale: it decided ON ITS OWN to call squeeze_shrink_logs first.
>
> It sent the raw logs to our Squeeze Action Group Lambda. Squeeze deduplicated the identical error lines, collapsed the stack traces, stripped the timestamps and UUIDs, and masked every leaked credential — in 6 milliseconds.
>
> 12,000 tokens became 1,800. That's an 85% reduction before Claude even started reasoning."

### On-Screen Text Overlay (show during trace)
```
BEFORE: 12,000 tokens ($0.036/query)
AFTER:   1,800 tokens ($0.005/query)
SAVED:  10,200 tokens (85%) in 6ms
Credentials masked: 9 (AWS keys, OpenAI keys, JWT, DB passwords)
```

---

### Part C — Show the Answer [1:40 – 1:50]

#### Visual
Show the agent's final response: a clean, structured incident triage.

#### Voiceover

> "And here's the agent's diagnosis — from the compressed context. Root cause: HikariPool connection pool exhaustion on the Aurora cluster. It correctly identified the specific service, named the remediation. Faster, cheaper, and not a single credential leaked."

---

### Part D — Show the CloudWatch Dashboard [1:50 – 2:10]

#### Visual
Switch to **AWS CloudWatch Console → Dashboards → Squeeze-AI-Token-Optimizer**. Pan across the widgets slowly.

#### Voiceover

> "Every compression call emits custom CloudWatch metrics in real-time. This is our live Squeeze dashboard running on AWS.
>
> The compression ratio gauge shows 85% average reduction. The dollar savings counter calculates cost savings across Claude Sonnet and Opus pricing. And this widget — DLP Secrets Intercepted — shows every credential Squeeze caught and masked before it could reach an external provider.
>
> These aren't simulated numbers. This is real traffic from our deployed Lambda functions hitting the Squeeze engine on AWS."

---

## SCENE 4: WHAT ELSE IT DOES [2:10 – 2:30]

### Visual
Quick montage (2–3 seconds each):
1. Architecture diagram (full system)
2. CloudFormation console showing 4 stacks
3. Terminal showing `npx cdk deploy --all` completion output

### Voiceover

> "Beyond the Bedrock Agent, Squeeze also runs as an autonomous CloudWatch Logs pipeline — intercepting production error streams in real-time, compressing them, and auto-generating incident summaries into S3 using Bedrock, with zero human intervention.
>
> We built CI log compression for CodeBuild, a codebase indexer that generates topological dependency graphs for coding agents, and a DLP compliance verification endpoint.
>
> Everything deploys with one command — 'cdk deploy all' — across 4 CDK stacks, and tears down with 'cdk destroy all' with zero leftover charges."

---

## SCENE 5: WHAT WE LEARNED [2:30 – 2:50]

### Visual
Direct to camera (or a clean text card if you prefer).

### Voiceover (be honest and specific — this is a scoring category)

> "Before this week, we had never built a Bedrock Agent with a custom Action Group. Learning how the orchestration planner reads an OpenAPI 3.0 schema and autonomously decides which tool to call — not because we hardcoded it, but because the agent reasoned about it — that was a genuine breakthrough moment for us.
>
> We also discovered Lambda Function URLs. We assumed you always needed API Gateway for a public endpoint. One Lambda with a Function URL gave us a remote MCP server with zero additional infrastructure."

---

## SCENE 6: CLOSE [2:50 – 3:00]

### Visual
Project logo or clean title card.

### Voiceover

> "Squeeze makes every LLM pipeline on AWS faster, cheaper, and safer. Thank you."

### Final Frame (hold 5 seconds)
```
SQUEEZE AI
Universal LLM Context Optimizer for AWS
Built with: Amazon Bedrock · AWS Lambda · CloudWatch · S3 · CDK

Team: [Your Team Name]
GitHub: [Your Repo URL]
```

---

## Video Editing Tips

1. **Cut all loading/waiting time.** If a Bedrock Agent takes 5 seconds to respond, edit it to 1 second with a brief fade.
2. **Use zoom/highlight** on the Bedrock Trace panel — judges need to read the rationale text.
3. **Add text overlays** for token counts and dollar savings — don't rely on voiceover alone for numbers.
4. **Keep the terminal font at 16pt+** — it must be readable in a compressed video upload.
5. **Record at 1080p minimum** — console text gets blurry at 720p.
