# 🎯 5-MINUTE PRE-RECORDING CHEAT SHEET (FOR ALL 4 TEAMMATES)

Keep this file open on a second monitor or phone while recording!

---

## 👥 Speaker Roles & Exact Files to Open

### 1️⃣ SPEAKER A: The Hook & The Problem [0:00 – 0:30]
- **What to open:**
  1. Open [`assets/01_raw_cloudwatch_dump.log`](01_raw_cloudwatch_dump.log) in VS Code.
     * **Action:** Scroll through the long repetitive lines slowly (show the wall of text).
  2. Switch to [`assets/02_leak_with_credentials.txt`](02_leak_with_credentials.txt).
     * **Action:** Highlight line 14 (`AKIAIOSFODNN7EXAMPLE`) and line 16 (`sk-proj-...`).
- **Key Line to Say:** *"Why pay an AI to read a hundred pages of noise when it only needs three lines of truth?"*

---

### 2️⃣ SPEAKER B: The 3 Core Pillars & Architecture [0:30 – 0:55]
- **What to open:**
  1. Double-click [`assets/10_architecture_visual.html`](10_architecture_visual.html) in Chrome (highlights the **100% Local Summarizer** + **Bedrock & CloudWatch**).
  2. Switch to [`assets/11_codebase_graph_sample.md`](11_codebase_graph_sample.md):
     * **Show:** The Topological Graph showing **462,929 raw tokens → 875 graph tokens (99.8% compression)**!
     * **Explain:** AI coding agents don't have to wander through 50 files; they jump straight to the central module!
  3. Show split-screen:
     * **LEFT:** [`assets/06_bloated_kinesis_records.json`](06_bloated_kinesis_records.json) (21KB)
     * **RIGHT:** [`assets/07_squeezed_json_output.json`](07_squeezed_json_output.json) (999 Bytes, 95% saved 100% locally!)
- **Key Line to Say:** *"Squeeze brings a 100% local summarizer, a codebase topological graph, and connects Amazon Bedrock with CloudWatch."*

---

### 3️⃣ SPEAKER C: The Live Bedrock Agent Demo [0:55 – 2:15]
- **What to open & do:**
  1. Open AWS Console → **Amazon Bedrock > Agents** (or terminal with `python3 aws/scripts/test_bedrock_agent.py --agent-id <ID>`).
  2. Copy the prompt from [`assets/08_bedrock_agent_copy_paste_prompt.txt`](08_bedrock_agent_copy_paste_prompt.txt) and paste it into the agent chat.
  3. **THE MONEY SHOT:** Click on the **Bedrock Orchestration Trace**:
     * Point to **Rationale**: *"I should compress it using squeeze_shrink_logs before analyzing."*
     * Point to **Action**: `squeeze_shrink_logs`
     * Point to **Observation**: 12,000 → 1,800 tokens in 6ms!
     * *(Backup reference if live Bedrock is slow: [`assets/09_bedrock_agent_trace_and_response.txt`](09_bedrock_agent_trace_and_response.txt))*
  4. Switch to AWS Console → **CloudWatch Dashboards > `Squeeze-AI-Token-Optimizer`**:
     * Point to: Compression Ratio (85%), Dollar Savings ($), and DLP Secrets Masked.
- **Key Line to Say:** *"We didn't hardcode that. The agent decided on its own to call Squeeze before reasoning."*

---

### 4️⃣ SPEAKER B: The Cloud Infrastructure Montage [2:15 – 2:30]
- **What to show (3-second quick cuts):**
  1. AWS CloudFormation console showing the 4 stacks (`SqueezeMcpBedrockStack`, etc.).
  2. AWS Lambda console showing the 5 deployed functions.
  3. Terminal showing `npx cdk synth` or `destroy_all.sh`.
- **Key Line to Say:** *"Four CDK stacks in TypeScript. One command to deploy, one command to destroy. Zero idle cost."*

---

### 5️⃣ SPEAKER D: What We Learned [2:30 – 2:50]
- **What to show:**
  * Direct to camera (clean, honest face-to-camera).
- **Key Line to Say:** *"Learning how the agent reasoned about an OpenAPI schema and decided to compress on its own was our biggest 'aha' moment."*

---

### 6️⃣ SPEAKER A: The Punchline & Close [2:50 – 3:00]
- **What to show:**
  * Speaker A on camera → Cut to final title card.
- **Key Line to Say:** *"Squeeze makes every LLM pipeline on AWS faster, cheaper, and safer. We're Squeeze. Thanks for watching."*

---

## 📂 Asset Files Quick Index

| File in `assets/` | Used In | Purpose |
|---|---|---|
| [`00_RECORDING_CHEAT_SHEET.md`](00_RECORDING_CHEAT_SHEET.md) | All | This cheatsheet |
| [`01_raw_cloudwatch_dump.log`](01_raw_cloudwatch_dump.log) | Scene 1, 2, 3 | Huge raw ugly logs to scroll through |
| [`02_leak_with_credentials.txt`](02_leak_with_credentials.txt) | Scene 1 | Plaintext AWS & OpenAI keys to zoom into |
| [`03_squeezed_log_output.log`](03_squeezed_log_output.log) | Scene 2 | Pre-squeezed logs for before/after split |
| [`04_big_code_chunk_500lines.py`](04_big_code_chunk_500lines.py) | Scene 2 | Big 250+ line Python code for AST demo |
| [`05_squeezed_code_skeleton.py`](05_squeezed_code_skeleton.py) | Scene 2 | Pre-extracted code skeleton (60% saved) |
| [`06_bloated_kinesis_records.json`](06_bloated_kinesis_records.json) | Scene 2 | 21KB ugly JSON records |
| [`07_squeezed_json_output.json`](07_squeezed_json_output.json) | Scene 2 | Shrunk JSON payload (95.4% saved) |
| [`08_bedrock_agent_copy_paste_prompt.txt`](08_bedrock_agent_copy_paste_prompt.txt) | Scene 3 | 1-click prompt to paste into Bedrock Agent |
| [`09_bedrock_agent_trace_and_response.txt`](09_bedrock_agent_trace_and_response.txt) | Scene 3 | Exact trace & answer reference / backup |
| [`10_architecture_visual.html`](10_architecture_visual.html) | Scene 2 | Sleek HTML architecture card graphic |
