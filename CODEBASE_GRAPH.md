# 🗺️ SQUEEZE CODEBASE TOPOLOGICAL GRAPH
- **Repository Path**: `/Users/aashu/Aashu/Squeeze`
- **Files Scanned**: 11 | **Total Symbols Indexed**: 148
- **Raw Code Tokens**: ~59,411 | **Graph Tokens**: ~385
- **Token Compression**: ~99.4% savings (exploration cost eliminated)

### 🏛️ Core Architecture Hubs (Ranked by Centrality):
- **`skeletonizer.js`** (Centrality: 1 imports)
  ↳ Classes: [annotations, closing] | Funcs: [signatures, skeletonizePython, body, skeletonizeTypeScript, skeletonizeCode]
- **`squeeze_mcp.py`** (Centrality: 0 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data]
- **`popup.js`** (Centrality: 0 imports)
  ↳ Funcs: [launchSidePanel, formatNumber, formatBytes, escapeHtml, loadDashboardData]
- **`sidepanel.js`** (Centrality: 0 imports)
  ↳ Classes: [PaymentGateway, AuthenticationManager, SessionPayload] | Funcs: [switchTab, estimateTokensLocal, updateInputMetrics, generateLineDiffHtml, generateDiffHtml]
- **`background.js`** (Centrality: 0 imports)
  ↳ Funcs: [estimateTokens, maskSensitiveData, removeDuplicateSentences, optimizeLocally, processVaultContext]

### 📦 Full Module Symbol & Interface Map:
- `skeletonizer.js` (435 lines, ~3773 tokens)
  ↳ Classes: [annotations, closing] | Funcs: [signatures, skeletonizePython, body, skeletonizeTypeScript, skeletonizeCode, shrinkJson, traverse, shrinkLogs, buildCodebaseGraph, alignPromptForCache]
- `squeeze_mcp.py` (771 lines, ~7476 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data, fold, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt, handle_message, main] | Imports: [sys, os, json, re]
- `popup.js` (336 lines, ~3238 tokens)
  ↳ Funcs: [launchSidePanel, formatNumber, formatBytes, escapeHtml, loadDashboardData, updateArticleStripState, processUploadedFiles, renderVaultFiles]
- `sidepanel.js` (928 lines, ~8947 tokens)
  ↳ Classes: [PaymentGateway, AuthenticationManager, SessionPayload] | Funcs: [switchTab, estimateTokensLocal, updateInputMetrics, generateLineDiffHtml, generateDiffHtml, escapeHtml, executeOptimization, renderOutput, in, loadAndRunDemo, and, processBatch] | Imports: [os, typing]
- `background.js` (859 lines, ~7328 tokens)
  ↳ Funcs: [estimateTokens, maskSensitiveData, removeDuplicateSentences, optimizeLocally, processVaultContext] | Imports: [skeletonizer.js]
- `uninstall.py` (79 lines, ~617 tokens)
  ↳ Funcs: [remove_from_json, main] | Imports: [sys, os, json, shutil]
- `install.py` (257 lines, ~2383 tokens)
  ↳ Funcs: [print_banner, get_script_dir, test_mcp_server, update_json_mcp_config, install_claude_code, install_claude_desktop, install_cursor, install_antigravity, main] | Imports: [sys, os, json, shutil]
- `content.js` (1323 lines, ~13146 tokens)
  ↳ Funcs: [findChatInput, getInputValue, setInputValue, findToolbarAnchor, estimateTokensLocal, escapeHtml, showTooltip, hideTooltip, showToast, mountWidgets, makeAccessibleBtn, wireInputEvents]
- `test_suite.js` (149 lines, ~1657 tokens)
  ↳ Classes: [PaymentGateway, AuthenticationManager, decl, closing, Database, AuthManager, annotation, UserProfile] | Funcs: [__init__, process_transaction, calculate_fee, start, verify] | Imports: [fs, vm, assert, os]
- `website/index.js` (360 lines, ~2887 tokens)
  ↳ Funcs: [initStickyNavbar, initWordRotator, renderWordSpans, initScrollReveal, initStatsCounter, initFaqAccordion, initInstallGuideTabs, initCopyButtons, initBlurFadeText, processNode, initTextRoll]
- `website/app.js` (897 lines, ~7957 tokens)
  ↳ Funcs: [setTheme, lerpN, lerpColor, getWarpedPoint, renderCanvas, updateSectionPositions, optimizeSandboxPrompt, updateCalculator, openWaitlist, closeWaitlist, showError, setSubmittingState]
