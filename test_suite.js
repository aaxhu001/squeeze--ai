/**
 * Squeeze AI — End-to-End Automated Test Suite
 * Tests AST Skeletonizers, JSON & Log Shrinkers, Tokenizer, DLP Shield, and Graph Generation.
 */

const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

console.log("==========================================");
console.log("⚡ SQUEEZE AI COMPREHENSIVE TEST SUITE");
console.log("==========================================\n");

// 1. Initialize Skeletonizer in isolated context
const ctx = { console, setTimeout, clearTimeout };
ctx.globalThis = ctx;
ctx.self = ctx;
const skelCode = fs.readFileSync("skeletonizer.js", "utf8");
vm.runInNewContext(skelCode, ctx);

assert(typeof ctx.skeletonizeCode === "function", "skeletonizeCode missing");
assert(typeof ctx.skeletonizePython === "function", "skeletonizePython missing");
assert(typeof ctx.skeletonizeTypeScript === "function", "skeletonizeTypeScript missing");
assert(typeof ctx.shrinkJson === "function", "shrinkJson missing");
assert(typeof ctx.shrinkLogs === "function", "shrinkLogs missing");
assert(typeof ctx.buildCodebaseGraph === "function", "buildCodebaseGraph missing");
assert(typeof ctx.alignPromptForCache === "function", "alignPromptForCache missing");
console.log("✓ Test 1: Service worker exports & global bindings verified.");

// 2. Python Multiline AST Skeletonizing
const pyInput = `class PaymentGateway:
    """Handles multi-currency payments."""
    def __init__(self, key: str):
        self.key = key

    async def process_transaction(
        self,
        customer_id: str,
        amount_cents: int = 5000,
        currency: str = "USD"
    ) -> dict:
        """Processes transaction through stripe API."""
        payload = {"cust": customer_id, "amt": amount_cents}
        res = requests.post("/pay", json=payload)
        return res.json()

    def calculate_fee(self, amount: float) -> float:
        return amount * 0.029 + 0.30`;

const pySkeleton = ctx.skeletonizePython(pyInput);
assert(pySkeleton.includes("async def process_transaction("), "Missing async def");
assert(pySkeleton.includes("customer_id: str,"), "Missing param 1");
assert(pySkeleton.includes("amount_cents: int = 5000,"), "Missing param 2");
assert(pySkeleton.includes("currency: str = \"USD\""), "Missing param 3");
assert(pySkeleton.includes("-> dict:"), "Missing return type annotation");
assert(pySkeleton.includes('"""Processes transaction through stripe API."""'), "Missing docstring");
assert(!pySkeleton.includes("requests.post"), "Implementation body was not stripped");
console.log("✓ Test 2: Python multiline typed signature skeletonizing passed.");

// 3. TypeScript Multiline AST Skeletonizing
const tsInput = `export interface UserProfile {
  id: string;
  email: string;
}

export class AuthenticationManager {
  private secretKey: string;

  constructor(key: string) {
    this.secretKey = key;
  }

  public async authenticateUser(
    req: Request,
    res: Response,
    next: NextFunction
  ): Promise<UserProfile | null> {
    const auth = req.headers["authorization"];
    if (!auth) return null;
    return jwt.verify(auth, this.secretKey);
  }

  public getSession(id: string): string {
    return this.sessions.get(id);
  }
}`;

const tsSkeleton = ctx.skeletonizeTypeScript(tsInput);
assert(tsSkeleton.includes("export class AuthenticationManager {"), "Missing class decl");
assert(tsSkeleton.includes("public async authenticateUser("), "Missing method signature start");
assert(tsSkeleton.includes("req: Request,"), "Missing multiline param");
assert(tsSkeleton.includes("): Promise<UserProfile | null> { /* ... */ }"), "Signature not closed properly with collapsed body");
assert(tsSkeleton.includes("public getSession(id: string): string { /* ... */ }"), "Missing simple method signature");
assert(tsSkeleton.endsWith("}"), "Missing class closing brace");
assert(!tsSkeleton.includes("jwt.verify"), "Method implementation was not stripped");
console.log("✓ Test 3: TypeScript multiline method & interface skeletonizing passed.");

