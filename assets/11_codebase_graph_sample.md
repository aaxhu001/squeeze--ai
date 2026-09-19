# 🗺️ SQUEEZE CODEBASE TOPOLOGICAL GRAPH
- **Repository Path**: `/Users/aashu/Aashu/Squeeze`
- **Files Scanned**: 25 | **Total Symbols Indexed**: 1531
- **Raw Code Tokens**: ~462,929 | **Graph Tokens**: ~875
- **Token Compression**: ~99.8% savings (exploration cost eliminated)

### 🏛️ Core Architecture Hubs (Ranked by Centrality):
- **`skeletonizer.js`** (Centrality: 1 imports)
  ↳ Classes: [annotations] | Funcs: [signatures, skeletonizePython, body, body, body]
- **`aws/lambdas/log-processor/squeeze_core.py`** (Centrality: 1 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go]
- **`aws/lambdas/codebase-indexer/squeeze_core.py`** (Centrality: 1 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go]
- **`aws/lambdas/dlp-verifier/squeeze_core.py`** (Centrality: 1 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go]
- **`squeeze_mcp.py`** (Centrality: 0 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data]

### 📦 Full Module Symbol & Interface Map:
- `skeletonizer.js` (434 lines, ~3773 tokens)
  ↳ Classes: [annotations] | Funcs: [signatures, skeletonizePython, body, body, body, skeletonizeTypeScript, skeletonizeCode, shrinkJson]
- `squeeze_mcp.py` (770 lines, ~7476 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data, fold, shrink_logs_data, generate_codebase_graph] | Imports: [sys, os, json, re]
- `pdf.worker.min.js` (22 lines, ~271795 tokens)
  ↳ Classes: [WorkerTask, WorkerMessageHandler, PasswordException, UnknownErrorException, InvalidPDFException] | Funcs: [webpackUniversalModuleDefinition, ensureNotTerminated, startWorkerTask, finishWorkerTask, loadDocument, getPdfManager, setupDoc, onSuccess] | Imports: [actual, a, worker]
- `popup.js` (336 lines, ~3238 tokens)
  ↳ Funcs: [launchSidePanel, formatNumber, formatBytes, escapeHtml, loadDashboardData, updateArticleStripState, processUploadedFiles, renderVaultFiles]
- `sidepanel.js` (927 lines, ~8947 tokens)
  ↳ Classes: [PaymentGateway, AuthenticationManager] | Funcs: [switchTab, estimateTokensLocal, updateInputMetrics, generateLineDiffHtml, generateDiffHtml, escapeHtml, executeOptimization, renderOutput] | Imports: [os, typing, List]
- `background.js` (859 lines, ~7328 tokens)
  ↳ Funcs: [estimateTokens, maskSensitiveData, removeDuplicateSentences, optimizeLocally, processVaultContext] | Imports: [skeletonizer.js, regex]
- `pdf.min.js` (22 lines, ~79997 tokens)
  ↳ Classes: [PasswordException, UnknownErrorException, InvalidPDFException, MissingPDFException, UnexpectedResponseException] | Funcs: [webpackUniversalModuleDefinition, assert, createValidAbsoluteUrl, _isValidProtocol, getModificationDate, getUuid, getVerbosityLevel, info] | Imports: [worker, bottom, top]
- `uninstall.py` (78 lines, ~617 tokens)
  ↳ Funcs: [remove_from_json, main] | Imports: [Claude, sys, os, json]
- `install.py` (256 lines, ~2383 tokens)
  ↳ Funcs: [print_banner, get_script_dir, test_mcp_server, update_json_mcp_config, install_claude_code, install_claude_desktop, install_cursor, install_antigravity] | Imports: [sys, os, json, shutil]
- `content.js` (1323 lines, ~13146 tokens)
  ↳ Funcs: [findChatInput, getInputValue, setInputValue, findToolbarAnchor, estimateTokensLocal, escapeHtml, showTooltip, hideTooltip] | Imports: [previous, previous, PDF..., actual]
