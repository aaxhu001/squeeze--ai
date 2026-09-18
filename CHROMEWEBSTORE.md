# Chrome Web Store Listing — Squeeze AI

**Last Updated:** September 19, 2026  
**Extension Name:** Squeeze AI - Prompt & Context Optimizer  
**Current Version:** 1.0.0  

---

## 1. Store Metadata

- **Name:** Squeeze AI - Prompt & Context Optimizer
- **Short Description (max 132 characters):**  
  Cut AI token bloat by up to 70%, mask sensitive credentials, and manage prompt context across Claude, ChatGPT, and Gemini.
- **Category:** Developer Tools / Productivity
- **Primary Language:** English

---

## 2. Detailed Store Description

Squeeze AI optimizes your chatbot prompts and documents in real time, cutting token bloat by up to 70%, preventing context limit exhaustion, and safeguarding sensitive credentials across Claude.ai, ChatGPT, and Google Gemini.

### Key Features:

⚡ **Instant Token Squeezer**  
Compress wordy prompts, polite conversational filler, redundant instructions, and duplicate paragraphs before sending them to LLMs. Reduce input token count and cut response latency instantly.

🛡️ **DLP Secret & Credential Shield**  
Prevent accidental leaks of production secrets. Squeeze automatically detects and masks API keys (OpenAI, Anthropic, Google AI, AWS), JWT bearer tokens, and database passwords directly in your browser before they can be submitted to AI platforms.

🖥️ **Persistent Side Panel (Squeeze Studio)**  
Open Squeeze alongside any webpage. Test prompts in a side-by-side visual diff editor, compare dollar savings across Claude 3.5 Sonnet, GPT-4o, and Gemini 1.5 Pro, and explore proven prompt engineering templates (CO-STAR, Few-Shot, Code Refactoring).

📄 **PDF Token Compactor**  
Extract and compress content from PDFs with one click. Automatically prunes repetitive headers, footers, page numbering, and whitespace so you can feed documents to AI models without blowing your token budget.

🗄️ **Smart Context Vault**  
Store your developer guidelines, style specs, and reference files locally. Squeeze intelligently attaches only relevant context snippets when matching keywords are detected in your prompt.

🌐 **Universal Multi-Platform Support**  
Works seamlessly inside the native chat inputs of Claude.ai, ChatGPT (chatgpt.com), and Google Gemini (gemini.google.com). Use the intuitive keyboard shortcut (Ctrl+Shift+S / Cmd+Shift+S) to squeeze any prompt in place.

🔒 **100% Private & Local**  
All heuristic compression and secret masking execute on-device inside your browser. Your prompts and credentials are never transmitted to external servers.

---

## 3. Permissions Justification

| Permission / Host | Why It Is Needed |
| :--- | :--- |
| `storage` | Required to save user preferences, custom compression modes, active rules, Context Vault files, and cumulative token savings locally on the user's device. |
| `sidePanel` | Required to provide the persistent Squeeze Studio side panel interface alongside any browser tab. |
| `tabs` | Required so the user can insert optimized prompts from the Side Panel directly into their active AI chat tab with one click. |
| `https://claude.ai/*` | Allows Squeeze to mount the prompt optimization button, token usage gauge, and context summarizer directly inside the Claude.ai chat interface. |
| `https://chatgpt.com/*` | Allows Squeeze to mount the prompt optimization button, secret shield, and text injector directly inside the ChatGPT web interface. |
| `https://chat.openai.com/*` | Legacy domain support for ChatGPT chat sessions. |
| `https://gemini.google.com/*` | Allows Squeeze to mount the prompt optimization button and text injector directly inside Google Gemini. |
| `http://localhost/*` | Optional user-configured local Context Vault endpoints (such as local documentation or MCP servers). |

---

## 4. Privacy & Data Use Disclosure

- **Does this extension collect user data?**  
  No. All text parsing, heuristic compression, token estimation, and credential redaction occur entirely on-device within the user's local browser runtime.
- **Does this extension transmit prompts or code to external servers?**  
  No. No prompts, source code, files, or telemetry are transmitted to any remote servers.
- **Single-Purpose Compliance:**  
  The single purpose of Squeeze AI is to optimize AI chatbot prompts for token efficiency and privacy directly within the browser.

---

## 5. Version History

- **v1.0.0 (Hackathon Production Release):**
  - Added Chrome MV3 Side Panel ("Squeeze Studio") with live token diff playground and multi-model cost analytics.
  - Expanded universal platform support to include ChatGPT (`chatgpt.com`) and Google Gemini (`gemini.google.com`).
  - Added real-time DLP Secret Shield for automated masking of API keys, JWTs, and database credentials.
  - Added interactive prompt engineering frameworks (CO-STAR, Few-Shot, Code Refactoring).
  - Added 1-click Judge Demo showcase presets.
  - Performance improvements to token estimation and duplicate sentence pruning.
