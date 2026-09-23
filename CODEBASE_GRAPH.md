# 🗺️ SQUEEZE CODEBASE TOPOLOGICAL GRAPH
- **Repository Path**: `/Users/aashu/Aashu/Squeeze`
- **Interactive Visualizer Generated**: `/Users/aashu/Aashu/Squeeze/codebase_graph.html` (Saved on disk! Double-click to open in browser & explore interactive node graph)
- **Markdown Knowledge Index**: `/Users/aashu/Aashu/Squeeze/CODEBASE_GRAPH.md`
- **Files Scanned**: 57 | **Total Symbols Indexed**: 1157
- **Raw Code Tokens**: ~205,451 | **Graph Tokens**: ~1,995
- **Token Compression**: ~99.0% savings (exploration cost eliminated)

### 🏛️ Core Architecture Hubs (Ranked by Centrality):
- **`aws/lambdas/log-processor/squeeze_core.py`** (Centrality: 3 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust]
- **`skeletonizer.js`** (Centrality: 1 imports)
  ↳ Classes: [annotations, closing] | Funcs: [skeletonizePython, lines, result, line, trimmed]
- **`squeeze_mcp.py`** (Centrality: 1 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data]
- **`website/app.js`** (Centrality: 1 imports)
  ↳ Funcs: [htmlEl, themeToggleBtn, themeIcon, moonIconPath, sunIconPath]
- **`aws/lambdas/codebase-indexer/squeeze_core.py`** (Centrality: 1 imports)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust]

### 📦 Full Module Symbol & Interface Map:
- `skeletonizer.js` (435 lines, ~3773 tokens)
  ↳ Classes: [annotations, closing] | Funcs: [skeletonizePython, lines, result, line, trimmed, indentMatch, indent, nextTrim, indentStr, skeletonizeTypeScript, open, close]
