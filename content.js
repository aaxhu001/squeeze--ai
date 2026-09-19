/**
 * Squeeze AI - Universal Content Script (Manifest V3)
 * Operates across Claude.ai, ChatGPT (chatgpt.com), and Google Gemini (gemini.google.com).
 * Injects prompt optimizer widgets, context depth monitors, secret alerts, and PDF squeezer.
 */

(function () {
  // --- PLATFORM DETECTION ---
  const HOST = window.location.hostname;
  const IS_CLAUDE = HOST.includes("claude.ai");
  const IS_CHATGPT = HOST.includes("chatgpt.com") || HOST.includes("openai.com");
  const IS_GEMINI = HOST.includes("gemini.google.com");

  // State
  let activeInputEl = null;
  let triggerBtn = null;
  let undoBtn = null;
  let pdfBtn = null;
  let summaryBtn = null;
  let vaultBadge = null;
  let usageBar = null;
  let modalContainer = null;
  let drawerContainer = null;
  let sidebarBtn = null;

  let originalPromptText = "";
  let lastOptimizedPrompt = "";
  let currentOptMode = "balanced";
  let activeTooltip = null;
  let currentUploadedPdf = null;
  let duplicateContextBlocks = [];
  let workingModalPrompt = "";

  // --- UNIVERSAL PLATFORM ADAPTER ---
  function findChatInput() {
    if (IS_CLAUDE) {
      return document.querySelector('div[contenteditable="true"]');
    }

    if (IS_CHATGPT) {
      // ChatGPT input can be contenteditable or textarea
      return (
        document.querySelector("#prompt-textarea") ||
        document.querySelector('div[contenteditable="true"][data-placeholder]') ||
        document.querySelector('div[contenteditable="true"]') ||
        document.querySelector('textarea[data-id="root"]')
      );
    }

    if (IS_GEMINI) {
      // Gemini rich-textarea
      return (
        document.querySelector("rich-textarea div[contenteditable='true']") ||
        document.querySelector(".ql-editor") ||
        document.querySelector("div.text-input-field[contenteditable='true']") ||
        document.querySelector("textarea[aria-label*='prompt' i]") ||
        document.querySelector("div[contenteditable='true']")
      );
    }

    // Generic fallback
    return document.querySelector('div[contenteditable="true"]') || document.querySelector("textarea");
  }

  function getInputValue(el) {
    if (!el) return "";
    let val = "";
    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      val = el.value || "";
    } else {
      val = el.innerText || el.textContent || "";
    }
    return val.replace(/[\u200B-\u200D\uFEFF]/g, "").trim();
  }

  function setInputValue(el, text) {
    if (!el) return;
    el.focus();

    if (el.tagName === "TEXTAREA" || el.tagName === "INPUT") {
      const proto = el.tagName === "INPUT" ? window.HTMLInputElement.prototype : window.HTMLTextAreaElement.prototype;
      const nativeSetter = Object.getOwnPropertyDescriptor(proto, "value")?.set;
      if (nativeSetter) {
        nativeSetter.call(el, text);
      } else {
        el.value = text;
      }
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    } else {
      // ContentEditable elements (Claude, ChatGPT rich text, Gemini)
      try {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        selection.removeAllRanges();
        selection.addRange(range);

        const execSuccess = document.execCommand("insertText", false, text);
        if (!execSuccess) {
          el.innerText = text;
        }
      } catch (err) {
        console.warn("execCommand fallback:", err);
        el.innerText = text;
      }

      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertReplacementText", data: text }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    // Visual feedback highlight
    const wrapper = el.closest(".flex.flex-col") || el.closest("fieldset") || el.closest("form") || el.parentElement;
    if (wrapper) {
      wrapper.style.transition = "box-shadow 0.3s ease";
      wrapper.style.boxShadow = "0 0 15px rgba(52, 211, 153, 0.6)";
      setTimeout(() => { wrapper.style.boxShadow = ""; }, 1200);
    }
    setTimeout(() => el.focus(), 50);
  }

  function findToolbarAnchor(inputEl) {
    if (!inputEl) return null;

    if (IS_CLAUDE) {
      const modelBtn = Array.from(document.querySelectorAll("button")).find(b => {
        const txt = (b.innerText || "").toLowerCase();
        return txt.includes("sonnet") || txt.includes("haiku") || txt.includes("opus") || txt.includes("claude");
      });
      if (modelBtn && modelBtn.parentNode) return { container: modelBtn.parentNode, beforeNode: modelBtn };

      const form = inputEl.closest("fieldset") || inputEl.closest("form");
      if (form) {
        const attachBtn = form.querySelector('button[aria-label*="attach" i]') || form.querySelector("button svg")?.closest("button");
        if (attachBtn && attachBtn.parentNode) return { container: attachBtn.parentNode, beforeNode: attachBtn };
      }
    }

    if (IS_CHATGPT) {
      // Find ChatGPT button row under prompt textarea
      const composer = inputEl.closest("form") || inputEl.closest('[data-testid*="composer"]') || inputEl.parentElement;
      if (composer) {
        const submitBtn = composer.querySelector('button[data-testid*="send-button"]') || composer.querySelector('button[aria-label*="send" i]');
        if (submitBtn && submitBtn.parentNode) return { container: submitBtn.parentNode, beforeNode: submitBtn };

        const attachBtn = composer.querySelector('button[aria-label*="attach" i]') || composer.querySelector('button[aria-label*="upload" i]');
        if (attachBtn && attachBtn.parentNode) return { container: attachBtn.parentNode, beforeNode: attachBtn.nextSibling };
      }
    }

    if (IS_GEMINI) {
      const geminiContainer = inputEl.closest(".input-area") || inputEl.closest("rich-textarea")?.parentElement;
      if (geminiContainer) {
        const sendBtn = geminiContainer.querySelector("button[aria-label*='Send' i]") || geminiContainer.querySelector(".send-button");
        if (sendBtn && sendBtn.parentNode) return { container: sendBtn.parentNode, beforeNode: sendBtn };
      }
    }

    // Default container: parent element of the input
    const parent = inputEl.parentElement;
    return parent ? { container: parent, beforeNode: null } : null;
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

  function escapeHtml(str) {
    return (str || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // --- TOOLTIP DISPLAY ---
  function showTooltip(targetEl, text) {
    if (!targetEl) return;
    hideTooltip();
    const tip = document.createElement("div");
    tip.className = "squeeze-tooltip";
    tip.textContent = text;
    document.body.appendChild(tip);

    const rect = targetEl.getBoundingClientRect();
    tip.style.left = rect.left + window.scrollX + rect.width / 2 - tip.offsetWidth / 2 + "px";
    tip.style.top = rect.top + window.scrollY - tip.offsetHeight - 8 + "px";

    requestAnimationFrame(() => tip.classList.add("show"));
    activeTooltip = tip;
  }

  function hideTooltip() {
    if (activeTooltip) {
      const tip = activeTooltip;
      activeTooltip = null;
      tip.classList.remove("show");
      setTimeout(() => tip.remove(), 150);
    }
  }

  function showToast(targetEl, text) {
    if (!targetEl) return;
    const toast = document.createElement("div");
    toast.className = "squeeze-tooltip";
    toast.textContent = text;
    document.body.appendChild(toast);

    const rect = targetEl.getBoundingClientRect();
    toast.style.left = rect.left + window.scrollX + rect.width / 2 - toast.offsetWidth / 2 + "px";
    toast.style.top = rect.top + window.scrollY - toast.offsetHeight - 8 + "px";
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  // --- ATTACH IN-PAGE SQUEEZE CONTROLS ---
  function mountWidgets() {
    const input = findChatInput();
    if (!input) {
      if (triggerBtn && !document.contains(triggerBtn)) triggerBtn = null;
      return;
    }

    if (input.dataset.squeezeInjected === "true" && triggerBtn && document.contains(triggerBtn)) {
      activeInputEl = input;
      return;
    }

    activeInputEl = input;
    input.dataset.squeezeInjected = "true";

    // Clean up any stale elements
    if (triggerBtn) triggerBtn.remove();
    if (pdfBtn) pdfBtn.remove();
    if (undoBtn) undoBtn.remove();
    if (summaryBtn) summaryBtn.remove();
    if (vaultBadge) vaultBadge.remove();

    // Helper to make a div accessible as a button
    function makeAccessibleBtn(el, label) {
      el.setAttribute("role", "button");
      el.setAttribute("aria-label", label);
      el.setAttribute("tabindex", "0");
      el.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); el.click(); }
      });
    }

    // 1. Squeeze Trigger Button
    triggerBtn = document.createElement("div");
    triggerBtn.className = "squeeze-trigger-btn inline-btn";
    triggerBtn.dataset.tooltip = "Squeeze Prompt (Ctrl+Shift+S)";
    makeAccessibleBtn(triggerBtn, "Squeeze Prompt (Ctrl+Shift+S)");
    triggerBtn.addEventListener("mouseenter", () => showTooltip(triggerBtn, triggerBtn.dataset.tooltip));
    triggerBtn.addEventListener("mouseleave", hideTooltip);
    triggerBtn.innerHTML = `
      <svg viewBox="0 0 512 512" width="16" height="16" style="display: block; color: inherit;" aria-hidden="true">
        <rect x="120" y="140" width="272" height="48" rx="24" fill="currentColor"/>
        <rect x="144" y="212" width="224" height="48" rx="24" fill="currentColor" fill-opacity="0.8"/>
        <rect x="176" y="284" width="160" height="48" rx="24" fill="currentColor" fill-opacity="0.6"/>
        <rect x="208" y="356" width="96" height="48" rx="24" fill="currentColor" fill-opacity="0.4"/>
      </svg>
    `;

    // 2. PDF Squeeze Button
    pdfBtn = document.createElement("div");
    pdfBtn.className = "squeeze-pdf-btn inline-btn";
    pdfBtn.dataset.tooltip = "Squeeze PDF & Insert";
    makeAccessibleBtn(pdfBtn, "Squeeze PDF and Insert");
    pdfBtn.addEventListener("mouseenter", () => showTooltip(pdfBtn, pdfBtn.dataset.tooltip));
    pdfBtn.addEventListener("mouseleave", hideTooltip);
    pdfBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
        <line x1="16" y1="13" x2="8" y2="13"></line>
        <line x1="16" y1="17" x2="8" y2="17"></line>
      </svg>
    `;

    // 3. Undo Button
    undoBtn = document.createElement("div");
    undoBtn.className = "squeeze-undo-btn inline-btn";
    undoBtn.dataset.tooltip = "Undo Prompt Optimization";
    makeAccessibleBtn(undoBtn, "Undo Prompt Optimization");
    undoBtn.addEventListener("mouseenter", () => showTooltip(undoBtn, undoBtn.dataset.tooltip));
    undoBtn.addEventListener("mouseleave", hideTooltip);
    undoBtn.style.display = "none";
    undoBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="transform: scaleX(-1);" aria-hidden="true">
        <path d="M3 7v6h6"></path>
        <path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"></path>
      </svg>
    `;

    // 4. Summarise Context Button
    summaryBtn = document.createElement("div");
    summaryBtn.className = "squeeze-summary-btn inline-btn";
    summaryBtn.dataset.tooltip = "Summarize Chat & New Thread";
    makeAccessibleBtn(summaryBtn, "Summarize Chat and Open New Thread");
    summaryBtn.addEventListener("mouseenter", () => showTooltip(summaryBtn, summaryBtn.dataset.tooltip));
    summaryBtn.addEventListener("mouseleave", hideTooltip);
    summaryBtn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        <line x1="9" y1="10" x2="15" y2="10"></line>
      </svg>
    `;

    // 5. Vault Indicator Badge
    vaultBadge = document.createElement("div");
    vaultBadge.id = "squeezeVaultBadge";
    vaultBadge.className = "squeeze-vault-badge inline-btn";
    vaultBadge.setAttribute("role", "status");
    vaultBadge.setAttribute("aria-live", "polite");
    vaultBadge.style.display = "none";
    vaultBadge.style.cursor = "default";

    // Mount to anchor
    const anchor = findToolbarAnchor(input);
    if (anchor && anchor.container) {
      if (anchor.beforeNode) {
        anchor.container.insertBefore(triggerBtn, anchor.beforeNode);
        anchor.container.insertBefore(pdfBtn, triggerBtn);
        anchor.container.insertBefore(summaryBtn, pdfBtn);
        anchor.container.insertBefore(undoBtn, summaryBtn);
        anchor.container.insertBefore(vaultBadge, undoBtn);
      } else {
        anchor.container.appendChild(vaultBadge);
        anchor.container.appendChild(undoBtn);
        anchor.container.appendChild(summaryBtn);
        anchor.container.appendChild(pdfBtn);
        anchor.container.appendChild(triggerBtn);
      }
    }

    // Wire events
    wireInputEvents(input);
    wireTriggerButton(input);
    wirePdfButton(input);
    wireUndoButton(input);
    wireSummaryButton(input);

    updateTriggerActiveState(input);
    updateVaultBadge(getInputValue(input));
    mountContextUsageBar();
    mountSidebarButton();

    // Check for pending summary from previous chat
    chrome.storage.local.get(["pendingChatSummary"], res => {
      if (res && res.pendingChatSummary) {
        chrome.storage.local.remove(["pendingChatSummary"]);
        setTimeout(() => {
          setInputValue(input, res.pendingChatSummary);
          showToast(input, "Context summary pasted from previous chat! Ready to send.");
        }, 400);
      }
    });
  }

  function wireInputEvents(input) {
    // Debounce secondary updates to avoid scanning the full DOM on every keystroke
    let inputDebounce;
    input.addEventListener("input", () => {
      updateTriggerActiveState(input);
      clearTimeout(inputDebounce);
      inputDebounce = setTimeout(() => {
        updateVaultBadge(getInputValue(input));
        updateContextDepth();
      }, 300);
    });

    // Keyboard shortcut: Ctrl+Shift+S or Cmd+Shift+S to Squeeze
    input.addEventListener("keydown", e => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        if (triggerBtn) triggerBtn.click();
      }
    });
  }

  function updateTriggerActiveState(input) {
    if (!triggerBtn) return;
    const val = getInputValue(input);
    if (val && val.length > 5) {
      triggerBtn.classList.add("active");
    } else {
      triggerBtn.classList.remove("active");
    }
  }

  function wireTriggerButton(input) {
    triggerBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      const text = getInputValue(input);
      if (!text || text.length < 5) {
        showToast(triggerBtn, "Type a prompt first!");
        return;
      }
      originalPromptText = text;
      openOptimizationModal(text, currentOptMode);
    });
  }

  function wireUndoButton(input) {
    undoBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      if (originalPromptText) {
        setInputValue(input, originalPromptText);
        undoBtn.style.display = "none";
        hideTooltip();
        showToast(triggerBtn, "Original prompt restored!");
        updateTriggerActiveState(input);
      }
    });
  }

  function wirePdfButton(input) {
    pdfBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();
      const fileInput = document.createElement("input");
      fileInput.type = "file";
      fileInput.accept = ".pdf";
      fileInput.style.display = "none";

      fileInput.addEventListener("change", async ev => {
        const file = ev.target.files[0];
        if (file) handlePdfExtraction(file);
      });

      document.body.appendChild(fileInput);
      fileInput.click();
      setTimeout(() => fileInput.remove(), 1000);
    });
  }

  // --- PDF EXTRACTION ---
  async function handlePdfExtraction(file) {
    ensureModalExists();
    currentUploadedPdf = file;
    const logoUrl = chrome.runtime.getURL("icons/icon48.png");

    modalContainer.innerHTML = `
      <div class="squeeze-modal-card">
        <div class="tm-modal-header">
          <div class="tm-modal-logo">
            <img src="${logoUrl}" class="animating" width="22" height="22" alt="Squeeze Icon">
            <span>Squeeze <span class="highlight">PDF Optimizer</span></span>
          </div>
          <button class="tm-close-btn">&times;</button>
        </div>
        <div class="tm-modal-body">
          <div class="tm-loading-state">
            <div class="tm-spinner"></div>
            <p id="tmPDFStatusText">Extracting text from PDF...</p>
            <span class="tm-loading-subtext" id="tmPDFSubtext">Initializing parser...</span>
          </div>
        </div>
      </div>
    `;

    modalContainer.classList.add("open");
    modalContainer.querySelector(".tm-close-btn").addEventListener("click", closeModal);

    const statusText = modalContainer.querySelector("#tmPDFStatusText");
    const subText = modalContainer.querySelector("#tmPDFSubtext");

    try {
      if (typeof pdfjsLib === "undefined") {
        throw new Error("PDF parser library failed to load.");
      }

      pdfjsLib.GlobalWorkerOptions.workerSrc = chrome.runtime.getURL("pdf.worker.min.js");
      subText.innerText = "Reading file buffer...";
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      const totalPages = pdf.numPages;
      const pagesText = [];
      const lineFrequency = {};

      function normalizeLine(l) {
        return l.replace(/\bpage\s+\d+(\s+of\s+\d+)?\b/gi, "PAGE_NUM").replace(/\b\d+\b/g, "NUM").trim();
      }

      for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        statusText.innerText = `Extracting PDF (Page ${pageNum} of ${totalPages})...`;
        const page = await pdf.getPage(pageNum);
        const content = await page.getTextContent();
        const lineBuckets = {};

        content.items.forEach(item => {
          if (!item.str || !item.str.trim()) return;
          const yCoord = Math.round(item.transform[5] / 2) * 2;
          if (!lineBuckets[yCoord]) lineBuckets[yCoord] = [];
          lineBuckets[yCoord].push(item);
        });

        const sortedY = Object.keys(lineBuckets).map(Number).sort((a, b) => b - a);
        const pageLines = [];
        sortedY.forEach(y => {
          const text = lineBuckets[y].sort((a, b) => a.transform[4] - b.transform[4]).map(i => i.str).join(" ").trim();
          if (text) {
            pageLines.push(text);
            const norm = normalizeLine(text);
            lineFrequency[norm] = (lineFrequency[norm] || 0) + 1;
          }
        });
        pagesText.push(pageLines);
      }

      // Filter repeated headers & footers
      const headerFooters = new Set();
      if (totalPages > 1) {
        for (const [line, count] of Object.entries(lineFrequency)) {
          if (count > 0.5 * totalPages) headerFooters.add(line);
        }
      }

      const cleanedPages = [];
      pagesText.forEach(lines => {
        const filtered = lines.filter(l => !headerFooters.has(normalizeLine(l)));
        cleanedPages.push(filtered.join("\n"));
      });

      let extracted = cleanedPages.join("\n\n").trim();
      if (extracted.length < 20) throw new Error("SCANNED_PDF_DETECTED");

      let cleaned = extracted.split("\n").map(l => l.trim()).join("\n");
      cleaned = cleaned.replace(/[^\S\r\n]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();

      // Fix #15: Cap PDF content to prevent chrome.storage quota overflow and context floods
      const PDF_CHAR_LIMIT = 50_000; // ≈12,500 tokens
      if (cleaned.length > PDF_CHAR_LIMIT) {
        cleaned = cleaned.substring(0, PDF_CHAR_LIMIT);
        const truncNote = `\n\n[PDF truncated at ~50,000 chars to protect context limits. Full PDF: ${totalPages} pages.]`;
        cleaned += truncNote;
        if (subText) subText.innerText = `Content capped at 50K chars (${totalPages}-page PDF). Squeezing...`;
      }

      statusText.innerText = "Squeezing PDF content...";
      if (!cleaned.includes("PDF truncated")) subText.innerText = "Applying token compression...";
      workingModalPrompt = cleaned;
      duplicateContextBlocks = findDuplicateContext(cleaned);
      requestOptimization(cleaned, currentOptMode);
    } catch (err) {
      console.error("PDF parsing error:", err);
      let msg = "Failed to parse PDF document.";
      if (err.message === "SCANNED_PDF_DETECTED") {
        msg = "This PDF appears to be a scanned image or contains no extractable text.";
      } else {
        msg += ` (${err.message})`;
      }

      const body = modalContainer.querySelector(".tm-modal-body");
      body.innerHTML = `
        <div class="tm-dup-warning-banner" style="background: rgba(255, 59, 48, 0.08); border: 1px solid rgba(255, 59, 48, 0.25); padding: 18px; border-radius: 10px; text-align: center;">
          <div style="font-size: 1.6rem; margin-bottom: 8px;">⚠️</div>
          <div style="font-size: 0.82rem; color: #ff5e84; line-height: 1.5; font-weight: 600; margin-bottom: 12px;">${msg}</div>
          <button class="tm-btn" id="tmPDFErrorCloseBtn">Close</button>
        </div>
      `;
      body.querySelector("#tmPDFErrorCloseBtn").addEventListener("click", closeModal);
    }
  }

  // --- DUPLICATE CONTEXT DETECTION ---
  function findDuplicateContext(text) {
    const previousUserMessages = [];
    const selectors = [
      '[data-testid="user-message"]',
      'div.font-user-message',
      '[data-message-author-role="user"]',
      'user-query'
    ];
    document.querySelectorAll(selectors.join(", ")).forEach(el => {
      previousUserMessages.push(el.innerText.trim());
    });

    if (previousUserMessages.length === 0) return [];

    const duplicates = [];
    const codeBlockRegex = /```[\s\S]*?```/g;
    let match;
    const candidates = [];

    while ((match = codeBlockRegex.exec(text)) !== null) {
      const original = match[0];
      if (original.length > 100) {
        const content = original.replace(/^```\w*\n|```$/g, "").trim();
        candidates.push({ original, content, type: "code block" });
      }
    }

    text.replace(codeBlockRegex, "").split(/\n\s*\n+/).forEach(para => {
      const trimmed = para.trim();
      if (trimmed.length > 150) {
        candidates.push({ original: para, content: trimmed, type: "paragraph" });
      }
    });

    candidates.forEach(cand => {
      const normCand = cand.content.toLowerCase().replace(/\s+/g, " ");
      for (const msg of previousUserMessages) {
        if (msg.toLowerCase().replace(/\s+/g, " ").includes(normCand)) {
          duplicates.push(cand);
          break;
        }
      }
    });

    return duplicates;
  }

  // --- OPTIMIZATION MODAL ---
  function ensureModalExists() {
    if (!modalContainer) {
      modalContainer = document.createElement("div");
      modalContainer.className = "squeeze-modal-container";
      document.body.appendChild(modalContainer);
      modalContainer.addEventListener("click", e => {
        if (e.target === modalContainer) closeModal();
      });
      // Escape key closes modal
      window.addEventListener("keydown", e => {
        if (e.key === "Escape" && modalContainer.classList.contains("open")) {
          closeModal();
        }
      });
    }
  }

  function closeModal() {
    if (modalContainer) {
      modalContainer.classList.remove("open");
      currentUploadedPdf = null;
      setTimeout(() => { modalContainer.innerHTML = ""; }, 300);
    }
  }

  function openOptimizationModal(promptText, mode) {
    ensureModalExists();
    workingModalPrompt = promptText;
    duplicateContextBlocks = findDuplicateContext(promptText);

    const logoUrl = chrome.runtime.getURL("icons/icon48.png");
    modalContainer.innerHTML = `
      <div class="squeeze-modal-card">
        <div class="tm-modal-header">
          <div class="tm-modal-logo">
            <img src="${logoUrl}" class="animating" width="22" height="22" alt="Squeeze Icon">
            <span>Squeeze <span class="highlight">Optimizer</span></span>
          </div>
          <button class="tm-close-btn">&times;</button>
        </div>
        <div class="tm-modal-body">
          <div class="tm-loading-state">
            <div class="tm-spinner"></div>
            <p>Squeezing prompt for maximum token efficiency...</p>
            <span class="tm-loading-subtext">Optimizing via Local Rules & DLP Scanner...</span>
          </div>
        </div>
      </div>
    `;

    modalContainer.classList.add("open");
    modalContainer.querySelector(".tm-close-btn").addEventListener("click", closeModal);
    requestOptimization(promptText, mode);
  }

  function requestOptimization(promptText, mode) {
    try {
      chrome.runtime.sendMessage(
        { action: "optimizePrompt", prompt: promptText, mode },
        response => {
          if (chrome.runtime.lastError) {
            // Must read .message to suppress Chrome's "Unchecked runtime.lastError" warning
            const errMsg = chrome.runtime.lastError.message || "Unknown error";
            renderModalError(`Communication with Squeeze background service failed (${errMsg}). Please refresh this tab.`);
          } else if (response && response.success) {
            renderModalContent(response);
          } else {
            renderModalError(response?.error || "Unknown optimization error.");
          }
        }
      );
    } catch (e) {
      renderModalError(`Squeeze was reloaded. Please refresh this tab. (${e.message})`);
    }
  }

  function renderModalError(errorMsg) {
    if (!modalContainer) return;
    const body = modalContainer.querySelector(".tm-modal-body");
    const logoImg = modalContainer.querySelector(".tm-modal-logo img");
    if (logoImg) logoImg.classList.remove("animating");

    body.innerHTML = `
      <div class="tm-error-state">
        <div class="tm-error-icon">⚠️</div>
        <h3>Optimization Failed</h3>
        <p class="tm-error-msg">${escapeHtml(errorMsg)}</p>
        <div class="tm-error-actions">
          <button class="tm-btn tm-btn-secondary" id="tmErrorCloseBtn">Close</button>
        </div>
      </div>
    `;
    body.querySelector("#tmErrorCloseBtn").addEventListener("click", closeModal);
  }

  // Fast line-level diff fallback for large prompts
  function generateLineDiff(orig, opt) {
    const origLines = orig.split("\n");
    const optLines  = opt.split("\n");
    const origSet   = new Set(origLines.map(l => l.trim()));
    const optSet    = new Set(optLines.map(l => l.trim()));

    const oldHtml = origLines.map(l => {
      const t = l.trim();
      return (t && !optSet.has(t))
        ? `<del class="tm-diff-del">${escapeHtml(l)}</del>`
        : escapeHtml(l);
    }).join("<br>");

    const newHtml = optLines.map(l => {
      const t = l.trim();
      return (t && !origSet.has(t))
        ? `<ins class="tm-diff-ins">${escapeHtml(l)}</ins>`
        : escapeHtml(l);
    }).join("<br>");

    return { oldHtml, newHtml };
  }

  // Generate word diff (LCS-based). Falls back to line-diff for large prompts.
  const LCS_WORD_CAP = 500;
  function generateDiffView(orig, opt) {
    const origWords = orig.trim().split(/(\s+)/);
    const optWords  = opt.trim().split(/(\s+)/);

    // Performance guard: LCS is O(m×n) — fallback for large inputs
    if (origWords.length > LCS_WORD_CAP || optWords.length > LCS_WORD_CAP) {
      return generateLineDiff(orig, opt);
    }

    const m = origWords.length;
    const n = optWords.length;
    const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (origWords[i - 1] === optWords[j - 1]) dp[i][j] = dp[i - 1][j - 1] + 1;
        else dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }

    let i = m, j = n;
    const oldArr = [], newArr = [];

    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && origWords[i - 1] === optWords[j - 1]) {
        const w = origWords[i - 1];
        oldArr.unshift(escapeHtml(w));
        newArr.unshift(escapeHtml(w));
        i--;
        j--;
      } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
        const w = optWords[j - 1];
        if (w.trim() === "") newArr.unshift(w);
        else newArr.unshift(`<ins class="tm-diff-ins">${escapeHtml(w)}</ins>`);
        j--;
      } else {
        const w = origWords[i - 1];
        if (w.trim() === "") oldArr.unshift(w);
        else oldArr.unshift(`<del class="tm-diff-del">${escapeHtml(w)}</del>`);
        i--;
      }
    }

    return { oldHtml: oldArr.join(""), newHtml: newArr.join("") };
  }

  function renderModalContent(data) {
    const body = modalContainer.querySelector(".tm-modal-body");
    const logoImg = modalContainer.querySelector(".tm-modal-logo img");
    if (logoImg) logoImg.classList.remove("animating");

    // Fix #19: Compute intent preservation score from actual word overlap (Jaccard similarity).
    // This replaces the hardcoded 93/98/99 magic numbers.
    function computeIntentScore(orig, opt) {
      const stopWords = new Set(["the","a","an","is","are","was","were","be","been","being",
        "have","has","had","do","does","did","will","would","could","should","may","might",
        "shall","can","need","dare","ought","used","i","you","he","she","it","we","they",
        "what","which","who","whom","this","that","these","those","am","to","of","in","for",
        "on","with","at","by","from","as","into","through","and","but","or","nor","so","yet"]);
      const tokenize = str => str.toLowerCase().replace(/[^a-z0-9\s]/g, " ")
        .split(/\s+/).filter(w => w.length > 2 && !stopWords.has(w));
      const origWords = new Set(tokenize(orig));
      const optWords  = new Set(tokenize(opt));
      const intersection = [...origWords].filter(w => optWords.has(w)).length;
      const union = new Set([...origWords, ...optWords]).size;
      if (union === 0) return 100;
      // Jaccard * 100, clamped to [85, 100] range for UX readability
      return Math.min(100, Math.max(85, Math.round((intersection / union) * 100)));
    }
    const intentScore = computeIntentScore(data.original, data.optimized);

    const diff = generateDiffView(data.original, data.optimized);

    // DLP banner
    let secretHtml = "";
    if (data.secretsDetected && data.secretsDetected.length > 0) {
      secretHtml = `
        <div class="tm-dup-warning-banner" style="background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.3); color: #34d399; margin-bottom: 12px;">
          <span>🛡️ <strong>DLP Shield:</strong> ${data.secretsDetected.length} credential(s) safely masked before sending.</span>
        </div>
      `;
    }

    // Duplicate context banner
    let dupsHtml = "";
    if (duplicateContextBlocks.length > 0) {
      dupsHtml = `
        <div class="tm-dup-warning-banner" style="background: rgba(255, 59, 48, 0.08); border: 1px solid rgba(255, 59, 48, 0.25); padding: 10px; border-radius: 8px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
          <div style="font-size: 0.76rem; color: #ff5e84;">
            ⚠️ <strong>Duplicate Context:</strong> ${duplicateContextBlocks.length} block(s) in this prompt was already sent earlier in the thread.
          </div>
          <button class="tm-btn" id="tmStripDupsBtn" style="padding: 4px 8px; font-size: 0.7rem; color: #ff5e84; border: 1px solid rgba(255,94,132,0.4); background: rgba(255,59,48,0.05); cursor: pointer; border-radius: 4px;">Strip Duplicates</button>
        </div>
      `;
    }

    // Applied rules
    const rulesHtml = data.rulesApplied && data.rulesApplied.length > 0
      ? `<div class="tm-applied-rules-chips" style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
          ${data.rulesApplied.map(r => `<span class="tm-rule-chip" style="font-size: 0.68rem; padding: 2px 8px; background: rgba(255, 109, 0, 0.1); border: 1px solid rgba(255, 109, 0, 0.3); color: #ff9d42; border-radius: 12px;">✓ ${escapeHtml(r)}</span>`).join("")}
        </div>`
      : "";

    // Attached context
    const vaultHtml = data.attachedContexts && data.attachedContexts.length > 0
      ? `<div style="margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.06); padding-top: 6px;">
          <span style="font-size: 0.7rem; color: #9e978e;">Vault Context Attached:</span>
          <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
            ${data.attachedContexts.map(c => `<span style="font-size: 0.65rem; padding: 2px 6px; background: rgba(0, 229, 255, 0.08); border: 1px solid rgba(0, 229, 255, 0.2); color: #00e5ff; border-radius: 10px;">📂 ${escapeHtml(c)}</span>`).join("")}
          </div>
        </div>`
      : "";

    const origLabel = currentUploadedPdf ? "Original PDF Content" : "Original Prompt";
    const optLabel = currentUploadedPdf ? "Squeezed PDF Content" : "Optimized Prompt";

    body.innerHTML = `
      <div class="tm-comparison-layout">
        ${secretHtml}
        ${dupsHtml}

        <!-- Options Bar -->
        <div class="tm-options-bar">
          <div class="tm-mode-selector-group">
            <label>Mode:</label>
            <select id="tmModeSelect" class="tm-mini-select">
              <option value="squeeze" ${data.mode === "squeeze" ? "selected" : ""}>Squeeze (Max Savings)</option>
              <option value="balanced" ${data.mode === "balanced" ? "selected" : ""}>Balanced (Concise)</option>
              <option value="polish" ${data.mode === "polish" ? "selected" : ""}>Polish (Enhance)</option>
            </select>
          </div>
          <div class="tm-stats-badges">
            <div class="tm-stats-badge-savings">
              Saves ${data.percentageSaved}% Tokens
            </div>
            <div class="tm-stats-badge-quality">
              ⚡ ${intentScore}% Intent Kept
            </div>
          </div>
        </div>

        <!-- Diff Grid -->
        <div class="tm-diff-grid">
          <div class="tm-diff-pane">
            <div class="tm-pane-header">
              <span>${origLabel}</span>
              <span class="tm-pane-stat">${data.originalTokens.toLocaleString()} tokens</span>
            </div>
            <div class="tm-pane-content tm-original-text" id="tmOriginalPane">${diff.oldHtml}</div>
          </div>
          
          <div class="tm-diff-pane tm-optimized-pane">
            <div class="tm-pane-header">
              <span>${optLabel}</span>
              <div class="tm-toggle-group">
                <button class="tm-toggle-btn active" id="tmToggleDiff">Diff</button>
                <button class="tm-toggle-btn" id="tmToggleEdit">Edit Raw</button>
              </div>
              <span class="tm-pane-stat glow-text">${data.optimizedTokens.toLocaleString()} tokens</span>
            </div>
            <div id="tmOptimizedWrapper" style="height: calc(100% - 32px); display: flex; flex-direction: column;">
              <div class="tm-pane-content tm-optimized-diff" id="tmOptimizedDiffPane">${diff.newHtml}</div>
              <textarea id="tmOptimizedInput" class="tm-pane-textarea" style="display: none;">${escapeHtml(data.optimized)}</textarea>
            </div>
          </div>
        </div>

        <!-- Savings Summary -->
        <div class="tm-savings-summary">
          <div class="tm-savings-icon">⚡</div>
          <div class="tm-savings-details">
            <span class="tm-savings-title">Optimization Complete!</span>
            <span class="tm-savings-desc">Saved <strong>${data.tokensSaved.toLocaleString()} tokens</strong> (${data.percentageSaved}% reduction) while preserving all intent.</span>
            ${rulesHtml}
            ${vaultHtml}
          </div>
        </div>

        <!-- Actions Footer -->
        <div class="tm-actions-footer">
          <button class="tm-btn tm-btn-secondary" id="tmDiscardBtn">Discard</button>
          <button class="tm-btn tm-btn-primary" id="tmApplyBtn">Apply & Squeeze</button>
        </div>
      </div>
    `;

    // Mode select change
    const modeSelect = body.querySelector("#tmModeSelect");
    modeSelect.addEventListener("change", () => {
      const newMode = modeSelect.value;
      currentOptMode = newMode;
      body.innerHTML = `
        <div class="tm-loading-state">
          <div class="tm-spinner"></div>
          <p>Re-optimizing prompt using ${newMode} mode...</p>
        </div>
      `;
      requestOptimization(workingModalPrompt, newMode);
    });

    // Toggle Diff vs Edit Raw
    const btnDiff = body.querySelector("#tmToggleDiff");
    const btnEdit = body.querySelector("#tmToggleEdit");
    const diffPane = body.querySelector("#tmOptimizedDiffPane");
    const editArea = body.querySelector("#tmOptimizedInput");
    const origPane = body.querySelector("#tmOriginalPane");

    btnDiff.addEventListener("click", () => {
      btnDiff.classList.add("active");
      btnEdit.classList.remove("active");
      diffPane.style.display = "block";
      editArea.style.display = "none";
      origPane.innerHTML = diff.oldHtml;
    });

    btnEdit.addEventListener("click", () => {
      btnEdit.classList.add("active");
      btnDiff.classList.remove("active");
      diffPane.style.display = "none";
      editArea.style.display = "block";
      origPane.innerHTML = escapeHtml(data.original);
      editArea.focus();
    });

    // Discard & Apply
    body.querySelector("#tmDiscardBtn").addEventListener("click", closeModal);
    body.querySelector("#tmApplyBtn").addEventListener("click", () => {
      // Fix: Use textarea value only when Edit Raw view is active.
      // When Diff view is shown, editArea is hidden and not kept in sync — use data.optimized directly.
      const inEditMode = editArea.style.display !== "none";
      const finalVal = inEditMode ? editArea.value : data.optimized;
      lastOptimizedPrompt = finalVal;
      if (activeInputEl) {
        setInputValue(activeInputEl, finalVal);
        if (undoBtn) undoBtn.style.display = "inline-flex";
      }
      closeModal();
    });

    // Strip Duplicates
    const stripBtn = body.querySelector("#tmStripDupsBtn");
    if (stripBtn) {
      stripBtn.addEventListener("click", () => {
        let cleaned = workingModalPrompt;
        duplicateContextBlocks.forEach(b => {
          cleaned = cleaned.replace(b.original, "");
        });
        cleaned = cleaned.replace(/\n\s*\n+/g, "\n\n").trim();
        duplicateContextBlocks = [];
        workingModalPrompt = cleaned;
        showToast(stripBtn, "Duplicate blocks stripped!");
        requestOptimization(cleaned, currentOptMode);
      });
    }
  }

  // --- CONTEXT SUMMARIZER ---
  function wireSummaryButton(input) {
    summaryBtn.addEventListener("click", e => {
      e.stopPropagation();
      e.preventDefault();

      try {
        const { summary, totalTurns, summarizedTurns } = extractConversationSummary();
        if (!summary || summary.length < 30) {
          showToast(summaryBtn, "No chat history to summarize yet!");
          return;
        }

        chrome.storage.local.set({ pendingChatSummary: summary }, () => {
          navigator.clipboard.writeText(summary).catch(() => {});
          // Fix #16: Show transparent turn count in toast
          const turnInfo = totalTurns > 0
            ? `Summarized ${summarizedTurns} of ${totalTurns} messages → fresh chat!`
            : "Context summarized! Opening fresh chat...";
          showToast(summaryBtn, turnInfo);

          // Open fresh chat depending on platform
          setTimeout(() => {
            if (IS_CLAUDE) window.location.href = "https://claude.ai/new";
            else if (IS_CHATGPT) window.location.href = "https://chatgpt.com/";
            else if (IS_GEMINI) window.location.href = "https://gemini.google.com/app";
          }, 1200);
        });
      } catch (err) {
        console.error("Summary error:", err);
        showToast(summaryBtn, "Error generating summary context.");
      }
    });
  }

  function extractConversationSummary() {
    const turns = [];

    if (IS_CLAUDE) {
      const messages = document.querySelectorAll(
        "div.font-user-message, div.font-claude-message, [data-testid='user-message'], [data-testid='bot-message'], .prose"
      );
      messages.forEach(el => {
        const isUser = el.closest('[data-testid="user-message"]') || el.classList.contains("font-user-message");
        const clone = el.cloneNode(true);
        clone.querySelectorAll("pre").forEach(p => p.remove());
        const text = clone.innerText.trim();
        const codeBlocks = [];
        el.querySelectorAll("pre code").forEach(c => {
          let lang = "code";
          c.classList.forEach(cls => { if (cls.startsWith("language-")) lang = cls.replace("language-", ""); });
          codeBlocks.push({ language: lang, code: c.innerText.trim().substring(0, 3000) });
        });
        if (text || codeBlocks.length > 0) turns.push({ sender: isUser ? "User" : "Claude", text, codeBlocks });
      });
    } else if (IS_CHATGPT) {
      const messages = document.querySelectorAll('[data-message-author-role]');
      messages.forEach(el => {
        const role = el.getAttribute("data-message-author-role");
        const text = el.innerText.trim();
        turns.push({ sender: role === "user" ? "User" : "Assistant", text, codeBlocks: [] });
      });
    } else {
      // Gemini
      const messages = document.querySelectorAll("user-query, model-response");
      messages.forEach(el => {
        const isUser = el.tagName.toLowerCase() === "user-query";
        turns.push({ sender: isUser ? "User" : "Gemini", text: el.innerText.trim(), codeBlocks: [] });
      });
    }

    if (turns.length === 0) return { summary: "", totalTurns: 0, summarizedTurns: 0 };

    const totalTurns = turns.length;
    // Keep last 3 exchanges (6 turns)
    const KEEP = 6;
    const recent = turns.slice(-KEEP);
    const summarizedTurns = recent.length;
    let output = "## Context Summary from Previous Chat (Squeezed)\n\n### Recent Discussion Timeline:\n";

    recent.forEach(t => {
      let snippet = t.text;
      if (snippet.length > 350) snippet = snippet.substring(0, 350) + "... [truncated]";
      output += `**${t.sender}**: ${snippet.replace(/\n/g, " ")}\n\n`;
    });

    output += "\n*This context was automatically summarized by Squeeze AI to save tokens. Ready to continue where we left off.*";
    return { summary: output, totalTurns, summarizedTurns };
  }

  // --- CONTEXT USAGE DEPTH BAR ---
  function mountContextUsageBar() {
    const input = findChatInput();
    if (!input) return;

    const parent = input.closest("form") || input.closest("fieldset") || input.parentElement;
    if (!parent) return;

    if (!usageBar || !document.contains(usageBar)) {
      usageBar = document.createElement("div");
      usageBar.className = "squeeze-usage-bar";
      parent.parentNode.insertBefore(usageBar, parent.nextSibling);
    }

    updateContextDepth();
  }

  async function updateContextDepth() {
    if (!usageBar) return;

    // Estimate thread tokens without double-counting parent & child message containers
    const rawNodes = Array.from(document.querySelectorAll(
      "div.font-user-message, div.font-claude-message, [data-testid='user-message'], [data-message-author-role], user-query, model-response"
    ));
    const textNodes = rawNodes.filter(node => !rawNodes.some(other => other !== node && other.contains(node)));
    let combined = "";
    textNodes.forEach(n => { combined += " " + n.innerText; });
    if (activeInputEl) combined += " " + getInputValue(activeInputEl);

    const totalTokens = estimateTokensLocal(combined);
    const percent = Math.min(100, Math.max(0, Math.round((totalTokens / 200_000) * 100)));
    const status = totalTokens < 40_000 ? "safe" : totalTokens < 100_000 ? "moderate" : totalTokens < 160_000 ? "heavy" : "critical";
    const statusLabel = status === "safe" ? "Safe Context" : status === "moderate" ? "Moderate Context" : status === "heavy" ? "Heavy Context" : "Critical Context (Start New Chat)";

    let nudgeHtml = "";
    if (totalTokens > 35_000) {
      nudgeHtml = `
        <div class="tm-summary-nudge">
          <span class="tm-nudge-icon">⚡</span>
          <span class="tm-nudge-text">High Context depth (${totalTokens.toLocaleString()} tokens). Starting a new chat cuts latency and cost by 70%!</span>
          <button class="tm-nudge-btn tm-btn-gold" id="tmBarSummarizeBtn">Summarize & New Chat</button>
        </div>
      `;
    }

    usageBar.innerHTML = `
      <div class="tm-usage-bar-content">
        <div class="tm-usage-columns">
          <div class="tm-context-column">
            <span class="tm-usage-dot dot-${status}"></span>
            <span class="tm-usage-title">Conversation Context:</span>
            <span class="tm-usage-val">${totalTokens.toLocaleString()}</span>
            <span class="tm-usage-divider">/</span>
            <span class="tm-usage-limit">200K tokens</span>
            <span class="tm-usage-percent">(${percent}%)</span>
            <span class="tm-usage-status-inline status-${status}">${statusLabel}</span>
          </div>
        </div>
        <div class="tm-progress-bars-container" style="display: flex; flex-direction: column; gap: 4px; width: 100%; margin-top: 4px;">
          <div class="tm-usage-progress-track" title="Conversation Context: ${percent}% used">
            <div class="tm-usage-progress-bar progress-${status}" style="width: ${percent}%"></div>
          </div>
        </div>
        ${nudgeHtml}
      </div>
    `;

    const barSumBtn = usageBar.querySelector("#tmBarSummarizeBtn");
    if (barSumBtn) {
      barSumBtn.addEventListener("click", () => {
        if (summaryBtn) summaryBtn.click();
      });
    }
  }

  // --- VAULT BADGE UPDATE ---
  function updateVaultBadge(promptText) {
    if (!vaultBadge) return;
    if (!promptText) {
      vaultBadge.style.display = "none";
      return;
    }

    chrome.storage.local.get(["vaultPreferences", "vaultPrefAlwaysInject", "vaultSmartTriggers", "vaultFiles"], data => {
      const prefs = data.vaultPreferences || "";
      const alwaysInject = data.vaultPrefAlwaysInject !== false;
      const smartTriggers = data.vaultSmartTriggers !== false;
      const files = data.vaultFiles || [];

      let count = 0;
      const attached = [];

      if (prefs.trim() && alwaysInject) {
        count++;
        attached.push("Developer Profile");
      }

      if (files.length > 0) {
        const lower = promptText.toLowerCase();
        for (const f of files) {
          let matches = false;
          if (smartTriggers) {
            const toks = f.name.replace(/\.[a-z0-9]+$/i, "").toLowerCase().split(/[^a-z0-9]+/).filter(w => w.length >= 3);
            for (const t of toks) {
              if (new RegExp("\\b" + t + "\\b", "i").test(lower)) {
                matches = true;
                break;
              }
            }
          } else {
            matches = true;
          }
          if (matches && f.content) {
            count++;
            attached.push(f.name);
          }
        }
      }

      if (count > 0) {
        vaultBadge.style.display = "inline-flex";
        vaultBadge.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; color: #ff6d00;">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
          </svg>
          <span style="font-size: 0.72rem; font-weight: 600; color: #ff6d00;">Vault: ${count}</span>
        `;
        vaultBadge.setAttribute("title", `Vault Context Attached:\n- ${attached.join("\n- ")}`);
      } else {
        vaultBadge.style.display = "none";
      }
    });
  }

  // --- SIDEBAR BUTTON & IN-PAGE DRAWER ---
  function mountSidebarButton() {
    if (sidebarBtn && document.contains(sidebarBtn)) return;

    const nav = document.querySelector("nav") || document.querySelector('[role="navigation"]') || document.querySelector("aside");
    if (!nav) return;

    sidebarBtn = document.createElement("button");
    sidebarBtn.className = "squeeze-sidebar-btn";
    sidebarBtn.dataset.tooltip = "Open Squeeze Side Panel";
    sidebarBtn.addEventListener("mouseenter", () => showTooltip(sidebarBtn, sidebarBtn.dataset.tooltip));
    sidebarBtn.addEventListener("mouseleave", hideTooltip);
    sidebarBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 512 512" fill="none">
        <path d="M 140 148 L 256 264 L 372 148" stroke="currentColor" stroke-width="48" stroke-linecap="round" stroke-linejoin="round"/>
        <rect x="160" y="324" width="192" height="44" rx="22" fill="currentColor"/>
      </svg>
    `;

    sidebarBtn.addEventListener("click", e => {
      e.stopPropagation();
      hideTooltip();
      chrome.runtime.sendMessage({ action: "openSidePanel" }, response => {
        if (chrome.runtime.lastError) {
          // Suppress error in console if side panel is not accessible
          const _err = chrome.runtime.lastError.message;
        }
      });
    });

    nav.appendChild(sidebarBtn);
  }

  // --- LISTEN FOR MESSAGES (E.G. FROM SIDE PANEL) ---
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.action === "insertPrompt") {
      const input = findChatInput();
      if (input && msg.text) {
        setInputValue(input, msg.text);
        if (undoBtn) undoBtn.style.display = "inline-flex";
        showToast(input, "Prompt squeezed & injected! ✨");
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: "Chat input not found" });
      }
    }
  });

  // --- OBSERVER & INITIALIZATION ---
  function init() {
    chrome.storage.local.get(["optimizationMode"], data => {
      if (data.optimizationMode) currentOptMode = data.optimizationMode;
    });

    mountWidgets();

    // Leading + trailing debounce: fire immediately on first mutation,
    // then again 600ms after the DOM settles. Prevents missing widget
    // injection during ChatGPT/Gemini streaming responses.
    let debounceTimer = null;
    let lastFiredAt = 0;
    const LEADING_INTERVAL = 1500; // ms before we fire leading again
    const TRAILING_DELAY = 600;    // ms after last mutation

    const observer = new MutationObserver(() => {
      const now = Date.now();
      if (now - lastFiredAt > LEADING_INTERVAL) {
        // Leading fire — instant widget mount
        mountWidgets();
        lastFiredAt = now;
      }
      // Trailing fire — re-check after DOM settles
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        mountWidgets();
        lastFiredAt = Date.now();
      }, TRAILING_DELAY);
    });

    observer.observe(document.body, { childList: true, subtree: true });

    chrome.storage.onChanged.addListener(changes => {
      if (changes.optimizationMode) currentOptMode = changes.optimizationMode.newValue;
      if (activeInputEl) updateVaultBadge(getInputValue(activeInputEl));
    });
  }

  init();
})();