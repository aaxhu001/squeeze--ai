/**
 * Squeeze AI - Graphify & Headroom Intelligence Engine
 * 
 * 1. Graphify: Deterministic Code Skeletonizer & Topological Code Graph
 * 2. Headroom: Content-Aware Shrinkers (JSON, Logs, Diffs) & Provider CacheAligner
 */

(function (exports) {
  // --- 1. CODE SKELETONIZER (GRAPHIFY CORE) ---
  // Strips implementation bodies while preserving classes, function signatures,
  // docstrings, type annotations, and exported interfaces. Slashes 70-90% of tokens.

  function skeletonizePython(code) {
    if (!code) return "";
    const lines = code.split("\n");
    const result = [];
    let inDocstring = false;
    let docstringDelim = "";
    let skipBodyIndent = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      const indentMatch = line.match(/^(\s*)/);
      const indent = indentMatch ? indentMatch[1].length : 0;

      // Check docstring state
      if (!inDocstring) {
        if (trimmed.startsWith('"""') || trimmed.startsWith("'''")) {
          docstringDelim = trimmed.substring(0, 3);
          if (trimmed.length > 3 && trimmed.endsWith(docstringDelim)) {
            // One-line docstring
            result.push(line);
            continue;
          }
          inDocstring = true;
          result.push(line);
          continue;
        }
      } else {
        result.push(line);
        if (trimmed.endsWith(docstringDelim)) {
          inDocstring = false;
        }
        continue;
      }

      // Check if we are skipping an indented function body
      if (skipBodyIndent !== null) {
        if (indent > skipBodyIndent && trimmed !== "") {
          // Inside function body - skip
          continue;
        } else if (trimmed === "") {
          continue;
        } else {
          // Exited function body
          skipBodyIndent = null;
        }
      }

      // Imports, decorators, classes, comments
      if (
        trimmed.startsWith("import ") ||
        trimmed.startsWith("from ") ||
        trimmed.startsWith("@") ||
        trimmed.startsWith("#") ||
        trimmed.startsWith("class ") ||
        trimmed.startsWith("type ") ||
        trimmed.includes(" = TypeVar(") ||
        trimmed.includes(" = NewType(")
      ) {
        result.push(line);
        continue;
      }

      // Function definition
      if (trimmed.startsWith("def ") || trimmed.startsWith("async def ")) {
        // Collect full signature if multi-line
        let sig = line;
        while (!sig.includes(":") && i + 1 < lines.length) {
          i++;
          sig += "\n" + lines[i];
        }
        result.push(sig);

        // Check if next line is a docstring
        let hasDocstring = false;
        if (i + 1 < lines.length) {
          const nextTrim = lines[i + 1].trim();
          if (nextTrim.startsWith('"""') || nextTrim.startsWith("'''")) {
            hasDocstring = true;
          }
        }

        if (!hasDocstring) {
          // Add standard Python placeholder
          const indentStr = " ".repeat(indent + 4);
          result.push(`${indentStr}...`);
        }
        skipBodyIndent = indent;
        continue;
      }

      // Keep top-level constants / global variables
      if (indent === 0 && trimmed.includes("=") && !trimmed.startsWith("if ") && !trimmed.startsWith("for ")) {
        result.push(line);
      }
    }

    return result.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function skeletonizeTypeScript(code) {
    if (!code) return "";
    const lines = code.split("\n");
    const result = [];
    let braceDepth = 0;
    let inFunctionBody = false;
    let funcBraceStart = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Keep imports, exports, types, interfaces, and decorators
      if (
        trimmed.startsWith("import ") ||
        trimmed.startsWith("export type ") ||
        trimmed.startsWith("export interface ") ||
        trimmed.startsWith("type ") ||
        trimmed.startsWith("interface ") ||
        trimmed.startsWith("@")
      ) {
        result.push(line);
        // Track braces inside interfaces/types
        const open = (line.match(/{/g) || []).length;
        const close = (line.match(/}/g) || []).length;
        braceDepth += (open - close);
        continue;
      }

      // Detect function or method signatures
      const isFunction =
        /^(export\s+)?(async\s+)?function\b/.test(trimmed) ||
        /^(public|private|protected|static|override|async|\s)*[a-zA-Z0-9_$]+\s*\([^)]*\)\s*(:\s*[^={]+)?\s*\{?$/.test(trimmed) ||
        /^(export\s+)?(const|let|var)\s+[a-zA-Z0-9_$]+\s*=\s*(async\s*)?\([^)]*\)\s*(:\s*[^={]+)?\s*=>\s*\{?$/.test(trimmed);

      const isClassDecl = /^(export\s+)?(abstract\s+)?class\b/.test(trimmed);

      if (isClassDecl) {
        result.push(line);
        const open = (line.match(/{/g) || []).length;
        const close = (line.match(/}/g) || []).length;
        braceDepth += (open - close);
        continue;
      }

      if (isFunction && !inFunctionBody) {
        let sig = line;
        // Collect multi-line signature
        while (!sig.includes("{") && !sig.endsWith(";") && i + 1 < lines.length) {
          i++;
          sig += "\n" + lines[i];
        }

        const indentMatch = line.match(/^(\s*)/);
        const indentStr = indentMatch ? indentMatch[1] : "";

        if (sig.includes("{")) {
          // Replace opening brace with collapsed body
          const sigClean = sig.substring(0, sig.indexOf("{")).trim();
          result.push(`${indentStr}${sigClean} { /* ... */ }`);
          inFunctionBody = true;
          funcBraceStart = braceDepth;
          braceDepth += (sig.match(/{/g) || []).length - (sig.match(/}/g) || []).length;
          if (braceDepth <= funcBraceStart) {
            inFunctionBody = false;
          }
        } else {
          result.push(sig);
        }
        continue;
      }

      const openBraces = (line.match(/{/g) || []).length;
      const closeBraces = (line.match(/}/g) || []).length;

      if (inFunctionBody) {
        braceDepth += (openBraces - closeBraces);
        if (braceDepth <= funcBraceStart) {
          inFunctionBody = false;
        }
        continue;
      }

      // If at top level or class level, keep property definitions
      if (braceDepth <= 1 && (trimmed.includes(":") || trimmed.includes(";")) && !trimmed.startsWith("return ") && !trimmed.startsWith("const ") && !trimmed.startsWith("let ")) {
        result.push(line);
      }

      braceDepth += (openBraces - closeBraces);
      if (braceDepth < 0) braceDepth = 0;
    }

    return result.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }

  function skeletonizeCode(code, filenameOrLang = "") {
    const lower = (filenameOrLang || "").toLowerCase();
    if (lower.endsWith(".py") || lower === "python" || lower === "py") {
      return skeletonizePython(code);
    }
    if (
      lower.endsWith(".ts") || lower.endsWith(".tsx") ||
      lower.endsWith(".js") || lower.endsWith(".jsx") ||
      lower === "typescript" || lower === "javascript" || lower === "ts" || lower === "js"
    ) {
      return skeletonizeTypeScript(code);
    }

    // Generic fallback: collapse blocks inside { ... } beyond first line
    return code
      .replace(/\{([^{}]{60,})\}/g, "{\n  /* ... implementation details omitted ... */\n}")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  // --- 2. CONTENT-AWARE SHRINKERS (HEADROOM CORE) ---

  // JSON Array Folder & Schema Extractor:
  // Condenses 100 repetitive items down to 1 item + item count notation
  function shrinkJson(jsonText, maxArrayItems = 2) {
    if (!jsonText || typeof jsonText !== "string") return jsonText;
    try {
      const parsed = JSON.parse(jsonText);

      function traverse(obj) {
        if (Array.isArray(obj)) {
          if (obj.length > maxArrayItems) {
            const count = obj.length;
            const kept = obj.slice(0, maxArrayItems).map(traverse);
            kept.push({
              _squeezed_array_note: `... [${count - maxArrayItems} additional similar items omitted for token efficiency]`,
              total_count: count
            });
            return kept;
          }
          return obj.map(traverse);
        } else if (obj !== null && typeof obj === "object") {
          const result = {};
          for (const [k, v] of Object.entries(obj)) {
            // Truncate huge base64 strings or long hashes
            if (typeof v === "string" && v.length > 250 && !v.includes(" ")) {
              result[k] = v.substring(0, 40) + `... [truncated string, length ${v.length}]`;
            } else {
              result[k] = traverse(v);
            }
          }
          return result;
        }
        return obj;
      }

      const shrunk = traverse(parsed);
      return JSON.stringify(shrunk, null, 2);
    } catch (e) {
      // Not valid JSON, return as-is
      return jsonText;
    }
  }

  // Log & Stack Trace Deduplicator
  function shrinkLogs(logText) {
    if (!logText) return "";
    const lines = logText.split("\n");
    const result = [];
    let prevLine = "";
    let repeatCount = 0;

    for (const line of lines) {
      // Strip noisy timestamps like 2026-09-19T01:23:45.678Z
      const cleanLine = line
        .replace(/\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?Z?/g, "[TIME]")
        .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, "[UUID]");

      if (cleanLine === prevLine) {
        repeatCount++;
      } else {
        if (repeatCount > 0) {
          result.push(`   ↳ [Previous line repeated ${repeatCount} additional times]`);
          repeatCount = 0;
        }
        result.push(cleanLine);
        prevLine = cleanLine;
      }
    }

    if (repeatCount > 0) {
      result.push(`   ↳ [Previous line repeated ${repeatCount} additional times]`);
    }

    return result.join("\n");
  }

  // --- 3. TOPOLOGICAL CODE GRAPH (GRAPHIFY CORE) ---
  // Maps multi-file relationships, exports, classes, and dependencies into a compact map
  function buildCodebaseGraph(filesList) {
    if (!filesList || filesList.length === 0) return { graphText: "", nodes: [] };

    const nodes = [];
    const relationships = [];

    for (const file of filesList) {
      const name = file.name;
      const content = file.content || "";
      const ext = name.split(".").pop().toLowerCase();

      const imports = [];
      const exportsList = [];
      const classes = [];
      const functions = [];

      // Extract imports
      const importMatches = content.matchAll(/(?:import\s+.*?from\s+['"]([^'"]+)['"]|from\s+([a-zA-Z0-9_.]+)\s+import|require\(['"]([^'"]+)['"]\))/g);
      for (const m of importMatches) {
        const target = m[1] || m[2] || m[3];
        if (target && !imports.includes(target)) imports.push(target);
      }

      // Extract classes
      const classMatches = content.matchAll(/\bclass\s+([a-zA-Z0-9_$]+)/g);
      for (const m of classMatches) {
        if (!classes.includes(m[1])) classes.push(m[1]);
      }

      // Extract functions
      const funcMatches = content.matchAll(/\b(?:def|function|const)\s+([a-zA-Z0-9_$]+)\s*(?:=\s*(?:async\s*)?\([^)]*\)|=|\()/g);
      for (const m of funcMatches) {
        const fn = m[1];
        if (!["if", "for", "while", "switch"].includes(fn) && !functions.includes(fn)) {
          functions.push(fn);
        }
      }

      nodes.push({
        file: name,
        ext,
        classes: classes.slice(0, 8),
        functions: functions.slice(0, 12),
        imports: imports.slice(0, 8)
      });
    }

    // Format into compact graph summary
    let graphText = "### CODEBASE TOPOLOGICAL GRAPH (Graphify Engine)\n";
    nodes.forEach(n => {
      const parts = [];
      if (n.classes.length > 0) parts.push(`Classes: [${n.classes.join(", ")}]`);
      if (n.functions.length > 0) parts.push(`Functions: [${n.functions.join(", ")}]`);
      if (n.imports.length > 0) parts.push(`Imports: [${n.imports.join(", ")}]`);
      graphText += `- **${n.file}**: ${parts.join(" | ") || "Module definitions"}\n`;
    });

    return { graphText, nodes };
  }

  // --- 4. PROVIDER CACHE ALIGNER (HEADROOM CORE) ---
  // Reorders prompt content into [Tier 1: Static Prefix] -> [Tier 2: Code Skeletons] -> [Tier 3: Dynamic Tail]
  // to maximize Anthropic Claude & OpenAI 90% prompt-cache hit rates.
  function alignPromptForCache(systemPrompt, architectureContext, userTask) {
    const parts = [];

    // Tier 1: Static Cacheable Prefix (Developer Persona + Global Directives)
    if (systemPrompt && systemPrompt.trim()) {
      parts.push(`<!-- CACHE_ANCHOR: SYSTEM_DIRECTIVES -->\n${systemPrompt.trim()}`);
    }

    // Tier 2: Semi-Static Context (Architectural Code Graph & Skeletons)
    if (architectureContext && architectureContext.trim()) {
      parts.push(`<!-- CACHE_ANCHOR: CODE_ARCHITECTURE -->\n${architectureContext.trim()}`);
    }

    // Tier 3: Dynamic Tail (The immediate user query / volatile payload)
    if (userTask && userTask.trim()) {
      parts.push(`<!-- DYNAMIC_PROMPT: ACTIVE_QUERY -->\n${userTask.trim()}`);
    }

    return parts.join("\n\n");
  }

  // Exports
  exports.skeletonizePython = skeletonizePython;
  exports.skeletonizeTypeScript = skeletonizeTypeScript;
  exports.skeletonizeCode = skeletonizeCode;
  exports.shrinkJson = shrinkJson;
  exports.shrinkLogs = shrinkLogs;
  exports.buildCodebaseGraph = buildCodebaseGraph;
  exports.alignPromptForCache = alignPromptForCache;

})(typeof module !== "undefined" && module.exports ? module.exports : (window.SqueezeSkeletonizer = {}));
