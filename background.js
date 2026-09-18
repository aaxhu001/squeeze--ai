/**
 * Squeeze AI - Background Service Worker (Manifest V3)
 * High-performance local token optimizer, DLP secret scanner,
 * Squeeze AST Code Skeletonizer, CacheAligner & Context Vault engine.
 */

try {
  importScripts("skeletonizer.js");
} catch (e) {
  console.warn("Could not import skeletonizer.js:", e);
}

// --- MODEL PRICING (USD per 1M input tokens) ---
const MODEL_RATES = {
  sonnet: { name: "Claude 3.5 Sonnet", ratePerMillion: 3.00 },
  opus: { name: "Claude 3 Opus", ratePerMillion: 15.00 },
  gpt4o: { name: "GPT-4o", ratePerMillion: 2.50 },
  geminiPro: { name: "Gemini 1.5 Pro", ratePerMillion: 1.25 },
  deepseek: { name: "DeepSeek V3", ratePerMillion: 0.14 }
};

// --- INITIALIZE EXTENSION DEFAULTS ---
chrome.runtime.onInstalled.addListener(async (details) => {
  const defaults = {
    optimizationMode: "balanced",
    ruleStripGreetings: true,
    ruleSimplifyPhrases: true,
    ruleAbbreviate: true,
    ruleStripArticles: true,
    rulePolishMarkdown: true,
    ruleSecretShield: true,
    stats_promptsOptimized: 0,
    stats_tokensSaved: 0,
    stats_costSaved: 0,
    stats_history: [],
    vaultPreferences: "",
    vaultPrefAlwaysInject: true,
    vaultSmartTriggers: true,
    vaultFiles: []
  };

  const current = await chrome.storage.local.get(Object.keys(defaults));
  const toSet = {};
  for (const [k, v] of Object.entries(defaults)) {
    if (current[k] === undefined) toSet[k] = v;
  }
  if (Object.keys(toSet).length > 0) {
    await chrome.storage.local.set(toSet);
  }

  // Set side panel behavior if supported
  if (chrome.sidePanel?.setPanelBehavior) {
    try {
      await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
    } catch (e) {
      console.warn("Side panel behavior setup:", e);
    }
  }
});