- `generate_feature_guide_pdf.py` (605 lines, ~7598 tokens)
  ↳ Classes: [NumberedCanvas, and, PaymentManager, PaymentManager] | Funcs: [__init__, showPage, save, draw_page_decorations, build_pdf, names, names, process_payment] | Imports: [os, sys, reportlab.lib.pagesizes, letter]
- `test_suite.js` (148 lines, ~1657 tokens)
  ↳ Classes: [PaymentGateway, annotation, AuthenticationManager, AuthenticationManager, decl] | Funcs: [__init__, process_transaction, calculate_fee, process_transaction, start, verify] | Imports: [os, auth, verify]
- `website/index.js` (359 lines, ~2887 tokens)
  ↳ Funcs: [initStickyNavbar, initWordRotator, renderWordSpans, initScrollReveal, initStatsCounter, initFaqAccordion, initInstallGuideTabs, initCopyButtons]
- `website/app.js` (896 lines, ~7957 tokens)
  ↳ Funcs: [setTheme, lerpN, lerpColor, getWarpedPoint, renderCanvas, updateSectionPositions, optimizeSandboxPrompt, updateCalculator]
- `PERSONAL_GUIDES_AND_DOCS/build_deep_feature_guide_pdf.py` (718 lines, ~11700 tokens)
  ↳ Classes: [MasterCanvas, declarations, annotations, DatabaseClient, DatabaseClient] | Funcs: [__init__, showPage, save, draw_decorations, create_deep_guide_pdf, bodies, relations, bodies] | Imports: [sys, reportlab.lib.pagesizes, letter, reportlab.lib]
- `PERSONAL_GUIDES_AND_DOCS/generate_pitch_pdf.py` (581 lines, ~8419 tokens)
  ↳ Classes: [NumberedCanvas, signatures, signatures, live] | Funcs: [__init__, showPage, save, draw_page_decorations, build_pdf, bodies] | Imports: [sys, reportlab.lib.pagesizes, letter, reportlab.lib]
- `PERSONAL_GUIDES_AND_DOCS/test_optimizer.js` (96 lines, ~956 tokens)
  ↳ Funcs: [and, inOrderToRun, inOrderToRun]
- `PERSONAL_GUIDES_AND_DOCS/generate_review_pack.py` (45 lines, ~502 tokens)
  ↳ Funcs: [generate_pack] | Imports: [os]
- `PERSONAL_GUIDES_AND_DOCS/test_code_cache_engine.js` (130 lines, ~1164 tokens)
  ↳ Classes: [DatabaseClient, AuthService] | Funcs: [__init__, execute_query, standalone_helper] | Imports: [os, sys, typing, List]
- `aws/lambdas/log-processor/index.py` (228 lines, ~2264 tokens)
  ↳ Funcs: [emit_cloudwatch_metrics, invoke_bedrock_summarizer, lambda_handler] | Imports: [os, sys, json, gzip]
- `aws/lambdas/log-processor/squeeze_core.py` (599 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go, bodies, skeletonize_rust, implementations] | Imports: [ranks., os, sys, json]
- `aws/lambdas/codebase-indexer/index.py` (118 lines, ~1011 tokens)
  ↳ Funcs: [download_and_extract_repo, lambda_handler] | Imports: [os, sys, json, shutil]
- `aws/lambdas/codebase-indexer/squeeze_core.py` (599 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go, bodies, skeletonize_rust, implementations] | Imports: [ranks., os, sys, json]
- `aws/lambdas/dlp-verifier/index.py` (69 lines, ~651 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [os, sys, json, boto3]
- `aws/lambdas/dlp-verifier/squeeze_core.py` (599 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, bodies, skeletonize_go, bodies, skeletonize_rust, implementations] | Imports: [ranks., os, sys, json]