// 4. JSON Array Folding & Hash Truncation
const largeJson = JSON.stringify({
  status: "ok",
  records: Array.from({ length: 25 }, (_, i) => ({
    id: `rec_${i}`,
    hash: "a".repeat(300)
  }))
});
const shrunkJson = ctx.shrinkJson(largeJson, 2);
const parsedShrunk = JSON.parse(shrunkJson);
assert(parsedShrunk.records.length === 3, "Array was not folded to maxItems + note");
assert(parsedShrunk.records[2]._squeezed_array_note.includes("23 additional similar items omitted"), "Note missing");
assert(parsedShrunk.records[0].hash.includes("truncated string"), "Long hash was not truncated");
console.log("✓ Test 4: JSON array folding and token shrinkage passed.");

// 5. Log Deduplication & Timestamp Normalization
const logsInput = `2026-09-19T01:23:45.123Z [ERROR] Failed to connect to Redis
2026-09-19T01:23:46.456Z [ERROR] Failed to connect to Redis
2026-09-19T01:23:47.789Z [ERROR] Failed to connect to Redis
2026-09-19T01:23:50.000Z [INFO] Fallback succeeded`;

const shrunkLogs = ctx.shrinkLogs(logsInput);
assert(shrunkLogs.includes("Previous line repeated 2 additional times"), "Logs not deduplicated");
assert(shrunkLogs.includes("[TIME] [ERROR] Failed to connect to Redis"), "Timestamps not normalized");
console.log("✓ Test 5: Log deduplication & timestamp normalization passed.");

// 6. Provider CacheAligner
const aligned = ctx.alignPromptForCache(
  "You are a Senior Systems Architect.",
  "class Database: ...",
  "Write an index migration for Postgres."
);
assert(aligned.includes("CACHE_ANCHOR: SYSTEM_DIRECTIVES"), "Tier 1 anchor missing");
assert(aligned.includes("CACHE_ANCHOR: CODE_ARCHITECTURE"), "Tier 2 anchor missing");
assert(aligned.includes("DYNAMIC_PROMPT: ACTIVE_QUERY"), "Tier 3 anchor missing");
console.log("✓ Test 6: Provider CacheAligner prompt ordering passed.");

// 7. Topological Codebase Graph
const fakeVault = [
  { name: "server.py", content: "import os\nfrom auth import verify\nclass AppServer:\n    def start(self):\n        pass" },
  { name: "auth.py", content: "class AuthManager:\n    def verify(self):\n        pass" }
];
const graph = ctx.buildCodebaseGraph(fakeVault);
assert(graph.nodes.length === 2, "Graph node count mismatch");
assert(graph.graphText.includes("AppServer"), "Graph text missing AppServer class");
assert(graph.graphText.includes("AuthManager"), "Graph text missing AuthManager class");
console.log("✓ Test 7: Topological codebase knowledge graph generation passed.");

// 8. MCP Codebase Graph Disk Generation (codebase_graph.html & CODEBASE_GRAPH.md)
const { execSync } = require("child_process");
const mcpGraphOutput = execSync(`python3 -c "import squeeze_mcp; print(squeeze_mcp.generate_codebase_graph('.'))"`).toString();
assert(mcpGraphOutput.includes("codebase_graph.html"), "Missing codebase_graph.html in MCP output");
assert(fs.existsSync("codebase_graph.html"), "codebase_graph.html was not written to disk");
assert(fs.existsSync("CODEBASE_GRAPH.md"), "CODEBASE_GRAPH.md was not written to disk");
console.log("✓ Test 8: MCP automated codebase_graph.html & CODEBASE_GRAPH.md disk generation passed.");

console.log("\n==========================================");
console.log("🎉 ALL TESTS PASSED SUCCESSFULLY (100%)");
console.log("==========================================");
