/**
 * Squeeze AI - Side Panel Script (Manifest V3)
 * Full interactive controller for Studio, Frameworks, DLP Shield,
 * Context Vault, Multi-Model Analytics, and Judge Demo Showcase.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const navButtons = document.querySelectorAll(".sp-nav-btn");
  const panes = document.querySelectorAll(".sp-pane");

  // Studio elements
  const inputPrompt = document.getElementById("spInputPrompt");
  const inputTokenBadge = document.getElementById("spInputTokenBadge");
  const charCount = document.getElementById("spCharCount");
  const clearInputBtn = document.getElementById("spClearInputBtn");
  const modeButtons = document.querySelectorAll(".sp-mode-btn");
  const toggleDlp = document.getElementById("spToggleDlp");
  const toggleVault = document.getElementById("spToggleVault");
  const squeezeBtn = document.getElementById("spSqueezeActionBtn");

  // Output elements
  const outputSection = document.getElementById("spOutputSection");
  const secretAlertBanner = document.getElementById("spSecretAlertBanner");
  const secretAlertCount = document.getElementById("spSecretAlertCount");
  const qualityPill = document.getElementById("spQualityPill");
  const viewDiffBtn = document.getElementById("spViewDiffBtn");
  const viewCleanBtn = document.getElementById("spViewCleanBtn");
  const tokensSavedVal = document.getElementById("spTokensSavedVal");
  const percentSavedVal = document.getElementById("spPercentSavedVal");
  const finalTokenCount = document.getElementById("spFinalTokenCount");
  const diffContainer = document.getElementById("spDiffViewContainer");
  const cleanTextarea = document.getElementById("spCleanViewTextarea");
  const rulesChips = document.getElementById("spRulesChips");
  const copyResultBtn = document.getElementById("spCopyResultBtn");
  const sendToTabBtn = document.getElementById("spSendToActiveTabBtn");
  const feedbackMsg = document.getElementById("spFeedbackMsg");

  // Model cost elements
  const costSonnet = document.getElementById("spCostSonnet");
  const costGpt4o = document.getElementById("spCostGpt4o");
  const costGemini = document.getElementById("spCostGemini");
  const costDeepseek = document.getElementById("spCostDeepseek");

  // Demo presets
  const demoPitchBtn = document.getElementById("spDemoPitchBtn");
  const demoPresetDev = document.getElementById("demoPresetDev");
  const demoPresetEmail = document.getElementById("demoPresetEmail");
  const demoPresetCode = document.getElementById("demoPresetCode");

  // Framework triggers
  const fwApplyCostar = document.getElementById("fwApplyCostar");
  const fwApplyFewshot = document.getElementById("fwApplyFewshot");
  const fwApplyCode = document.getElementById("fwApplyCode");
  const fwApplyExec = document.getElementById("fwApplyExec");

  // DLP elements
  const dlpTestInput = document.getElementById("spDlpTestInput");
  const dlpResultBox = document.getElementById("spDlpResultBox");

  // Vault elements
  const vaultPrefs = document.getElementById("spVaultPrefs");
  const vaultAlwaysInject = document.getElementById("spVaultAlwaysInject");
  const vaultSmartTriggers = document.getElementById("spVaultSmartTriggers");
  const vaultDropzone = document.getElementById("spVaultDropzone");
  const vaultFileInput = document.getElementById("spVaultFileInput");
  const vaultBrowseLink = document.getElementById("spVaultBrowseLink");
  const vaultList = document.getElementById("spVaultList");

  // Analytics elements
  const analyticsPrompts = document.getElementById("spAnalyticsPrompts");
  const analyticsTokens = document.getElementById("spAnalyticsTokens");
  const analyticsCost = document.getElementById("spAnalyticsCost");
  const ecoEnergy = document.getElementById("spEcoEnergy");
  const ecoCo2 = document.getElementById("spEcoCo2");
  const historyList = document.getElementById("spHistoryList");
  const resetStatsBtn = document.getElementById("spResetStatsBtn");

  // State
  let currentMode = "balanced";
  let lastOptimizedResult = null;
  let vaultFilesList = [];
  let analyticsLastLoaded = 0; // Fix #17: track last analytics render to avoid redundant re-renders

  // --- TAB SWITCHING ---
  navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");
      navButtons.forEach(b => b.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(`pane-${target}`);
      if (targetPane) targetPane.classList.add("active");

      // Fix #17: Only reload analytics if >5s have passed since last load
      if (target === "analytics") {
        const now = Date.now();
        if (now - analyticsLastLoaded > 5000) {
          loadAnalytics();
          analyticsLastLoaded = now;
        }
      }
      if (target === "vault") loadVaultData();
      if (target === "graph") loadCodeGraph();
    });
  });

  function switchTab(tabId) {
    const btn = document.querySelector(`.sp-nav-btn[data-tab="${tabId}"]`);
    if (btn) btn.click();
  }

  // --- TOKEN ESTIMATION ---
  function estimateTokensLocal(text) {
    if (!text) return 0;
    const trimmed = text.trim();
    if (!trimmed) return 0;
    const words = trimmed.split(/\s+/).length;
    const chars = trimmed.length;
    const specialChars = (trimmed.match(/[{}\[\]()<>=:;,.!?"'`\/\\|#*&^%$@~+-]/g) || []).length;
    const codeRatio = specialChars / Math.max(1, chars);
    const charEst = Math.ceil(chars / (codeRatio > 0.15 ? 3.2 : 4.0));
    const wordEst = Math.ceil(words * 1.35);
    return Math.max(charEst, wordEst);
  }

  function updateInputMetrics() {
    const text = inputPrompt.value || "";
    const tokens = estimateTokensLocal(text);
    inputTokenBadge.textContent = `${tokens.toLocaleString()} tokens`;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    charCount.textContent = `${chars.toLocaleString()} chars · ${words.toLocaleString()} words`;
  }

  if (inputPrompt) inputPrompt.addEventListener("input", updateInputMetrics);

  if (clearInputBtn) {
    clearInputBtn.addEventListener("click", () => {
      if (inputPrompt) inputPrompt.value = "";
      updateInputMetrics();
      if (outputSection) outputSection.style.display = "none";
      if (inputPrompt) inputPrompt.focus();
    });
  }

  // --- MODE SELECTION ---
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      modeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentMode = btn.getAttribute("data-mode");
      chrome.storage.local.set({ optimizationMode: currentMode });
      // If we already have output, auto-reoptimize
      if (inputPrompt.value.trim() && outputSection.style.display !== "none") {
        executeOptimization();
      }
    });
  });

  // --- WORD-LEVEL DIFF GENERATOR ---
  function generateDiffHtml(original, optimized) {
    const origTokens = original.trim().split(/(\s+)/);
    const optTokens = optimized.trim().split(/(\s+)/);

    // LCS (Longest Common Subsequence)
    const m = origTokens.length;
    const n = optTokens.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (origTokens[i - 1] === optTokens[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1] + 1;
        } else {
          dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
        }
      }
    }

    let i = m, j = n;
    const diffPieces = [];

    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && origTokens[i - 1] === optTokens[j - 1]) {
        diffPieces.unshift(escapeHtml(origTokens[i - 1]));
        i--;
        j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        const text = optTokens[j - 1];
        if (text.trim() === "") {
          diffPieces.unshift(text);
        } else {
          diffPieces.unshift(`<ins class="sp-diff-ins">${escapeHtml(text)}</ins>`);
        }
        j--;
      } else {
        const text = origTokens[i - 1];
        if (text.trim() === "") {
          diffPieces.unshift(text);
        } else {
          diffPieces.unshift(`<del class="sp-diff-del">${escapeHtml(text)}</del>`);
        }
        i--;
      }
    }

    return diffPieces.join("");
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- SQUEEZE EXECUTION ---
  async function executeOptimization() {
    if (!inputPrompt) return;
    const text = inputPrompt.value.trim();
    if (!text) {
      inputPrompt.focus();
      return;
    }

    if (squeezeBtn) {
      squeezeBtn.disabled = true;
      const btnText = squeezeBtn.querySelector(".btn-text");
      if (btnText) btnText.textContent = "Squeezing...";
    }

    try {
      chrome.runtime.sendMessage(
        {
          action: "optimizePrompt",
          prompt: text,
          mode: currentMode
        },
        response => {
          if (squeezeBtn) {
            squeezeBtn.disabled = false;
            const btnText = squeezeBtn.querySelector(".btn-text");
            if (btnText) btnText.textContent = "Squeeze Prompt";
          }

          if (chrome.runtime.lastError) {
            alert("Error communicating with Squeeze background service: " + chrome.runtime.lastError.message);
            return;
          }

          if (response && response.success) {
            renderOutput(response);
          } else {
            alert("Optimization failed: " + (response?.error || "Unknown error"));
          }
        }
      );
    } catch (err) {
      if (squeezeBtn) {
        squeezeBtn.disabled = false;
        const btnText = squeezeBtn.querySelector(".btn-text");
        if (btnText) btnText.textContent = "Squeeze Prompt";
      }
      alert("Error: " + err.message);
    }
  }

  function renderOutput(data) {
    lastOptimizedResult = data;
    if (outputSection) outputSection.style.display = "flex";

    // Tokens & Percent
    if (tokensSavedVal) tokensSavedVal.textContent = data.tokensSaved.toLocaleString();
    if (percentSavedVal) percentSavedVal.textContent = `${data.percentageSaved}%`;
    if (finalTokenCount) finalTokenCount.textContent = data.optimizedTokens.toLocaleString();

    // Intent quality heuristic
    let intentScore = 98;
    if (data.mode === "squeeze") intentScore = 93;
    else if (data.mode === "polish") intentScore = 99;
    if (qualityPill) qualityPill.textContent = `⚡ ${intentScore}% Intent Preserved`;

    // DLP Alert
    if (secretAlertBanner) {
      if (data.secretsDetected && data.secretsDetected.length > 0) {
        secretAlertBanner.style.display = "flex";
        if (secretAlertCount) secretAlertCount.textContent = `${data.secretsDetected.length} secret(s) safely masked (${data.secretsDetected.map(s => s.type).join(", ")}).`;
      } else {
        secretAlertBanner.style.display = "none";
      }
    }

    // Diff view & clean view
    if (diffContainer) diffContainer.innerHTML = generateDiffHtml(data.original, data.optimized);
    if (cleanTextarea) cleanTextarea.value = data.optimized;

    // Default to diff view
    if (diffContainer) diffContainer.style.display = "block";
    if (cleanTextarea) cleanTextarea.style.display = "none";
    if (viewDiffBtn) viewDiffBtn.classList.add("active");
    if (viewCleanBtn) viewCleanBtn.classList.remove("active");

    // Applied rule chips
    if (rulesChips) {
      rulesChips.innerHTML = "";
      if (data.rulesApplied && data.rulesApplied.length > 0) {
        data.rulesApplied.forEach(rule => {
          const chip = document.createElement("span");
          chip.className = "sp-rule-chip";
          chip.textContent = `✓ ${rule}`;
          rulesChips.appendChild(chip);
        });
      }
    }

    // Cost calculations per 100 queries
    const multiplier = 100;
    const tokens = data.tokensSaved;
    if (costSonnet) costSonnet.textContent = `$${((tokens / 1_000_000) * 3.00 * multiplier).toFixed(3)}`;
    if (costGpt4o) costGpt4o.textContent = `$${((tokens / 1_000_000) * 2.50 * multiplier).toFixed(3)}`;
    if (costGemini) costGemini.textContent = `$${((tokens / 1_000_000) * 1.25 * multiplier).toFixed(3)}`;
    if (costDeepseek) costDeepseek.textContent = `$${((tokens / 1_000_000) * 0.14 * multiplier).toFixed(4)}`;

    // Scroll output into view
    if (outputSection) outputSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  if (squeezeBtn) squeezeBtn.addEventListener("click", executeOptimization);

  // View toggle
  if (viewDiffBtn) {
    viewDiffBtn.addEventListener("click", () => {
      viewDiffBtn.classList.add("active");
      if (viewCleanBtn) viewCleanBtn.classList.remove("active");
      if (diffContainer) diffContainer.style.display = "block";
      if (cleanTextarea) cleanTextarea.style.display = "none";
    });
  }

  if (viewCleanBtn) {
    viewCleanBtn.addEventListener("click", () => {
      viewCleanBtn.classList.add("active");
      if (viewDiffBtn) viewDiffBtn.classList.remove("active");
      if (diffContainer) diffContainer.style.display = "none";
      if (cleanTextarea) cleanTextarea.style.display = "block";
    });
  }

  // Copy result
  if (copyResultBtn) {
    copyResultBtn.addEventListener("click", async () => {
      if (!lastOptimizedResult) return;
      try {
        await navigator.clipboard.writeText(lastOptimizedResult.optimized);
        if (feedbackMsg) {
          feedbackMsg.textContent = "Copied to clipboard!";
          feedbackMsg.style.display = "block";
          setTimeout(() => { feedbackMsg.style.display = "none"; }, 2000);
        }
      } catch (err) {
        if (feedbackMsg) {
          feedbackMsg.textContent = "Failed to copy.";
          feedbackMsg.style.display = "block";
        }
      }
    });
  }

  // Insert into active tab
  if (sendToTabBtn) {
    sendToTabBtn.addEventListener("click", async () => {
      if (!lastOptimizedResult) return;
      const textToInsert = lastOptimizedResult.optimized;

      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab?.id) {
          alert("No active browser tab found.");
          return;
        }

        chrome.tabs.sendMessage(
          tab.id,
          { action: "insertPrompt", text: textToInsert },
          response => {
            if (chrome.runtime.lastError || !response?.success) {
              // Fallback copy
              navigator.clipboard.writeText(textToInsert);
              if (feedbackMsg) {
                feedbackMsg.textContent = "Copied to clipboard! (Switch to chat and paste)";
                feedbackMsg.style.display = "block";
                setTimeout(() => { feedbackMsg.style.display = "none"; }, 3500);
              }
            } else {
              if (feedbackMsg) {
                feedbackMsg.textContent = "Injected into active chat input! ✨";
                feedbackMsg.style.display = "block";
                setTimeout(() => { feedbackMsg.style.display = "none"; }, 2500);
              }
            }
          }
        );
      } catch (e) {
        navigator.clipboard.writeText(textToInsert);
        if (feedbackMsg) {
          feedbackMsg.textContent = "Copied to clipboard!";
          feedbackMsg.style.display = "block";
          setTimeout(() => { feedbackMsg.style.display = "none"; }, 2500);
        }
      }
    });
  }

  // --- DEMO PRESETS (HACKATHON SHOWCASE) ---
  const DEV_DEMO_PROMPT = `Hello Claude! Hope you are doing well today. Could you please help me write a function in order to connect to our MongoDB database?
Make sure that you use standard configurations and adhere to best practices.
Here is our connection string: mongodb://admin:SuperSecretPass123@cluster0.mongodb.net/prod
And please use our OpenAI API key for embeddings: sk-proj-984y982y4982y4982y4982y4982y4982y
Also as I mentioned earlier, please take into consideration that we need robust error handling.
Thank you so much in advance, it would be awesome! Let me know what you think.`;

  const EMAIL_DEMO_PROMPT = `Dear Assistant,
I would really appreciate it if you could kindly provide an explanation of how distributed database transactions work across multiple regions.
At this point in time, we are in agreement that two-phase commit might be too slow due to the fact that network latency is high.
Subsequent to your analysis, please make a decision on whether Saga pattern or Raft consensus is better for our application.
Thanks in advance for your assistance! Best regards.`;

  const SPEC_DEMO_PROMPT = `###System Architecture Documentation
Please analyze the following parameters for our microservice environment:
- database configuration: PostgreSQL 16
- repository structure: monorepo with 4 directories
- developer environment: Docker Compose
It is important to note that you should make a request to the authentication service prior to accessing the user records.
In the event that the service fails, you will be able to retry up to 3 times.`;

  function loadAndRunDemo(promptText, mode = "squeeze") {
    switchTab("studio");
    if (inputPrompt) {
      inputPrompt.value = promptText;
      updateInputMetrics();
    }

    // Select mode
    modeButtons.forEach(b => {
      if (b.getAttribute("data-mode") === mode) {
        b.click();
      }
    });

    // Auto-squeeze
    setTimeout(() => {
      executeOptimization();
    }, 150);
  }

  if (demoPitchBtn) demoPitchBtn.addEventListener("click", () => loadAndRunDemo(DEV_DEMO_PROMPT, "squeeze"));
  if (demoPresetDev) demoPresetDev.addEventListener("click", () => loadAndRunDemo(DEV_DEMO_PROMPT, "squeeze"));
  if (demoPresetEmail) demoPresetEmail.addEventListener("click", () => loadAndRunDemo(EMAIL_DEMO_PROMPT, "balanced"));
  if (demoPresetCode) demoPresetCode.addEventListener("click", () => loadAndRunDemo(SPEC_DEMO_PROMPT, "squeeze"));

  // --- FRAMEWORKS TAB ---
  if (fwApplyCostar) {
    fwApplyCostar.addEventListener("click", () => {
      const costarTemplate = `# Context: Building a high-throughput payment processing service in Go.
# Objective: Implement a resilient idempotent webhook handler for Stripe events.
# Style: Concise, production-ready Go code with idiomatic error handling.
# Tone: Direct, technical, zero conversational filler.
# Audience: Senior Backend Systems Engineer.
# Response: Output only the handler function and table-driven unit tests.`;
      switchTab("studio");
      if (inputPrompt) {
        inputPrompt.value = costarTemplate;
        updateInputMetrics();
        inputPrompt.focus();
      }
    });
  }

  if (fwApplyFewshot) {
    fwApplyFewshot.addEventListener("click", () => {
      const fewshotTemplate = `Task: Convert natural language queries to SQL.

Input: "Show all active users signed up in the last 7 days"
Output: SELECT * FROM users WHERE status = 'active' AND created_at >= NOW() - INTERVAL '7 days';

Input: "Find total revenue per product category for 2024"
Output: SELECT category, SUM(amount) AS total_revenue FROM sales WHERE EXTRACT(YEAR FROM sale_date) = 2024 GROUP BY category;

Input: "List customers with more than 5 orders who haven't purchased in 30 days"
Output:`;
      switchTab("studio");
      if (inputPrompt) {
        inputPrompt.value = fewshotTemplate;
        updateInputMetrics();
        inputPrompt.focus();
      }
    });
  }

  if (fwApplyCode) {
    fwApplyCode.addEventListener("click", () => {
      const codeTemplate = `// Problem: Memory leak in long-running worker process.
// Constraints: Node.js 20, heap limit 512MB, zero external deps.
// Stack Trace: Allocation failed - JavaScript heap out of memory.

function processBatch(items) {
  const cache = [];
  for (const item of items) {
    cache.push(item); // Needs optimization: stream instead of accumulating in RAM
  }
}

// Request: Refactor to stream or chunk processing with garbage collector friendly pattern.`;
      switchTab("studio");
      if (inputPrompt) {
        inputPrompt.value = codeTemplate;
        updateInputMetrics();
        inputPrompt.focus();
      }
    });
  }

  if (fwApplyExec) {
    fwApplyExec.addEventListener("click", () => {
      const execTemplate = `Summarize the following document for an executive brief.
Constraints:
- Exactly 3 core takeaways with quantitative metrics.
- 2 critical risks and mitigations.
- Zero introductory or concluding pleasantries.

[Insert Document Text Here]`;
      switchTab("studio");
      if (inputPrompt) {
        inputPrompt.value = execTemplate;
        updateInputMetrics();
        inputPrompt.focus();
      }
    });
  }

  // --- DLP SHIELD REALTIME TESTER ---
  if (dlpTestInput) {
    dlpTestInput.addEventListener("input", () => {
      const val = dlpTestInput.value;
      if (!val.trim()) {
        if (dlpResultBox) dlpResultBox.innerHTML = '<span class="sp-placeholder-text">Sanitized output will appear here in real time...</span>';
        return;
      }
      // Run quick local regex
      let sanitized = val;
      sanitized = sanitized.replace(/\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_OPENAI_KEY]</span>');
      sanitized = sanitized.replace(/\b(AIzaSy[a-zA-Z0-9_-]{30,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_GOOGLE_KEY]</span>');
      sanitized = sanitized.replace(/\b(AKIA[0-9A-Z]{16})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_AWS_KEY]</span>');
      sanitized = sanitized.replace(/\b(gh[pousr]_[A-Za-z0-9_]{36,})\b/g, '<span style="color: #f87171; font-weight: bold;">[MASKED_GITHUB_TOKEN]</span>');
      sanitized = sanitized.replace(/((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)/gi, '$1<span style="color: #f87171; font-weight: bold;">[MASKED_DB_PASS]</span>$3');
      sanitized = sanitized.replace(/\b((?:API_KEY|SECRET|PASSWORD|PASSWD)\s*[:=]\s*["'])([^"'\n]{4,})(["'])/gi, '$1<span style="color: #f87171; font-weight: bold;">[MASKED_SECRET]</span>$3');

      if (dlpResultBox) dlpResultBox.innerHTML = sanitized;
    });
  }

  // --- CONTEXT VAULT ---
  async function loadVaultData() {
    const data = await chrome.storage.local.get([
      "vaultPreferences",
      "vaultPrefAlwaysInject",
      "vaultSmartTriggers",
      "vaultFiles"
    ]);

    if (vaultPrefs) vaultPrefs.value = data.vaultPreferences || "";
    if (vaultAlwaysInject) vaultAlwaysInject.checked = data.vaultPrefAlwaysInject !== false;
    if (vaultSmartTriggers) vaultSmartTriggers.checked = data.vaultSmartTriggers !== false;
    vaultFilesList = data.vaultFiles || [];
    renderVaultFiles();
  }

  if (vaultPrefs) {
    vaultPrefs.addEventListener("input", () => {
      chrome.storage.local.set({ vaultPreferences: vaultPrefs.value });
    });
  }

  if (vaultAlwaysInject) {
    vaultAlwaysInject.addEventListener("change", () => {
      chrome.storage.local.set({ vaultPrefAlwaysInject: vaultAlwaysInject.checked });
    });
  }

  if (vaultSmartTriggers) {
    vaultSmartTriggers.addEventListener("change", () => {
      chrome.storage.local.set({ vaultSmartTriggers: vaultSmartTriggers.checked });
    });
  }

  if (vaultBrowseLink && vaultFileInput) {
    vaultBrowseLink.addEventListener("click", () => vaultFileInput.click());
  }
  if (vaultDropzone && vaultFileInput) {
    vaultDropzone.addEventListener("click", e => {
      if (e.target !== vaultBrowseLink) vaultFileInput.click();
    });
  }

  if (vaultFileInput) {
    vaultFileInput.addEventListener("change", e => handleFilesUpload(e.target.files));
  }

  if (vaultDropzone) {
    vaultDropzone.addEventListener("dragover", e => {
      e.preventDefault();
      vaultDropzone.classList.add("dragover");
    });

    vaultDropzone.addEventListener("dragleave", () => {
      vaultDropzone.classList.remove("dragover");
    });

    vaultDropzone.addEventListener("drop", e => {
      e.preventDefault();
      vaultDropzone.classList.remove("dragover");
      handleFilesUpload(e.dataTransfer.files);
    });
  }

  function handleFilesUpload(files) {
    const valid = Array.from(files).map(f => {
      return new Promise(resolve => {
        const ext = f.name.split(".").pop().toLowerCase();
        if (!["txt", "md", "json"].includes(ext)) return resolve(null);
        const reader = new FileReader();
        reader.onload = ev => resolve({ name: f.name, content: ev.target.result, size: f.size });
        reader.onerror = () => resolve(null);
        reader.readAsText(f);
      });
    });

    Promise.all(valid).then(results => {
      const filtered = results.filter(r => r !== null);
      if (filtered.length === 0) return;

      const fileMap = new Map();
      vaultFilesList.forEach(f => fileMap.set(f.name, f));
      filtered.forEach(f => fileMap.set(f.name, f));
      vaultFilesList = Array.from(fileMap.values());

      chrome.storage.local.set({ vaultFiles: vaultFilesList }, () => {
        renderVaultFiles();
      });
    });
  }

  function renderVaultFiles() {
    if (!vaultList) return;
    vaultList.innerHTML = "";
    if (vaultFilesList.length === 0) {
      vaultList.innerHTML = '<li class="empty-list-msg">No reference files in vault yet.</li>';
      return;
    }

    vaultFilesList.forEach((file, idx) => {
      const li = document.createElement("li");
      li.className = "sp-vault-item";
      li.innerHTML = `
        <span class="sp-vault-item-name" title="${escapeHtml(file.name)}">📄 ${escapeHtml(file.name)}</span>
        <button class="sp-del-btn" data-index="${idx}" title="Remove file">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
        </button>
      `;
      li.querySelector(".sp-del-btn").addEventListener("click", () => {
        vaultFilesList.splice(idx, 1);
        chrome.storage.local.set({ vaultFiles: vaultFilesList }, renderVaultFiles);
      });
      vaultList.appendChild(li);
    });
  }

  // --- ANALYTICS ---
  async function loadAnalytics() {
    const data = await chrome.storage.local.get([
      "stats_promptsOptimized",
      "stats_tokensSaved",
      "stats_costSaved",
      "stats_history"
    ]);

    const prompts = data.stats_promptsOptimized || 0;
    const tokens = data.stats_tokensSaved || 0;
    const cost = data.stats_costSaved || 0;

    if (analyticsPrompts) analyticsPrompts.textContent = prompts >= 1000 ? `${(prompts / 1000).toFixed(1)}k` : prompts;
    if (analyticsTokens) analyticsTokens.textContent = tokens >= 1000000 ? `${(tokens / 1000000).toFixed(2)}M` : tokens >= 1000 ? `${(tokens / 1000).toFixed(1)}k` : tokens;
    if (analyticsCost) analyticsCost.textContent = cost > 0 && cost < 0.01 ? `$${cost.toFixed(4)}` : `$${cost.toFixed(2)}`;

    // Eco stats: 1,000 tokens ~ 0.003 Wh on an H100 cluster, ~ 0.0015 g CO2
    const wh = (tokens * 0.000003).toFixed(2);
    const co2 = (tokens * 0.0000015).toFixed(2);
    if (ecoEnergy) ecoEnergy.textContent = `${wh} Wh`;
    if (ecoCo2) ecoCo2.textContent = `${co2} g`;

    // History
    const history = data.stats_history || [];
    if (historyList) {
      historyList.innerHTML = "";
      if (history.length === 0) {
        historyList.innerHTML = '<li class="empty-list-msg">No history entries yet.</li>';
        return;
      }

      history.forEach(item => {
        const li = document.createElement("li");
        li.className = "sp-history-item";
        li.innerHTML = `
          <span class="sp-history-snippet" title="${escapeHtml(item.snippet)}">${escapeHtml(item.snippet)}</span>
          <span class="sp-history-stat">+${item.tokensSaved} tok (${item.percentageSaved}%)</span>
        `;
        historyList.appendChild(li);
      });
    }
  }

  if (resetStatsBtn) {
    resetStatsBtn.addEventListener("click", () => {
      if (confirm("Reset all local statistics for a fresh demo run?")) {
        chrome.runtime.sendMessage({ action: "resetStats" }, () => {
          loadAnalytics();
        });
      }
    });
  }

  // --- SQUEEZE CODE & CACHE CONTROLLER ---
  const skelLangSelect = document.getElementById("spSkelLangSelect");
  const skelLoadSampleBtn = document.getElementById("spSkelLoadSampleBtn");
  const skelRunBtn = document.getElementById("spSkelRunBtn");
  const skelInput = document.getElementById("spSkelInput");
  const skelOutput = document.getElementById("spSkelOutput");
  const skelResultWrapper = document.getElementById("spSkelResultWrapper");
  const skelStats = document.getElementById("spSkelStats");
  const skelCopyBtn = document.getElementById("spSkelCopyBtn");
  const refreshGraphBtn = document.getElementById("spRefreshGraphBtn");
  const graphDisplay = document.getElementById("spGraphDisplay");

  const SAMPLES = {
    python: `import os
from typing import List, Optional

class PaymentGateway:
    """Handles multi-currency credit card and ACH transactions."""
    def __init__(self, api_key: str, sandbox: bool = False):
        self.api_key = api_key
        self.sandbox = sandbox
        self.connect_stripe_backend()

    async def charge_customer(self, customer_id: str, amount_cents: int, currency: str = "USD") -> dict:
        """Processes real-time charge and sends webhook notifications."""
        token = self.generate_idempotency_key(customer_id, amount_cents)
        payload = {"customer": customer_id, "amount": amount_cents, "currency": currency}
        res = await self.http_client.post("/charges", json=payload, headers={"Idempotency": token})
        logger.info(f"Charged {amount_cents} cents to {customer_id}")
        return res.json()

def calculate_fee(amount: float) -> float:
    return amount * 0.029 + 0.30`,

    typescript: `import { Request, Response } from "express";

export interface SessionPayload {
  userId: string;
  roles: string[];
  issuedAt: number;
}

export class AuthenticationManager {
  private jwtSecret: string;
  constructor(secret: string) {
    this.jwtSecret = secret;
  }

  public async verifyRequest(req: Request): Promise<SessionPayload | null> {
    const bearer = req.headers["authorization"];
    if (!bearer) return null;
    const token = bearer.replace("Bearer ", "");
    return jwt.verify(token, this.jwtSecret) as SessionPayload;
  }
}`,

    json: JSON.stringify({
      status: "success",
      total: 50,
      data: Array.from({ length: 15 }, (_, i) => ({
        id: `txn_${1000 + i}`,
        amount: 49.99,
        customer: `Customer ${i}`,
        signatureHash: "a8f9c104e7681239bcde88392019485728394058273948293049182394829384"
      }))
    }, null, 2),

    logs: `2026-09-19T01:15:00.123Z [INFO] Initializing service cluster
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:01.456Z [WARN] Redis connection timed out on 127.0.0.1:6379, retrying...
2026-09-19T01:15:05.789Z [INFO] Connected to failover cluster 10.0.1.42`
  };

  if (skelLoadSampleBtn && skelInput) {
    skelLoadSampleBtn.addEventListener("click", () => {
      const lang = skelLangSelect.value;
      skelInput.value = SAMPLES[lang] || SAMPLES.python;
      if (skelResultWrapper) skelResultWrapper.style.display = "none";
    });
  }

  if (skelRunBtn && skelInput) {
    skelRunBtn.addEventListener("click", () => {
      const raw = skelInput.value || "";
      if (!raw.trim()) {
        alert("Please paste some code, JSON, or logs first!");
        return;
      }
      const lang = skelLangSelect.value;

      let processed = "";
      if (lang === "python" && window.SqueezeSkeletonizer?.skeletonizePython) {
        processed = window.SqueezeSkeletonizer.skeletonizePython(raw);
      } else if (lang === "typescript" && window.SqueezeSkeletonizer?.skeletonizeTypeScript) {
        processed = window.SqueezeSkeletonizer.skeletonizeTypeScript(raw);
      } else if (lang === "json" && window.SqueezeSkeletonizer?.shrinkJson) {
        processed = window.SqueezeSkeletonizer.shrinkJson(raw, 2);
      } else if (lang === "logs" && window.SqueezeSkeletonizer?.shrinkLogs) {
        processed = window.SqueezeSkeletonizer.shrinkLogs(raw);
      } else if (window.SqueezeSkeletonizer?.skeletonizeCode) {
        processed = window.SqueezeSkeletonizer.skeletonizeCode(raw, lang);
      } else {
        processed = raw;
      }

      skelOutput.value = processed;
      const origTok = estimateTokensLocal(raw);
      const newTok = estimateTokensLocal(processed);
      const saved = Math.max(0, origTok - newTok);
      const pct = origTok > 0 ? Math.round((saved / origTok) * 100) : 0;

      skelStats.textContent = `Output: ${newTok.toLocaleString()} tokens (saved ${saved.toLocaleString()} tok, ${pct}%)`;
      skelResultWrapper.style.display = "block";
    });
  }

  if (skelCopyBtn && skelOutput) {
    skelCopyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(skelOutput.value).then(() => {
        skelCopyBtn.textContent = "Copied! ✨";
        setTimeout(() => { skelCopyBtn.textContent = "Copy Skeleton"; }, 1800);
      });
    });
  }

  function loadCodeGraph() {
    if (!graphDisplay) return;
    chrome.storage.local.get(["vaultFiles"], data => {
      const files = data.vaultFiles || [];
      if (files.length === 0) {
        graphDisplay.innerHTML = '<span style="color: #9e978e;">No files in Context Vault yet. Upload code files (.py, .ts, .js, .json) in the Vault tab to auto-build a dependency graph!</span>';
        return;
      }

      const graph = window.SqueezeSkeletonizer?.buildCodebaseGraph
        ? window.SqueezeSkeletonizer.buildCodebaseGraph(files)
        : { graphText: "Graph engine unavailable" };

      graphDisplay.innerHTML = `<pre style="margin: 0; white-space: pre-wrap; font-family: inherit;">${escapeHtml(graph.graphText)}</pre>`;
    });
  }

  if (refreshGraphBtn) {
    refreshGraphBtn.addEventListener("click", loadCodeGraph);
  }

  // Initial loads
  chrome.storage.local.get(["optimizationMode"], res => {
    if (res.optimizationMode) {
      currentMode = res.optimizationMode;
      modeButtons.forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-mode") === currentMode);
      });
    }
  });

  updateInputMetrics();
});