// --- TOKEN ESTIMATION ENGINE ---
// NOTE: This is the canonical implementation. Identical copies exist in
// content.js (estimateTokensLocal) and sidepanel.js for context isolation
// (content scripts and side panels can't share service worker scope).
// TODO: Extract to a shared bundle once a build pipeline is added.
function estimateTokens(text) {
  if (!text || typeof text !== "string") return 0;
  const trimmed = text.trim();
  if (!trimmed) return 0;

  // Words count
  const words = trimmed.split(/\s+/).length;
  const chars = trimmed.length;

  // Code / Symbol intensity factor
  const specialChars = (trimmed.match(/[{}\[\]()<>=:;,.!?"'`\/\\|#*&^%$@~+-]/g) || []).length;
  const codeRatio = specialChars / Math.max(1, chars);

  // Heuristic: standard prose ~4 chars/token, code-heavy ~3 chars/token
  const charEstimate = Math.ceil(chars / (codeRatio > 0.15 ? 3.2 : 4.0));
  const wordEstimate = Math.ceil(words * 1.35);

  return Math.max(charEstimate, wordEstimate);
}

// --- DATA LOSS PREVENTION (DLP) & SECRET REDACTION ENGINE ---
function maskSensitiveData(text) {
  if (!text) return { sanitized: "", secretsFound: [] };

  let sanitized = text;
  const secretsFound = [];

  const patterns = [
    {
      type: "OpenAI API Key",
      regex: /\b(sk-(?:proj-|live-)?[a-zA-Z0-9_-]{20,})\b/g,
      replacement: "[MASKED_OPENAI_KEY]"
    },
    {
      type: "Google AI / Gemini Key",
      regex: /\b(AIzaSy[a-zA-Z0-9_-]{30,})\b/g,
      replacement: "[MASKED_GOOGLE_KEY]"
    },
    {
      type: "Anthropic Claude Key",
      regex: /\b(sk-ant-[a-zA-Z0-9_-]{20,})\b/g,
      replacement: "[MASKED_ANTHROPIC_KEY]"
    },
    {
      type: "AWS Access Key",
      regex: /\b(AKIA[0-9A-Z]{16})\b/g,
      replacement: "[MASKED_AWS_KEY]"
    },
    {
      type: "GitHub Token",
      regex: /\b(gh[pousr]_[A-Za-z0-9_]{36,})\b/g,
      replacement: "[MASKED_GITHUB_TOKEN]"
    },
    {
      type: "JWT / Bearer Token",
      regex: /\b(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b/g,
      replacement: "[MASKED_JWT_TOKEN]"
    },
    {
      type: "Database Password / URI",
      regex: /((?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql):\/\/[^:\s]+:)([^@\s]+)(@)/gi,
      customReplace: (match, prefix, pass, suffix) => `${prefix}[MASKED_DB_PASS]${suffix}`
    },
    {
      type: "Secret in Config",
      regex: /\b((?:API_KEY|SECRET|PASSWORD|PASSWD|AUTH_TOKEN|PRIVATE_KEY)\s*[:=]\s*["'])([^"'\n]{4,})(["'])/gi,
      customReplace: (match, prefix, val, suffix) => `${prefix}[MASKED_SECRET]${suffix}`
    }
  ];

  for (const item of patterns) {
    // Fix: always reset lastIndex before using global regexes to avoid
    // the stateful bug where .test() advances lastIndex and .replace() skips matches.
    item.regex.lastIndex = 0;

    if (item.customReplace) {
      item.regex.lastIndex = 0;
      const testCopy = new RegExp(item.regex.source, item.regex.flags);
      if (testCopy.test(sanitized)) {
        item.regex.lastIndex = 0;
        sanitized = sanitized.replace(item.regex, (match, p1, p2, p3) => {
          secretsFound.push({ type: item.type, snippet: match.substring(0, 15) + "..." });
          return item.customReplace(match, p1, p2, p3);
        });
      }
    } else {
      item.regex.lastIndex = 0;
      const allMatches = [...sanitized.matchAll(item.regex)];
      if (allMatches.length > 0) {
        allMatches.forEach(m => {
          secretsFound.push({ type: item.type, snippet: m[0].substring(0, 8) + "..." });
        });
        item.regex.lastIndex = 0;
        sanitized = sanitized.replace(item.regex, item.replacement);
      }
    }
  }

  return { sanitized, secretsFound };
}

// --- DUPLICATE SENTENCE & PARAGRAPH DETECTOR ---
function removeDuplicateSentences(text, rulesApplied) {
  if (!text) return "";
  const sentences = text.match(/[^.!?]+(?:[.!?]+|\s*$)/g) || [text];
  const seen = new Set();
  const result = [];
  let hasDupes = false;

  for (const s of sentences) {
    const trimmed = s.trim();
    if (!trimmed) continue;
    // Normalized key
    const key = trimmed.toLowerCase().replace(/[^a-z0-9]/g, "");
    if (key.length > 15 && seen.has(key)) {
      hasDupes = true;
    } else {
      if (key.length > 15) seen.add(key);
      result.push(s);
    }
  }

  if (hasDupes && rulesApplied && !rulesApplied.includes("Duplicate sentence removal")) {
    rulesApplied.push("Duplicate sentence removal");
  }

  return result.join(" ").replace(/\s{2,}/g, " ").trim();
}

// --- LOCAL HEURISTIC OPTIMIZATION ENGINE ---
function optimizeLocally(text, mode = "balanced", rules = {}) {
  if (!text) return { optimized: "", rulesApplied: [] };

  const rulesApplied = [];
  const placeholders = [];
  let counter = 0;

  // Protect code blocks, inline code, URLs, and HTML tags from regex corruption
  let processed = text.replace(
    /(```[\s\S]*?```|`[^`\n]+`|<[^>]+>|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|https?:\/\/[^\s]+)/g,
    (match) => {
      const ph = `__SQUEEZE_PLACEHOLDER_${counter}__`;
      placeholders.push({ placeholder: ph, original: match });
      counter++;
      return ph;
    }
  );

  // 1. Remove duplicate sentences
  if (rules.ruleSimplifyPhrases) {
    processed = removeDuplicateSentences(processed, rulesApplied);
  }

  // 2. Meta-commentary & Preamble Removal
  if (rules.ruleStripGreetings) {
    let changed = false;
    const metaPatterns = [
      /\b(?:just\s+to\s+clarify|as\s+stated\s+previously|mind\s+you|bear\s+in\s+mind\s+that|it's\s+worth\s+noting\s+that|to\s+be\s+clear|note\s+that|needless\s+to\s+say)\b[.,!?]*\s*/gi,
      /\b(?:so\s+)?as\s+i\s+(?:mentioned|stated)(?:\s+(?:above|earlier|previously|before))?\b[.,!?]*\s*/gi,
      /\b(?:as\s+we\s+discussed|just\s+to\s+recap\s+our\s+discussion|recap\s+our\s+discussion)\b(?:\s+(?:earlier\s+in\s+the\s+thread|above|previously|before))?[.,!?]*\s*/gi
    ];
    metaPatterns.forEach(p => {
      if (p.test(processed)) {
        processed = processed.replace(p, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Meta-commentary removal");
  }

  // 3. Redundant Qualifiers Stripping
  if (rules.ruleSimplifyPhrases) {
    let changed = false;
    const qualifiers = [
      /\b(?:please\s+)?make\s+sure\s+that\s+you\b\s*/gi,
      /\bi\s+need\s+you\s+to\b\s*/gi,
      /\bi\s+want\s+you\s+to\b\s*/gi,
      /\bit\s+is\s+important\s+(?:that|to)\s+you\b\s*/gi,
      /\bbe\s+sure\s+to\b\s*/gi,
      /\bensure\s+that\s+you\b\s*/gi,
      /\bgo\s+ahead\s+and\b\s*/gi,
      /\bkindly\s+(?:provide|generate|give|write)\b\s*/gi,
      /\bi\s+was\s+hoping\s+you\s+could\b\s*/gi
    ];
    qualifiers.forEach(regex => {
      if (regex.test(processed)) {
        processed = processed.replace(regex, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Redundant qualifier stripping");
  }

  // 4. Role-play Preamble Compaction
  if (rules.ruleStripGreetings) {
    const roleRegex = /\bact\s+as\s+(?:if\s+you\s+were\s+)?(?:though\s+you\s+were\s+)?(?:a\s+|an\s+)?(?:the\s+)?(?:expert\s+|professional\s+|senior\s+|experienced\s+)?([\w\s-]+?)(?:\s+with\s+\d+\s+years\s+of\s+experience|\s+with\s+experience)?\s*([.,!?]|$)/gi;
    if (roleRegex.test(processed)) {
      processed = processed.replace(roleRegex, (m, role, punct) => `Act as ${role.trim()}${punct || "."}`);
      rulesApplied.push("Role-play preamble compaction");
    }
  }

  // 5. Politeness & Greetings Removal
  if (rules.ruleStripGreetings) {
    let changed = false;
    const politenessPatterns = [
      { regex: /\b(?:thank\s+you|thanks)(?:\s+for\s+[^.!?]+)?(?:\s*,\s*it\s+was\s+[^.!?]+)?[.!?]+\s*/gi },
      { regex: /\b(?:thank\s+you|thanks)\s*,\s*(?:that\s+worked|that\s+works\s+(?:great|well)?)[.!?]+\s*/gi },
      { regex: /\b(?:awesome|great|cool|perfect)\s*,\s*that\s+works\s+(?:great|well|perfectly)?[.!?]+\s*/gi },
      { regex: /\bthanks\s+in\s+advance[.,!?]*\s*/gi },
      { regex: /\bi\s+would\s+(?:really\s+)?appreciate\s+it\s+if\s+you\s+could\b\s*/gi },
      { regex: /\blet\s+me\s+know\s+if\s+you\s+have\s+(?:any\s+)?questions[.,!?]*\s*/gi },
      { regex: /\blet\s+me\s+know\s+what\s+you\s+think[.,!?]*\s*/gi },
      { regex: /\bhope\s+you\s+are\s+doing\s+well[.,!?]*\s*/gi },
      { regex: /\bhope\s+this\s+helps[.,!?]*\s*/gi },
      { regex: /\bbest\s+regards|regards|sincerely|yours\s+truly\b[.,!?]*\s*/gi },
      { regex: /(?:hello|hi|hey|greetings|dear|good\s+(?:morning|afternoon|evening))\s+(?:claude|chatgpt|assistant|ai|there|sir|madam|team|friend|buddy)\b[.,!?]*\s*/gi },
      { regex: /\b(?:could|can|would)\s+you\s+please\s+(?:help\s+me\s+(?:to\s+)?)?/gi },
      { regex: /\b(?:could|can|would)\s+you\s+(?:help\s+me\s+(?:to\s+)?)?/gi },
      { regex: /\b(?:i\s+would\s+like\s+you\s+to|i\s+want\s+you\s+to|i\s+need\s+you\s+to|i'm\s+looking\s+for\s+a|i\s+was\s+wondering\s+if\s+you\s+could)\b\s*/gi },
      { regex: /(?:^|([.!?]\s+))please\b\s*/gi, replaceWith: "$1" },
      { regex: /\bplease\s+(?:write|create|generate|make|help|explain|do|find|check|tell|give|show|list|analyze|sort|provide)\b/gi },
      { regex: /,\s*please[.,!?]*(?=\s|$)/gi },
      { regex: /\bthank\s+you\b[.,!?]*\s*/gi },
      { regex: /\bthanks\b[.,!?]*\s*/gi }
    ];

    politenessPatterns.forEach(item => {
      if (item.regex.test(processed)) {
        processed = item.replaceWith !== undefined
          ? processed.replace(item.regex, item.replaceWith)
          : processed.replace(item.regex, "");
        changed = true;
      }
    });
    if (changed) rulesApplied.push("Politeness padding removal");
  }

  // 6. Verbosity Simplification (Comprehensive dictionary)
  if (rules.ruleSimplifyPhrases) {
    const dictionary = {
      "in order to": "to",
      "due to the fact that": "because",
      "at this point in time": "now",
      "for the purpose of": "to",
      "has the ability to": "can",
      "take into consideration": "consider",
      "make a decision": "decide",
      "utilize": "use",
      "utilizes": "uses",
      "utilizing": "using",
      "as well as": "and",
      "a number of": "several",
      "along the lines of": "like",
      "referred to as": "called",
      "in the event that": "if",
      "on a daily basis": "daily",
      "with respect to": "regarding",
      "in addition to": "and",
      "so as to": "to",
      "is responsible for": "does",
      "by means of": "by",
      "in close proximity to": "near",
      "make use of": "use",
      "perform an analysis of": "analyze",
      "provide an explanation of": "explain",
      "conduct an investigation into": "investigate",
      "has a requirement for": "needs",
      "it is important to note that": "note that",
      "bearing in mind that": "considering",
      "for the reason that": "because",
      "in the near future": "soon",
      "in the course of": "during",
      "with the exception of": "except",
      "are in agreement": "agree",
      "make adjustments to": "adjust",
      "give rise to": "cause",
      "draw attention to": "highlight",
      "at the present time": "currently",
      "subsequent to": "after",
      "prior to": "before",
      "take steps to": "try to",
      "despite the fact that": "although",
      "as a consequence of": "because of",
      "at an early date": "soon",
      "by virtue of": "because of",
      "give consideration to": "consider",
      "in spite of": "despite"
    };

    let changed = false;
    for (const [verbose, concise] of Object.entries(dictionary)) {
      const reg = new RegExp(`\\b${verbose}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, concise);
        changed = true;
      }
    }
    if (changed) rulesApplied.push("Verbosity simplification");
  }

  // 7. Technical Abbreviation Substitution
  if (rules.ruleAbbreviate) {
    let abbrevs = {
      "information": "info",
      "database": "DB",
      "function": "fn",
      "parameter": "param",
      "parameters": "params",
      "configuration": "config",
      "administrator": "admin",
      "development": "dev",
      "application": "app",
      "applications": "apps",
      "for example": "e.g.",
      "that is": "i.e.",
      "versus": "vs",
      "approximately": "~",
      "without": "w/o",
      "with": "w/",
      "number": "num",
      "numbers": "nums",
      "between": "betw",
      "through": "thru",
      "standard": "std",
      "environment": "env",
      "temporary": "temp",
      "documentation": "docs",
      "difference": "diff",
      "developer": "dev",
      "developers": "devs",
      "repository": "repo",
      "repositories": "repos",
      "directory": "dir",
      "directories": "dirs",
      "implementation": "impl",
      "implementations": "impls"
    };

    // Conservative abbreviation in balanced/polish mode
    if (mode === "balanced" || mode === "polish") {
      abbrevs = {
        "for example": "e.g.",
        "that is": "i.e.",
        "versus": "vs",
        "approximately": "~",
        "documentation": "docs",
        "configuration": "config",
        "repository": "repo"
      };
    }

    let changed = false;
    for (const [full, abbr] of Object.entries(abbrevs)) {
      const reg = new RegExp(`\\b${full}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, abbr);
        changed = true;
      }
    }
    if (changed) rulesApplied.push("Abbreviation substitution");
  }

  // 8. Article & Auxiliary Stripping (Squeeze / Extreme Mode)
  if (rules.ruleStripArticles && mode === "squeeze") {
    const auxiliaries = {
      "should make a request to": "request",
      "should make a request": "request",
      "make a request to": "request",
      "is going to be": "will be",
      "should be": "be",
      "ought to": "should",
      "will be able to": "can",
      "it is necessary that": "must",
      "you can": "can",
      "we can": "can"
    };

    let changed = false;
    for (const [k, v] of Object.entries(auxiliaries)) {
      const reg = new RegExp(`\\b${k}\\b`, "gi");
      if (reg.test(processed)) {
        processed = processed.replace(reg, v);
        changed = true;
      }
    }

    const articles = /\b(?:the|a|an)\b\s+/gi;
    if (articles.test(processed)) {
      processed = processed.replace(articles, "");
      changed = true;
    }

    if (changed) rulesApplied.push("Article & auxiliary stripping");
  }

  // 9. Markdown & Whitespace Polish
  if (rules.rulePolishMarkdown) {
    let changed = false;
    // Clean excessive punctuation
    if (/!{2,}/.test(processed)) {
      processed = processed.replace(/!{2,}/g, "!");
      changed = true;
    }
    if (/\?{2,}/.test(processed)) {
      processed = processed.replace(/\?{2,}/g, "?");
      changed = true;
    }
    // Fix markdown headings: '#Heading' -> '# Heading'
    processed = processed.replace(/(^|\n)(#{1,6})([^\s#])([^\n]+)/g, "$1$2 $3$4");
    // Normalize bullet points to '- '
    processed = processed.replace(/(^|\n)[*+]\s+/g, "$1- ");
    // Remove multi-spaces and trailing spaces
    processed = processed.replace(/[ \t]{2,}/g, " ");
    processed = processed.replace(/^[ \t]+/gm, "").replace(/[ \t]+$/gm, "");
    // Collapse excessive blank lines (max 2)
    processed = processed.replace(/\n{3,}/g, "\n\n");

    if (changed) rulesApplied.push("Punctuation & spacing cleanup");
  }

  processed = processed.trim();

  // Restore protected blocks
  for (let i = 0; i < placeholders.length; i++) {
    const item = placeholders[i];
    processed = processed.replace(item.placeholder, item.original);
  }

  return { optimized: processed, rulesApplied };
}

// --- CONTEXT VAULT INJECTION ---
async function processVaultContext(prompt, mode, rules) {
  // chrome.storage.local.get returns a Promise in MV3
  const data = await chrome.storage.local.get([
    "vaultPreferences", "vaultPrefAlwaysInject", "vaultSmartTriggers",
    "vaultFiles", "vaultServerUrl", "vaultServerEnabled"
  ]);

  const prefs = data.vaultPreferences || "";
  const alwaysInject = data.vaultPrefAlwaysInject !== false;
  const smartTriggers = data.vaultSmartTriggers !== false;
  const files = data.vaultFiles || [];
  const attachedContexts = [];
  const contextParts = [];
  let rawTokens = 0;

  // 1. Personal Profile / Preferences
  if (prefs.trim() && alwaysInject) {
    rawTokens += estimateTokens(prefs);
    const optPrefs = optimizeLocally(prefs, "balanced", {
      ruleStripGreetings: true,
      ruleSimplifyPhrases: true,
      ruleAbbreviate: false,
      ruleStripArticles: false,
      rulePolishMarkdown: true
    }).optimized;
    contextParts.push(`[Developer Profile]\n${optPrefs}`);
    attachedContexts.push("Developer Profile");
  }

  // 2. Local Files matching keywords
  if (files.length > 0) {
    const lowerPrompt = prompt.toLowerCase();
    for (const f of files) {
      let matches = false;
      if (smartTriggers) {
        const baseTokens = f.name
          .replace(/\.[a-z0-9]+$/i, "")
          .toLowerCase()
          .split(/[^a-z0-9]+/)
          .filter(w => w.length >= 3 || ["db", "js", "ts", "go", "py", "sql", "api", "auth"].includes(w));

        for (const tok of baseTokens) {
          if (new RegExp("\\b" + tok + "\\b", "i").test(lowerPrompt)) {
            matches = true;
            break;
          }
        }
      } else {
        matches = true;
      }

      if (matches && f.content) {
        rawTokens += estimateTokens(f.content);
        let contentToProcess = f.content;
        const ext = f.name.split(".").pop().toLowerCase();

        // 🚀 Squeeze Code & Data Intelligence:
        // Automatically skeletonize code and fold JSON arrays to save 70-90% tokens!
        let labelSuffix = "";
        if (typeof skeletonizeCode === "function" && ["py", "ts", "tsx", "js", "jsx", "go", "rs"].includes(ext)) {
          contentToProcess = skeletonizeCode(f.content, f.name);
          labelSuffix = " (Squeeze Skeleton)";
        } else if (typeof shrinkJson === "function" && ext === "json") {
          contentToProcess = shrinkJson(f.content, 2);
          labelSuffix = " (Squeeze Shrunk)";
        }

        const optFile = optimizeLocally(maskSensitiveData(contentToProcess).sanitized, mode, rules).optimized;
        contextParts.push(`[Context: ${f.name}${labelSuffix}]\n${optFile}`);
        attachedContexts.push(`${f.name}${labelSuffix ? " [Condensed]" : ""}`);
      }
    }
  }

  let contextBlock = "";
  if (contextParts.length > 0) {
    contextBlock = `=== SQUEEZED CONTEXT VAULT ===\n${contextParts.join("\n\n")}\n==============================\n\n`;
  }

  return { contextBlock, attachedContexts, rawContextTokens: rawTokens };
}

// --- MESSAGE DISPATCHER ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "optimizePrompt") {
    (async () => {
      const { prompt, mode: requestedMode } = request;
      const settings = await chrome.storage.local.get([
        "optimizationMode",
        "ruleStripGreetings",
        "ruleSimplifyPhrases",
        "ruleAbbreviate",
        "ruleStripArticles",
        "rulePolishMarkdown",
        "ruleSecretShield"
      ]);

      const mode = requestedMode || settings.optimizationMode || "balanced";
      const rules = {
        ruleStripGreetings: settings.ruleStripGreetings !== false,
        ruleSimplifyPhrases: settings.ruleSimplifyPhrases !== false,
        ruleAbbreviate: settings.ruleAbbreviate !== false,
        ruleStripArticles: settings.ruleStripArticles !== false,
        rulePolishMarkdown: settings.rulePolishMarkdown !== false
      };

      try {
        // 1. DLP Secret Scan & Redaction
        let workingPrompt = prompt;
        let secretsDetected = [];
        if (settings.ruleSecretShield !== false) {
          const dlp = maskSensitiveData(prompt);
          workingPrompt = dlp.sanitized;
          secretsDetected = dlp.secretsFound;
        }

        // 2. Vault Context Attachment
        const { contextBlock, attachedContexts, rawContextTokens } = await processVaultContext(
          workingPrompt,
          mode,
          rules
        );

        // 3. Local Compression
        const { optimized, rulesApplied } = optimizeLocally(workingPrompt, mode, rules);
        const finalOptimized = contextBlock + optimized;

        // 4. Token & Cost Accounting
        const originalTokens = estimateTokens(prompt) + rawContextTokens;
        const optimizedTokens = estimateTokens(finalOptimized);
        const tokensSaved = Math.max(0, originalTokens - optimizedTokens);
        const percentageSaved = originalTokens > 0 ? Math.round((tokensSaved / originalTokens) * 100) : 0;

        // Multi-model savings calculation
        const costSavings = {};
        for (const [key, model] of Object.entries(MODEL_RATES)) {
          costSavings[key] = {
            name: model.name,
            savedDollars: (tokensSaved / 1_000_000) * model.ratePerMillion
          };
        }

        const sonnetSavings = costSavings.sonnet.savedDollars;

        // 5. Update Cumulative Stats & History
        const currentStats = await chrome.storage.local.get([
          "stats_promptsOptimized",
          "stats_tokensSaved",
          "stats_costSaved",
          "stats_history"
        ]);

        const history = currentStats.stats_history || [];
        history.unshift({
          timestamp: Date.now(),
          originalLength: prompt.length,
          tokensSaved,
          percentageSaved,
          mode,
          snippet: prompt.substring(0, 60).replace(/\n/g, " ") + (prompt.length > 60 ? "..." : "")
        });

        // Keep last 15 history entries (splice is safe even if > 1 extra entry)
        if (history.length > 15) history.splice(15);

        await chrome.storage.local.set({
          stats_promptsOptimized: (currentStats.stats_promptsOptimized || 0) + 1,
          stats_tokensSaved: (currentStats.stats_tokensSaved || 0) + tokensSaved,
          stats_costSaved: (currentStats.stats_costSaved || 0) + sonnetSavings,
          stats_history: history
        });

        sendResponse({
          success: true,
          original: prompt,
          optimized: finalOptimized,
          originalTokens,
          optimizedTokens,
          tokensSaved,
          percentageSaved,
          mode,
          rulesApplied,
          attachedContexts,
          secretsDetected,
          costSavings
        });
      } catch (err) {
        console.error("Optimization error:", err);
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true; // Keep message channel open for async response
  }

  if (request.action === "openSidePanel") {
    (async () => {
      try {
        let windowId = sender.tab?.windowId;
        if (!windowId) {
          const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
          windowId = activeTab?.windowId;
        }
        if (chrome.sidePanel?.open && windowId) {
          await chrome.sidePanel.open({ windowId });
          sendResponse({ success: true });
        } else {
          sendResponse({ success: false, error: "Side Panel API unavailable" });
        }
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "getStats") {
    (async () => {
      const stats = await chrome.storage.local.get([
        "stats_promptsOptimized",
        "stats_tokensSaved",
        "stats_costSaved",
        "stats_history"
      ]);
      sendResponse({ success: true, stats });
    })();
    return true;
  }

  if (request.action === "resetStats") {
    (async () => {
      await chrome.storage.local.set({
        stats_promptsOptimized: 0,
        stats_tokensSaved: 0,
        stats_costSaved: 0,
        stats_history: []
      });
      sendResponse({ success: true });
    })();
    return true;
  }

  if (request.action === "checkBuiltInAI") {
    (async () => {
      const hasAI = typeof globalThis.ai !== "undefined" && typeof globalThis.ai.languageModel !== "undefined";
      sendResponse({ success: true, hasBuiltInAI: hasAI });
    })();
    return true;
  }

  // --- SQUEEZE CODE & CACHE ACTIONS ---
  if (request.action === "skeletonizeCode") {
    (async () => {
      try {
        const { code, language } = request;
        const skeleton = typeof skeletonizeCode === "function"
          ? skeletonizeCode(code, language)
          : code;
        const origTokens = estimateTokens(code);
        const skelTokens = estimateTokens(skeleton);
        sendResponse({
          success: true,
          skeleton,
          originalTokens: origTokens,
          skeletonTokens: skelTokens,
          tokensSaved: Math.max(0, origTokens - skelTokens)
        });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "shrinkJson") {
    (async () => {
      try {
        const { jsonText, maxItems } = request;
        const shrunk = typeof shrinkJson === "function"
          ? shrinkJson(jsonText, maxItems || 2)
          : jsonText;
        const origTokens = estimateTokens(jsonText);
        const shrunkTokens = estimateTokens(shrunk);
        sendResponse({
          success: true,
          shrunk,
          originalTokens: origTokens,
          shrunkTokens,
          tokensSaved: Math.max(0, origTokens - shrunkTokens)
        });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "shrinkLogs") {
    (async () => {
      try {
        const { logText } = request;
        const shrunk = typeof shrinkLogs === "function"
          ? shrinkLogs(logText)
          : logText;
        sendResponse({ success: true, shrunk });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "getCodeGraph") {
    (async () => {
      try {
        const data = await chrome.storage.local.get(["vaultFiles"]);
        const files = data.vaultFiles || [];
        const graph = typeof buildCodebaseGraph === "function"
          ? buildCodebaseGraph(files)
          : { graphText: "Graph engine unavailable", nodes: [] };
        sendResponse({ success: true, graph });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }

  if (request.action === "alignCache") {
    (async () => {
      try {
        const { systemPrompt, context, query } = request;
        const aligned = typeof alignPromptForCache === "function"
          ? alignPromptForCache(systemPrompt, context, query)
          : `${systemPrompt}\n\n${context}\n\n${query}`;
        sendResponse({ success: true, aligned });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }
});