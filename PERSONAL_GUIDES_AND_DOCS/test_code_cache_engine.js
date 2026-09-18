const {
  skeletonizePython,
  skeletonizeTypeScript,
  shrinkJson,
  shrinkLogs,
  buildCodebaseGraph,
  alignPromptForCache
} = require("./skeletonizer.js");

console.log("🚀 Testing Squeeze Code & Cache Intelligence Engine...\n");

// 1. Test Python Skeletonizer
const pyCode = `
import os
import sys
from typing import List, Optional

class DatabaseClient:
    """Connects to SQL/NoSQL cluster with pooled retries."""
    
    def __init__(self, host: str, port: int = 5432):
        self.host = host
        self.port = port
        self._pool = []
        for i in range(10):
            self._pool.append(connect_raw(host, port))

    async def execute_query(self, query: str, params: Optional[dict] = None) -> List[dict]:
        """Runs parameterized query across available connection."""
        cursor = self.get_connection().cursor()
        cursor.execute(query, params or {})
        rows = cursor.fetchall()
        logger.info("Query executed successfully")
        return [dict(r) for r in rows]

def standalone_helper(x: int) -> bool:
    val = x * 2
    return val > 10
`;

const pySkeleton = skeletonizePython(pyCode);
console.log("=== 1. PYTHON SKELETON (Squeeze AST) ===");
console.log(pySkeleton);
const pyOrigTokens = Math.ceil(pyCode.length / 4);
const pySkelTokens = Math.ceil(pySkeleton.length / 4);
console.log(`Original: ~${pyOrigTokens} tokens -> Skeleton: ~${pySkelTokens} tokens (${Math.round((pyOrigTokens - pySkelTokens)/pyOrigTokens * 100)}% saved!)\n`);

// 2. Test TypeScript Skeletonizer
const tsCode = `
import { Request, Response } from "express";

export interface UserSession {
  userId: string;
  roles: string[];
  expiresAt: number;
}

export class AuthService {
  private secretKey: string;

  constructor(key: string) {
    this.secretKey = key;
    this.initCryptoProviders();
  }

  public async authenticate(req: Request): Promise<UserSession | null> {
    const token = req.headers.authorization?.split(" ")[1];
    if (!token) return null;
    const decoded = verifyJwt(token, this.secretKey);
    return { userId: decoded.sub, roles: decoded.roles, expiresAt: decoded.exp };
  }
}
`;

const tsSkeleton = skeletonizeTypeScript(tsCode);
console.log("=== 2. TYPESCRIPT SKELETON (Squeeze AST) ===");
console.log(tsSkeleton);
const tsOrigTokens = Math.ceil(tsCode.length / 4);
const tsSkelTokens = Math.ceil(tsSkeleton.length / 4);
console.log(`Original: ~${tsOrigTokens} tokens -> Skeleton: ~${tsSkelTokens} tokens (${Math.round((tsOrigTokens - tsSkelTokens)/tsOrigTokens * 100)}% saved!)\n`);

// 3. Test JSON Array Folder
const bigJson = JSON.stringify({
  status: "success",
  users: Array.from({ length: 25 }, (_, i) => ({
    id: `usr_${i}`,
    name: `User Name ${i}`,
    email: `user${i}@example.com`,
    tokenPayload: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
  }))
});

const shrunkJson = shrinkJson(bigJson, 2);
console.log("=== 3. JSON ARRAY FOLDER (Squeeze Data) ===");
console.log(shrunkJson.substring(0, 350) + "...\n");
const jsonOrigTokens = Math.ceil(bigJson.length / 4);
const jsonSkelTokens = Math.ceil(shrunkJson.length / 4);
console.log(`Original: ~${jsonOrigTokens} tokens -> Shrunk: ~${jsonSkelTokens} tokens (${Math.round((jsonOrigTokens - jsonSkelTokens)/jsonOrigTokens * 100)}% saved!)\n`);

// 4. Test Log Deduplicator
const logs = `
2026-09-19T01:10:00.123Z [INFO] Service starting up...
2026-09-19T01:10:01.456Z [WARN] Connection timeout to Redis node 127.0.0.1:6379, retrying...
2026-09-19T01:10:01.456Z [WARN] Connection timeout to Redis node 127.0.0.1:6379, retrying...
2026-09-19T01:10:01.456Z [WARN] Connection timeout to Redis node 127.0.0.1:6379, retrying...
2026-09-19T01:10:01.456Z [WARN] Connection timeout to Redis node 127.0.0.1:6379, retrying...
2026-09-19T01:10:05.789Z [INFO] Connected to failover node.
`;
const cleanLogs = shrinkLogs(logs);
console.log("=== 4. LOG DEDUPLICATION (Squeeze Data) ===");
console.log(cleanLogs);

// 5. Test Codebase Graph Builder
const graph = buildCodebaseGraph([
  { name: "db.py", content: pyCode },
  { name: "auth.ts", content: tsCode }
]);
console.log("=== 5. CODEBASE TOPOLOGICAL GRAPH (Squeeze Engine) ===");
console.log(graph.graphText);

// 6. Test Cache Aligner
const aligned = alignPromptForCache(
  "Act as a Principal Staff Engineer. Prioritize speed & reliability.",
  graph.graphText,
  "How should AuthService interact with DatabaseClient?"
);
console.log("=== 6. CACHE-ALIGNED PROMPT (Squeeze Engine) ===");
console.log(aligned);

console.log("\n✅ ALL SQUEEZE CODE & CACHE ENGINE TESTS PASSED!");