- `squeeze_mcp.py` (914 lines, ~11123 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_code, shrink_json_data, fold, shrink_logs_data, resolve_import_path, build_codebase_graph_html, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [sys, os, json, re]
- `popup.js` (336 lines, ~3238 tokens)
  ↳ Funcs: [tabButtons, tabPanes, statPrompts, statTokens, statCost, statusBadge, openSidePanelTopBtn, openSidePanelActionBtn, footerStudioLink, settingsForm, ruleSecretShield, ruleStripGreetings]
- `sidepanel.js` (928 lines, ~8947 tokens)
  ↳ Classes: [PaymentGateway, AuthenticationManager, SessionPayload] | Funcs: [navButtons, panes, inputPrompt, inputTokenBadge, charCount, clearInputBtn, modeButtons, toggleDlp, toggleVault, squeezeBtn, outputSection, secretAlertBanner] | Imports: [os, typing]
- `background.js` (859 lines, ~7328 tokens)
  ↳ Funcs: [MODEL_RATES, defaults, current, toSet, estimateTokens, trimmed, words, chars, specialChars, codeRatio, charEstimate, wordEstimate] | Imports: [skeletonizer.js]
- `uninstall.py` (79 lines, ~617 tokens)
  ↳ Funcs: [remove_from_json, main] | Imports: [sys, os, json, shutil]
- `install.py` (257 lines, ~2383 tokens)
  ↳ Funcs: [print_banner, get_script_dir, test_mcp_server, update_json_mcp_config, install_claude_code, install_claude_desktop, install_cursor, install_antigravity, main] | Imports: [sys, os, json, shutil]
- `content.js` (1323 lines, ~13146 tokens)
  ↳ Funcs: [HOST, IS_CLAUDE, IS_CHATGPT, IS_GEMINI, findChatInput, getInputValue, setInputValue, proto, nativeSetter, selection, range, execSuccess]
- `generate_feature_guide_pdf.py` (606 lines, ~7598 tokens)
  ↳ Classes: [NumberedCanvas, and, PaymentManager] | Funcs: [__init__, showPage, save, draw_page_decorations, build_pdf, process_payment] | Imports: [os, sys, reportlab.lib.pagesizes, reportlab.platypus]
- `test_suite.js` (157 lines, ~1819 tokens)
  ↳ Classes: [PaymentGateway, AuthenticationManager, decl, closing, Database, AuthManager, annotation, UserProfile] | Funcs: [fs, vm, assert, ctx, skelCode, pyInput, __init__, process_transaction, calculate_fee, pySkeleton, tsInput, auth] | Imports: [fs, vm, assert, os]
- `website/index.js` (360 lines, ~2887 tokens)
  ↳ Funcs: [initStickyNavbar, navbar, handleScroll, initWordRotator, rotatorEl, words, STAGGER, renderWordSpans, container, charSpan, nextIdx, currentWord]
- `website/app.js` (897 lines, ~7957 tokens)
  ↳ Funcs: [htmlEl, themeToggleBtn, themeIcon, moonIconPath, sunIconPath, setTheme, canvas, ctx, CELL_SIZE, INFLUENCE_RADIUS, MAX_WARP, DOT_SPACING]
- `aws/lambdas/log-processor/index.py` (229 lines, ~2264 tokens)
  ↳ Funcs: [emit_cloudwatch_metrics, invoke_bedrock_summarizer, lambda_handler] | Imports: [os, sys, json, gzip]
- `aws/lambdas/log-processor/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/lambdas/codebase-indexer/index.py` (119 lines, ~1011 tokens)
  ↳ Funcs: [download_and_extract_repo, lambda_handler] | Imports: [os, sys, json, shutil]
- `aws/lambdas/codebase-indexer/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/lambdas/dlp-verifier/index.py` (70 lines, ~651 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [os, sys, json, boto3]
- `aws/lambdas/dlp-verifier/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/lambdas/bedrock-action-handler/index.py` (181 lines, ~1701 tokens)
  ↳ Funcs: [emit_metrics, lambda_handler] | Imports: [json, os, sys, squeeze_core]
- `aws/lambdas/bedrock-action-handler/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/lambdas/noisy-logger/index.py` (49 lines, ~628 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [sys, time, uuid]
- `aws/cdk/bin/squeeze-app.ts` (52 lines, ~533 tokens)
  ↳ Funcs: [app, bedrockModelId, mcpBedrockStack, logPipelineStack, dashboardStack, devToolsStack] | Imports: [source-map-support/register]
- `aws/cdk/lib/squeeze-dev-tools-stack.ts` (142 lines, ~1411 tokens)
  ↳ Classes: [SqueezeDevToolsStack] | Funcs: [ciBuildProject, indexerFunction, indexerUrlResource, dlpVerifierFunction, dlpUrlResource] | Imports: [urllib.request]
- `aws/cdk/lib/squeeze-log-pipeline-stack.ts` (120 lines, ~1262 tokens)
  ↳ Classes: [SqueezeLogPipelineStack, SqueezeLogPipelineStackProps] | Funcs: [modelId, noisyLogGroup]
- `aws/cdk/lib/squeeze-dashboard-stack.ts` (143 lines, ~1138 tokens)
  ↳ Classes: [SqueezeDashboardStack] | Funcs: [dashboard, tokensBeforeMetric, tokensAfterMetric, tokensSavedMetric, costSavedMetric, secretsMaskedMetric, compressionRatioMetric]
- `aws/cdk/lib/squeeze-mcp-bedrock-stack.ts` (167 lines, ~1670 tokens)
  ↳ Classes: [SqueezeMcpBedrockStack, SqueezeMcpBedrockStackProps] | Funcs: [modelId, mcpFunction, fnUrl, actionGroupFunction, agentRole, schemaPath, openApiSchema, agent, agentAlias]
- `aws/cdk/cdk.out/asset.687ea3d7eb5d8cabddea98082a49acc148edcee403230563a840770b95284092/index.py` (175 lines, ~1678 tokens)
  ↳ Funcs: [emit_metrics, lambda_handler] | Imports: [json, os, sys, boto3]
- `aws/cdk/cdk.out/asset.687ea3d7eb5d8cabddea98082a49acc148edcee403230563a840770b95284092/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.5f881867aa123bca5dae14c42018fbcb5967c9572e762dab572874ed27058276/index.py` (119 lines, ~1011 tokens)
  ↳ Funcs: [download_and_extract_repo, lambda_handler] | Imports: [os, sys, json, shutil]
- `aws/cdk/cdk.out/asset.5f881867aa123bca5dae14c42018fbcb5967c9572e762dab572874ed27058276/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.faa95a81ae7d7373f3e1f242268f904eb748d8d0fdd306e8a6fe515a1905a7d6/index.js` (2 lines, ~1100 tokens)
  ↳ Funcs: [R, k, u, D, T, O, b, S, F, _, U, N] | Imports: [https, url]
- `aws/cdk/cdk.out/asset.fb7524e4bdfa49a7c0562cbda0a8fcb4382ae04921545c47005de6f6d6593dcf/index.py` (181 lines, ~1701 tokens)
  ↳ Funcs: [emit_metrics, lambda_handler] | Imports: [json, os, sys, squeeze_core]
- `aws/cdk/cdk.out/asset.fb7524e4bdfa49a7c0562cbda0a8fcb4382ae04921545c47005de6f6d6593dcf/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.81fdfd454df1b33db3e850aeb6c423df6be298d85a4ab7f85d63c99f76eb53c7/index.py` (49 lines, ~628 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [sys, time, uuid]
- `aws/cdk/cdk.out/asset.bc4ffbbca47c22f996253bf20885cc775eff2dd56315f240a0d49cb2ad455959/index.py` (119 lines, ~1011 tokens)
  ↳ Funcs: [download_and_extract_repo, lambda_handler] | Imports: [os, sys, json, shutil]
- `aws/cdk/cdk.out/asset.bc4ffbbca47c22f996253bf20885cc775eff2dd56315f240a0d49cb2ad455959/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.21663d0d6a5e6803837b4781d94cdb20d1034e67c34b7f4c17e192e288483d1f/index.py` (70 lines, ~651 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [os, sys, json, boto3]
- `aws/cdk/cdk.out/asset.21663d0d6a5e6803837b4781d94cdb20d1034e67c34b7f4c17e192e288483d1f/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.6732323ac764912c1126eb2a09ad4f297d4f7747e794397ac2a7b4169f7bd6c7/app.py` (463 lines, ~4599 tokens)
  ↳ Classes: [SqueezeHTTPRequestHandler] | Funcs: [handle_mcp_jsonrpc, handle_rest_request, lambda_handler, _send_json, do_OPTIONS, do_GET, do_POST, log_message, run_standalone] | Imports: [os, sys, json, time]
- `aws/cdk/cdk.out/asset.6732323ac764912c1126eb2a09ad4f297d4f7747e794397ac2a7b4169f7bd6c7/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.2bb8068f1633690dd140c3204e2d80eeb8f75444523681282b357b92b00610bb/index.py` (223 lines, ~2236 tokens)
  ↳ Funcs: [emit_cloudwatch_metrics, invoke_bedrock_summarizer, lambda_handler] | Imports: [os, sys, json, gzip]
- `aws/cdk/cdk.out/asset.2bb8068f1633690dd140c3204e2d80eeb8f75444523681282b357b92b00610bb/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.71b047216f66595e3f8565f28dc2f8d23141556e0f166053d4a48b80fcd2af7f/app.py` (463 lines, ~4599 tokens)
  ↳ Classes: [SqueezeHTTPRequestHandler] | Funcs: [handle_mcp_jsonrpc, handle_rest_request, lambda_handler, _send_json, do_OPTIONS, do_GET, do_POST, log_message, run_standalone] | Imports: [os, sys, json, time]
- `aws/cdk/cdk.out/asset.71b047216f66595e3f8565f28dc2f8d23141556e0f166053d4a48b80fcd2af7f/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.56c263d9e76312476cd8ca620fd191b4d2db9ee4537f33eff0658877dacb7124/index.py` (229 lines, ~2264 tokens)
  ↳ Funcs: [emit_cloudwatch_metrics, invoke_bedrock_summarizer, lambda_handler] | Imports: [os, sys, json, gzip]
- `aws/cdk/cdk.out/asset.56c263d9e76312476cd8ca620fd191b4d2db9ee4537f33eff0658877dacb7124/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/cdk/cdk.out/asset.dece92409bfe79ff340f4db9acc75cee7682bfb648c637ba67e53695a6b7f061/index.py` (70 lines, ~651 tokens)
  ↳ Funcs: [lambda_handler] | Imports: [os, sys, json, boto3]
- `aws/cdk/cdk.out/asset.dece92409bfe79ff340f4db9acc75cee7682bfb648c637ba67e53695a6b7f061/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/ci/triage_build_failure.py` (80 lines, ~698 tokens)
  ↳ Funcs: [main] | Imports: [os, sys, json, argparse]
- `aws/mcp-server/app.py` (463 lines, ~4599 tokens)
  ↳ Classes: [SqueezeHTTPRequestHandler] | Funcs: [handle_mcp_jsonrpc, handle_rest_request, lambda_handler, _send_json, do_OPTIONS, do_GET, do_POST, log_message, run_standalone] | Imports: [os, sys, json, time]
- `aws/mcp-server/squeeze_core.py` (600 lines, ~5819 tokens)
  ↳ Funcs: [mask_secrets, skeletonize_python, skeletonize_typescript, skeletonize_go, skeletonize_rust, skeletonize_code, shrink_json_data, _shrink, shrink_logs_data, generate_codebase_graph, align_prompt_for_cache, optimize_prompt] | Imports: [ranks., os, sys, json]
- `aws/demo-data/sample_repo_snippet.py` (68 lines, ~681 tokens)
  ↳ Classes: [OrderValidationError, PaymentGatewayError, OrderItem, OrderProcessor] | Funcs: [__init__, total, validate_order, calculate_tax_and_discounts, authorize_payment, settle_and_dispatch] | Imports: [os, sys, json, logging]
- `aws/scripts/simulate_demo_traffic.py` (111 lines, ~1229 tokens)
  ↳ Funcs: [simulate_traffic] | Imports: [os, sys, time, random]
- `aws/scripts/test_bedrock_agent.py` (104 lines, ~1036 tokens)
  ↳ Funcs: [invoke_agent] | Imports: [os, sys, json, uuid]
- `aws/scripts/test_local_engine.py` (162 lines, ~1773 tokens)
  ↳ Classes: [TestSqueezeAIEngine, OrderProcessor] | Funcs: [setUp, test_01_shrink_logs, test_02_shrink_json, test_03_skeletonize_code, test_04_dlp_secret_shield, test_05_reversible_chunks, test_06_codebase_graph, test_07_bedrock_action_group_event, test_08_mcp_lambda_function_url] | Imports: [os, sys, json, unittest]
- `assets/05_squeezed_code_skeleton.py` (80 lines, ~850 tokens)
  ↳ Classes: [PaymentGatewayException, InventoryExhaustedException, FraudDetectionAlert, LineItem, OrderHeader, FraudAssessmentEngine, InventoryReservationManager, PaymentRailClient] | Funcs: [compute_subtotal_cents, is_eligible_for_free_shipping, total_cents, __init__, inspect_request, reserve_skus, release_reservation, authorize_charge, capture_charge, execute_order_pipeline] | Imports: [os, sys, time, json]
- `assets/04_big_code_chunk_500lines.py` (224 lines, ~2072 tokens)
  ↳ Classes: [PaymentGatewayException, InventoryExhaustedException, FraudDetectionAlert, LineItem, OrderHeader, FraudAssessmentEngine, InventoryReservationManager, PaymentRailClient] | Funcs: [compute_subtotal_cents, is_eligible_for_free_shipping, total_cents, __init__, inspect_request, reserve_skus, release_reservation, authorize_charge, capture_charge, execute_order_pipeline] | Imports: [os, sys, time, json]