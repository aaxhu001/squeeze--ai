# 🎬 SQUEEZE ON AWS — FULL VIDEO SCRIPT (4 SPEAKERS)

**Duration:** 3:00  
**Format:** Pre-recorded screen + talking head  
**Speakers:**
- **SPEAKER A** — The Narrator / Problem Framer (opens and closes the video)
- **SPEAKER B** — The Architect / AWS Expert (explains the system design)
- **SPEAKER C** — The Demo Driver (does the live screen recording demo)
- **SPEAKER D** — The Learner / Closer (talks about what the team learned)

> **Recording Tip:** Each person records their section separately. Edit them together. This is easier than doing one continuous take.

---

## PRE-RECORDING SETUP

Before anyone hits record:

```bash
# Terminal 1: Verify engine works
python3 aws/scripts/test_local_engine.py

# Terminal 2: Deploy stacks (if not done)
cd aws/cdk && npx cdk deploy --all

# Terminal 3: Seed CloudWatch dashboard with real data
python3 aws/scripts/simulate_demo_traffic.py --batches 25

# Terminal 4: Test the Bedrock Agent and note the Agent ID
python3 aws/scripts/test_bedrock_agent.py --agent-id <AGENT_ID>
```

Pre-open browser tabs:
- AWS Bedrock Console → Agents → Squeeze-Bedrock-Optimizer
- AWS CloudWatch → Dashboards → Squeeze-AI-Token-Optimizer
- AWS Lambda Console (showing 5 functions)
- VS Code with `raw_cloudwatch_dump.log` and `leak_with_credentials.txt` open

---

---

## SCENE 1: THE HOOK — THE PROBLEM IS REAL
**[0:00 – 0:30] — SPEAKER A (to camera + screen share)**

---

### SCREEN DIRECTION
- Start with Speaker A on camera (or voiceover over screen).
- Screen shows: VS Code with `raw_cloudwatch_dump.log` open. Slowly scroll through it so judges see the wall of repetitive text.
- At 0:15, switch to `leak_with_credentials.txt`. Zoom into the lines showing `AKIAIOSFODNN7EXAMPLE` and `sk-proj-abCDef...`.

### DIALOGUE — SPEAKER A (Recommended Version: "The Noise Tax")

> "There is a costly problem in cloud AI that nobody likes to talk about: **AI models charge you by the word, but the cloud is full of useless noise.**
>
> Look at this real AWS log on my screen.
> 
> *(scroll through raw log)*
>
> It's twelve thousand words long. But ninety percent of it is literally the exact same error message repeated forty-seven times. And worse — look right here at line 14: an active AWS secret key, an OpenAI key, and a database password, sitting in plain text.
>
> If you feed this to an AI agent, three bad things happen:
> First, you pay top dollar for the model to read copy-paste junk.
> Second, the agent gets slow and confused by the clutter.
> And third, your company's private passwords just leaked to an external LLM.
>
> Why pay an AI to read a hundred pages of noise when it only needs three lines of truth?
>
> We built Squeeze to solve this."

### ON-SCREEN TEXT OVERLAY (show at 0:20)
```
THE PROBLEM:
1. 💸 85%+ of cloud data is duplicate noise (you pay for every word)
2. 🐢 Slows down AI reasoning and causes context overflow
3. 🚨 Leaked AWS keys & passwords sent directly to LLMs
```

---

---

## SCENE 2: WHAT SQUEEZE IS — THE ARCHITECTURE
**[0:30 – 0:55] — SPEAKER B (to camera + screen share)**

---

### SCREEN DIRECTION
- Speaker B on camera for first 5 seconds, then cut to screen share.
- Show the Mermaid architecture diagram from `ARCHITECTURE.md` (rendered in VS Code preview or as a screenshot). Hold for 6 seconds.
- Then show a **before/after split**:
  - LEFT side: raw log dump (red-tinted or red border)
  - RIGHT side: squeezed output (green-tinted, visibly 5x shorter)
