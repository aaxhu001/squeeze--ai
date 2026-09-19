/**
 * Squeeze AI - Popup Dashboard Script (Manifest V3)
 * Handles popup stats display, quick Side Panel launching,
 * optimization mode selection, rule configuration, and Context Vault.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation elements
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  // Dashboard elements
  const statPrompts = document.getElementById("statPrompts");
  const statTokens = document.getElementById("statTokens");
  const statCost = document.getElementById("statCost");
  const statusBadge = document.getElementById("statusBadge");

  // Side Panel triggers
  const openSidePanelTopBtn = document.getElementById("openSidePanelTopBtn");
  const openSidePanelActionBtn = document.getElementById("openSidePanelActionBtn");
  const footerStudioLink = document.getElementById("footerStudioLink");

  // Settings form elements
  const settingsForm = document.getElementById("settingsForm");
  const ruleSecretShield = document.getElementById("ruleSecretShield");
  const ruleStripGreetings = document.getElementById("ruleStripGreetings");
  const ruleSimplifyPhrases = document.getElementById("ruleSimplifyPhrases");
  const ruleAbbreviate = document.getElementById("ruleAbbreviate");
  const ruleStripArticles = document.getElementById("ruleStripArticles");
  const rulePolishMarkdown = document.getElementById("rulePolishMarkdown");
  const saveFeedback = document.getElementById("saveFeedback");

  // Vault elements
  const vaultPreferences = document.getElementById("vaultPreferences");
  const vaultPrefAlwaysInject = document.getElementById("vaultPrefAlwaysInject");
  const vaultSmartTriggers = document.getElementById("vaultSmartTriggers");
  const vaultDropZone = document.getElementById("vaultDropZone");
  const vaultFileInput = document.getElementById("vaultFileInput");
  const vaultBrowseLink = document.getElementById("vaultBrowseLink");
  const vaultFileList = document.getElementById("vaultFileList");

  let localVaultFiles = [];

  // --- TAB NAVIGATION ---
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const target = document.getElementById(`${tabId}Tab`);
      if (target) target.classList.add("active");
    });
  });

  // --- LAUNCH SIDE PANEL ---
  // Fix #1 (Critical): chrome.sidePanel.open() MUST be called within a user gesture
  // handler in the popup. Relaying through background.js loses the gesture context
  // and silently fails. We call it directly here.
  async function launchSidePanel() {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && chrome.sidePanel?.open) {
        await chrome.sidePanel.open({ windowId: tab.windowId });
      }
    } catch (err) {
      console.warn("Side panel open failed:", err);
    }
    window.close();
  }

  if (openSidePanelTopBtn) openSidePanelTopBtn.addEventListener("click", launchSidePanel);
  if (openSidePanelActionBtn) openSidePanelActionBtn.addEventListener("click", launchSidePanel);
  if (footerStudioLink) {
    footerStudioLink.addEventListener("click", e => {
      e.preventDefault();
      launchSidePanel();
    });
  }

  // --- NUMBER FORMATTER ---
  function formatNumber(num) {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toString();
  }

  function formatBytes(bytes) {
    if (!bytes || bytes <= 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB"];
    const i = Math.min(Math.floor(Math.log(bytes) / Math.log(k)), sizes.length - 1);
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- LOAD SETTINGS & STATS ---
  function loadDashboardData() {
    chrome.storage.local.get(
      [
        "optimizationMode",
        "ruleSecretShield",
        "ruleStripGreetings",
        "ruleSimplifyPhrases",
        "ruleAbbreviate",
        "ruleStripArticles",
        "rulePolishMarkdown",
        "stats_promptsOptimized",
        "stats_tokensSaved",
        "stats_costSaved",
        "vaultPreferences",
        "vaultPrefAlwaysInject",
        "vaultSmartTriggers",
        "vaultFiles"
      ],
      data => {
        // Mode
        const mode = data.optimizationMode || "balanced";
        const modeRadio = document.querySelector(`input[name="optimizationMode"][value="${mode}"]`);
        if (modeRadio) modeRadio.checked = true;

        // Rules
        if (ruleSecretShield) ruleSecretShield.checked = data.ruleSecretShield !== false;
        if (ruleStripGreetings) ruleStripGreetings.checked = data.ruleStripGreetings !== false;
        if (ruleSimplifyPhrases) ruleSimplifyPhrases.checked = data.ruleSimplifyPhrases !== false;
        if (ruleAbbreviate) ruleAbbreviate.checked = data.ruleAbbreviate !== false;
        if (ruleStripArticles) ruleStripArticles.checked = data.ruleStripArticles !== false;
        if (rulePolishMarkdown) rulePolishMarkdown.checked = data.rulePolishMarkdown !== false;

        // Stats — Fix #13: guard against null elements to prevent popup blank crashes
        const prompts = data.stats_promptsOptimized || 0;
        const tokens = data.stats_tokensSaved || 0;
        const cost = data.stats_costSaved || 0;

        if (statPrompts) statPrompts.textContent = formatNumber(prompts);
        if (statTokens) statTokens.textContent = formatNumber(tokens);
        if (statCost) statCost.textContent = cost > 0 && cost < 0.01 ? `$${cost.toFixed(4)}` : `$${cost.toFixed(2)}`;

        // Vault
        if (vaultPreferences) vaultPreferences.value = data.vaultPreferences || "";
        if (vaultPrefAlwaysInject) vaultPrefAlwaysInject.checked = data.vaultPrefAlwaysInject !== false;
        if (vaultSmartTriggers) vaultSmartTriggers.checked = data.vaultSmartTriggers !== false;
        localVaultFiles = data.vaultFiles || [];
        if (vaultFileList) renderVaultFiles();

        // Apply article strip greying after mode is set
        updateArticleStripState();
      }
    );
  }

  // --- SAVE SETTINGS ---
  // Fix #8: Grey-out "Strip Articles" when not in Squeeze mode — it only activates there.
  function updateArticleStripState() {
    if (!ruleStripArticles) return;
    const mode = document.querySelector('input[name="optimizationMode"]:checked')?.value || "balanced";
    const isSqueeze = mode === "squeeze";
    ruleStripArticles.disabled = !isSqueeze;
    const label = ruleStripArticles.closest("label") || ruleStripArticles.nextElementSibling;
    if (label) {
      label.style.opacity = isSqueeze ? "1" : "0.45";
      label.style.cursor = isSqueeze ? "" : "not-allowed";
      label.title = isSqueeze ? "" : "Only active in Squeeze mode";
    }
  }
  // Run on mode change
  document.querySelectorAll('input[name="optimizationMode"]').forEach(radio => {
    radio.addEventListener("change", updateArticleStripState);
  });

  if (settingsForm) {
    settingsForm.addEventListener("submit", e => {
      e.preventDefault();
      const mode = document.querySelector('input[name="optimizationMode"]:checked')?.value || "balanced";

      chrome.storage.local.set(
        {
          optimizationMode: mode,
          ruleSecretShield: ruleSecretShield ? ruleSecretShield.checked : true,
          ruleStripGreetings: ruleStripGreetings ? ruleStripGreetings.checked : true,
          ruleSimplifyPhrases: ruleSimplifyPhrases ? ruleSimplifyPhrases.checked : true,
          ruleAbbreviate: ruleAbbreviate ? ruleAbbreviate.checked : true,
          ruleStripArticles: ruleStripArticles ? ruleStripArticles.checked : true,
          rulePolishMarkdown: rulePolishMarkdown ? rulePolishMarkdown.checked : true
        },
        () => {
          if (saveFeedback) {
            saveFeedback.classList.add("show");
            setTimeout(() => {
              saveFeedback.classList.remove("show");
            }, 2500);
          }
        }
      );
    });
  }

  // --- VAULT PREFERENCES AUTO-SAVE ---
  if (vaultPreferences) {
    vaultPreferences.addEventListener("input", () => {
      chrome.storage.local.set({ vaultPreferences: vaultPreferences.value });
    });
  }

  if (vaultPrefAlwaysInject) {
    vaultPrefAlwaysInject.addEventListener("change", () => {
      chrome.storage.local.set({ vaultPrefAlwaysInject: vaultPrefAlwaysInject.checked });
    });
  }

  if (vaultSmartTriggers) {
    vaultSmartTriggers.addEventListener("change", () => {
      chrome.storage.local.set({ vaultSmartTriggers: vaultSmartTriggers.checked });
    });
  }

  // --- VAULT FILES UPLOAD ---
  if (vaultBrowseLink && vaultFileInput) {
    vaultBrowseLink.addEventListener("click", e => {
      e.preventDefault();
      vaultFileInput.click();
    });
  }

  if (vaultFileInput) {
    vaultFileInput.addEventListener("change", e => {
      processUploadedFiles(e.target.files);
    });
  }

  if (vaultDropZone) {
    vaultDropZone.addEventListener("dragover", e => {
      e.preventDefault();
      vaultDropZone.classList.add("dragover");
    });

    vaultDropZone.addEventListener("dragleave", () => {
      vaultDropZone.classList.remove("dragover");
    });

    vaultDropZone.addEventListener("drop", e => {
      e.preventDefault();
      vaultDropZone.classList.remove("dragover");
      processUploadedFiles(e.dataTransfer.files);
    });
  }

  function processUploadedFiles(files) {
    const MAX_FILE_BYTES  = 500 * 1024;  // 500 KB per file
    const MAX_VAULT_BYTES = 3 * 1024 * 1024; // 3 MB total vault

    const promises = Array.from(files).map(f => {
      return new Promise(resolve => {
        const ext = f.name.split(".").pop().toLowerCase();
        if (!["txt", "md", "json"].includes(ext)) return resolve(null);
        // Fix #6: Enforce per-file size limit to prevent storage quota crashes
        if (f.size > MAX_FILE_BYTES) {
          alert(`"${f.name}" exceeds the 500 KB limit (${(f.size / 1024).toFixed(0)} KB). Please trim it before uploading.`);
          return resolve(null);
        }
        const reader = new FileReader();
        reader.onload = ev => resolve({ name: f.name, content: ev.target.result, size: f.size });
        reader.onerror = () => resolve(null);
        reader.readAsText(f);
      });
    });

    Promise.all(promises).then(results => {
      const valid = results.filter(r => r !== null);
      if (valid.length === 0) return;

      const map = new Map();
      localVaultFiles.forEach(f => map.set(f.name, f));
      valid.forEach(f => map.set(f.name, f));
      const merged = Array.from(map.values());

      // Fix #6: Enforce total vault size limit
      const totalBytes = merged.reduce((sum, f) => sum + (f.size || 0), 0);
      if (totalBytes > MAX_VAULT_BYTES) {
        alert(`Vault total would exceed 3 MB (${(totalBytes / 1024 / 1024).toFixed(1)} MB). Remove some files first.`);
        return;
      }

      localVaultFiles = merged;
      chrome.storage.local.set({ vaultFiles: localVaultFiles }, () => {
        renderVaultFiles();
      });
    });
  }

  function renderVaultFiles() {
    vaultFileList.innerHTML = "";
    if (localVaultFiles.length === 0) {
      const empty = document.createElement("li");
      empty.className = "empty-list-msg";
      empty.textContent = "No files uploaded to the vault yet.";
      vaultFileList.appendChild(empty);
      return;
    }

    localVaultFiles.forEach((file, index) => {
      const li = document.createElement("li");
      li.className = "vault-file-item";
      li.innerHTML = `
        <div class="file-item-info">
          <span class="file-item-name" title="${escapeHtml(file.name)}">📄 ${escapeHtml(file.name)}</span>
          <span class="file-item-size">${formatBytes(file.size)}</span>
        </div>
        <button class="file-delete-btn" data-index="${index}" title="Remove file">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      `;

      li.querySelector(".file-delete-btn").addEventListener("click", () => {
        localVaultFiles.splice(index, 1);
        chrome.storage.local.set({ vaultFiles: localVaultFiles }, renderVaultFiles);
      });

      vaultFileList.appendChild(li);
    });
  }

  loadDashboardData();
});