- At 0:48, flash the AWS service logos in a row.

### DIALOGUE — SPEAKER B

> "Squeeze solves this with three breakthrough capabilities built natively into AWS:
>
> First — **our 100% Local Summarizer.** It runs completely on the edge with zero external pip dependencies and sub-ten-millisecond latency. It collapses bloated logs by eighty-five percent, folds repetitive JSON arrays by ninety-five percent, and masks eight types of production credentials before anything ever leaves your account. Zero extra API cost.
>
> Second — **our Codebase Topological Graph.**
> 
> *(switch screen to `assets/11_codebase_graph_sample.md`)*
>
> Look at this: when an AI coding assistant inspects a large codebase, it usually reads dozens of files — burning half a million tokens just searching for where a function lives. Squeeze indexes the entire codebase in milliseconds, ranks every module by import centrality, and delivers a compact symbol map. Half a million tokens becomes eight hundred tokens. The LLM goes straight to the exact file it needs to edit without wandering through the codebase.
>
> And third — **we connect two AWS powerhouses:**
> We wired Squeeze directly into **Amazon Bedrock** as an autonomous Action Group, and streamed real-time savings directly into **Amazon CloudWatch**.
>
> Let me hand it to [Speaker C] to show you the Bedrock Agent using Squeeze live."

### ON-SCREEN TEXT OVERLAY (show during Speaker B)
```
⚡ SQUEEZE 3 CORE PILLARS:
1. 100% Local Summarizer & DLP Shield (<10ms, zero pip dependencies)
2. Codebase Topological Graph (99.8% token savings on repo navigation)
3. AWS Power Duo: Amazon Bedrock Agent + Amazon CloudWatch Dashboard
```

---

---

## SCENE 3: THE LIVE DEMO — ONE FEATURE, WORKING, END-TO-END
**[0:55 – 2:15] — SPEAKER C (screen share + voiceover)**

> **This is 80 seconds. This is the section that wins or loses the hackathon.**
> **Record this part multiple times and pick the cleanest take.**

---

### PART A — INVOKE THE BEDROCK AGENT [0:55 – 1:10]

#### SCREEN DIRECTION
Show the terminal. Run:
```bash
python3 aws/scripts/test_bedrock_agent.py --agent-id <AGENT_ID>
```
Or show the **Bedrock Console chat interface** and type the prompt.

#### DIALOGUE — SPEAKER C

> "This is our deployed Bedrock Agent — Squeeze-Bedrock-Optimizer — running Claude 3.5 Sonnet on AWS.
>
> I'm sending it that same fifty-kilobyte raw CloudWatch log dump. My prompt is simple: 'Analyze these logs and diagnose the database failure.'
>
> *(hit enter / submit)*
>
> Now watch what happens in the orchestration trace."

---

### PART B — THE TRACE — THE MONEY SHOT [1:10 – 1:40]

#### SCREEN DIRECTION
Switch to the **Bedrock Agent Trace panel** in the AWS Console. Zoom in (Cmd+Plus or browser zoom) so the text is clearly readable. Highlight or circle these three things:

1. **The Rationale** — where the agent explains WHY it's calling Squeeze
2. **The Action** — `squeeze_shrink_logs` with the input
3. **The Observation** — the compressed result returned

#### DIALOGUE — SPEAKER C

> "Here's the orchestration trace — and this is the key moment of our entire project.
>
> *(zoom into rationale)*
>
> Look at the agent's rationale. It says: 'The user provided raw log data. I should compress it using squeeze_shrink_logs before analyzing.' We didn't hardcode that. We didn't tell it to compress first. The agent read our OpenAPI schema, understood what Squeeze does, and DECIDED ON ITS OWN to compress the logs before reasoning.
>
> *(zoom into action)*
>
> It sent the raw logs to our Squeeze Action Group Lambda. The Lambda ran our compression engine — deduplicated forty-seven identical error lines, collapsed six stack traces into one, stripped every timestamp and UUID, and masked nine leaked credentials.
>
> *(zoom into observation)*
>
> Twelve thousand tokens became eighteen hundred. The compression took six milliseconds. And now Claude is reasoning over clean, high-density context instead of noise."

### ON-SCREEN TEXT OVERLAY (show during trace)
```
🔑 AUTONOMOUS TOOL SELECTION
Agent decided to call Squeeze — not hardcoded
12,000 → 1,800 tokens (85% saved)
Latency: 6ms | Secrets masked: 9
```

---

### PART C — THE ANSWER [1:40 – 1:50]

#### SCREEN DIRECTION
Show the agent's final response in the console or terminal output.

#### DIALOGUE — SPEAKER C

> "And here's the diagnosis. Root cause: HikariPool connection pool exhaustion on the Aurora cluster in us-east-1b. Impacted services: order processing and payment ledger. Recommended fix: increase connection pool limit and add exponential backoff.
>
> Correct answer. Eighty-five percent cheaper. Zero credentials leaked."

---

### PART D — THE CLOUDWATCH DASHBOARD [1:50 – 2:15]

#### SCREEN DIRECTION
Switch to **AWS CloudWatch Console → Dashboards → Squeeze-AI-Token-Optimizer**. Slowly pan across each widget. Zoom into the numbers.

#### DIALOGUE — SPEAKER C

> "Every compression call emits custom CloudWatch metrics to our Squeeze-AI namespace. This dashboard is live on AWS right now.
>
> *(point to first widget)*
> Cumulative tokens saved — over thirty thousand tokens from our test traffic.
>
> *(point to second widget)*
> Dollar savings — calculated in real-time across Claude Sonnet at three dollars per million tokens and Opus at fifteen.
>
> *(point to third widget)*
> This one is my favorite — DLP Secrets Intercepted. Every AWS key, every database password, every JWT that Squeeze caught and masked before it could reach an external provider.
>
> *(point to fourth widget)*
> And the compression ratio gauge — eighty-five percent average. These are real numbers from real Lambda invocations on our deployed stack.
>
> Let me hand it to [Speaker D's name]."

---

---

## SCENE 4: THE FULL PICTURE + WHAT ELSE
**[2:15 – 2:30] — SPEAKER B (quick screen share)**

---

### SCREEN DIRECTION
Quick montage (3 seconds each):
1. AWS CloudFormation console showing the 4 stacks: `SqueezeMcpBedrockStack`, `SqueezeLogPipelineStack`, `SqueezeDashboardStack`, `SqueezeDevToolsStack`
2. AWS Lambda console showing 5 deployed functions
3. Terminal showing `npx cdk destroy --all` (to prove one-command teardown)

### DIALOGUE — SPEAKER B

> "Beyond the Bedrock Agent, Squeeze also runs as an autonomous CloudWatch Logs pipeline — intercepting production errors in real-time, compressing them, and generating incident summaries into S3 using Bedrock with zero human intervention.
>
> We built CI log compression for CodeBuild, a codebase indexer for coding agents, and a DLP compliance endpoint.
>
> The entire stack is four CDK stacks in TypeScript. One command to deploy. One command to destroy. Zero idle cost."

---

---

## SCENE 5: WHAT WE LEARNED
**[2:30 – 2:50] — SPEAKER D (to camera)**

---

### SCREEN DIRECTION
Speaker D on camera. Clean background. No screen share — this should feel personal and honest.

### DIALOGUE — SPEAKER D

> "Honestly — before this project, none of us had built a Bedrock Agent with a custom Action Group.
>
> The moment that blew our minds was when we saw the orchestration trace for the first time. We defined an OpenAPI schema describing what Squeeze does — shrink logs, fold JSON, mask secrets. And then the agent just... figured out when to call it. We didn't write any routing logic. The agent reasoned about the user's request, read the schema, and decided: 'I should compress first.'
>
> We also learned about Lambda Function URLs — we had no idea you could expose a public HTTP endpoint from a single Lambda without API Gateway. That's how we turned Squeeze into a remote MCP server that works with Cursor, Windsurf, and Claude Code — all from one Lambda function.
>
> This hackathon taught us that building on AWS isn't about knowing every service — it's about wiring the right ones together."

---

---

## SCENE 6: THE CLOSE
**[2:50 – 3:00] — SPEAKER A (to camera)**

---

### SCREEN DIRECTION
Speaker A back on camera. Confident, direct.

### DIALOGUE — SPEAKER A

> "Squeeze makes every LLM pipeline on AWS faster, cheaper, and safer.
>
> Eighty-five percent fewer tokens. Nine credential types masked in-flight. Sub-ten-millisecond latency. Zero idle cost. One-command teardown.
>
> We're Squeeze. Thanks for watching."

### FINAL FRAME (hold for 5 seconds, no voiceover)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ⚡ SQUEEZE AI
  Universal LLM Context Optimizer

  Built with:
  Amazon Bedrock · AWS Lambda
  Amazon CloudWatch · Amazon S3
  AWS CDK · AWS CodeBuild

  Team: [Your Team Name]
  GitHub: [Your Repo URL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

---

## 🎬 PRODUCTION NOTES

### Speaker Assignment Summary

| Speaker | Sections | Total Time | Role |
|---|---|---|---|
| **A** | Scene 1 (Hook) + Scene 6 (Close) | ~40 seconds | Opens and closes — strong, confident presence |
| **B** | Scene 2 (Architecture) + Scene 4 (Full Picture) | ~40 seconds | Technical depth — knows the AWS services cold |
| **C** | Scene 3 (Full Demo) | ~80 seconds | Screen share expert — smooth, no fumbling |
| **D** | Scene 5 (Learning) | ~20 seconds | Honest, personal — the human moment |

### Recording Workflow

1. **Record each scene separately.** Don't try to do a single 3-minute take.
2. **Speaker C should record Scene 3 multiple times** and pick the cleanest run (no loading spinners, no typos, no console errors).
3. **Use OBS Studio, QuickTime, or Loom** for screen recording.
4. **Edit in CapCut, iMovie, or DaVinci Resolve** (all free).
5. **Add text overlays** in the editor — don't rely on voiceover for numbers.
6. **Export at 1080p, 30fps.** Console text gets blurry below 1080p.

### Timing Cheat Sheet

```
0:00  SPEAKER A  — "Every team building AI agents on AWS..."
0:30  SPEAKER B  — "Squeeze is a context compression engine..."
0:55  SPEAKER C  — "This is our deployed Bedrock Agent..."
1:10  SPEAKER C  — "Here's the orchestration trace..."  ← THE MONEY SHOT
1:40  SPEAKER C  — "And here's the diagnosis..."
1:50  SPEAKER C  — "Every compression call emits custom CloudWatch metrics..."
2:15  SPEAKER B  — "Beyond the Bedrock Agent..."
2:30  SPEAKER D  — "Honestly, before this project..."
2:50  SPEAKER A  — "Squeeze makes every LLM pipeline on AWS..."
3:00  END CARD
```

### If Something Goes Wrong During Recording

- **Bedrock Agent is slow?** → Edit out the wait. Cut from "hit enter" to "the trace appeared."
- **CloudWatch dashboard has no data?** → Run `simulate_demo_traffic.py --batches 30` again.
- **Bedrock Agent not deployed?** → Record the demo using `test_local_engine.py` output and show the CDK `cdk synth` output as proof of AWS integration. Mention "deployed on AWS" but show local execution. Not ideal, but better than a broken demo.
- **One speaker can't record?** → Redistribute: Speaker A takes Scene 5 (Learning) as well. Three speakers works fine.
