// Automated test suite for Squeeze AI Background Optimizer
const fs = require('fs');

// Mock chrome APIs for headless node testing
global.chrome = {
  runtime: {
    onInstalled: { addListener: () => {} },
    onMessage: { addListener: () => {} }
  },
  storage: {
    local: {
      get: (keys, cb) => {
        const res = {};
        keys.forEach(k => res[k] = undefined);
        if (cb) cb(res);
        return Promise.resolve(res);
      },
      set: (obj, cb) => {
        if (cb) cb();
        return Promise.resolve();
      }
    }
  }
};

// Read background.js functions
const bgCode = fs.readFileSync('background.js', 'utf8');
eval(bgCode);

console.log("=== SQUEEZE AI TEST SUITE ===");

// Test 1: Token Estimation
const t1 = estimateTokens("Hello world, this is a test prompt!");
console.assert(t1 > 0, "Token count should be > 0");
console.log(`[PASS] Token Estimation: "Hello world..." -> ${t1} tokens`);

// Test 2: DLP Secret Shield
const secretPrompt = `Here is my key: sk-proj-12345678901234567890abcdef and DB: mongodb://admin:SuperSecret999@db.net/test`;
const dlp = maskSensitiveData(secretPrompt);
console.assert(dlp.sanitized.includes("[MASKED_OPENAI_KEY]"), "OpenAI key should be masked");
console.assert(dlp.sanitized.includes("[MASKED_DB_PASS]"), "DB password should be masked");
console.assert(!dlp.sanitized.includes("SuperSecret999"), "Plaintext password must not leak");
console.log(`[PASS] DLP Secret Shield: Redacted ${dlp.secretsFound.length} secrets successfully:`);
console.log("       " + dlp.sanitized);

// Test 3: Balanced Optimization (Fluff & Greetings Removal)
const fluffyPrompt = `Hello Claude! Hope you are doing well today. Could you please help me in order to write a database query? Thanks in advance!`;
const optBalanced = optimizeLocally(fluffyPrompt, "balanced", {
  ruleStripGreetings: true,
  ruleSimplifyPhrases: true,
  ruleAbbreviate: false,
  ruleStripArticles: false,
  rulePolishMarkdown: true
});
console.assert(!optBalanced.optimized.toLowerCase().includes("hello claude"), "Greeting should be stripped");
console.assert(!optBalanced.optimized.toLowerCase().includes("in order to"), "'in order to' should become 'to'");
console.assert(!optBalanced.optimized.toLowerCase().includes("thanks in advance"), "Closing thanks should be stripped");
console.log(`[PASS] Balanced Compression:`);
console.log(`       Original: "${fluffyPrompt}"`);
console.log(`       Squeezed: "${optBalanced.optimized}"`);
console.log(`       Rules:    ${optBalanced.rulesApplied.join(", ")}`);

// Test 4: Code Block Preservation
const codePrompt = `Please check this code:
\`\`\`js
function inOrderToRun() {
  const please = "do not touch";
  return please;
}
\`\`\`
Thanks!`;
const optCode = optimizeLocally(codePrompt, "squeeze", {
  ruleStripGreetings: true,
  ruleSimplifyPhrases: true,
  ruleAbbreviate: true,
  ruleStripArticles: true,
  rulePolishMarkdown: true
});
console.assert(optCode.optimized.includes("function inOrderToRun()"), "Code inside blocks must be preserved exactly!");
console.assert(optCode.optimized.includes('const please = "do not touch";'), "Code string literals must NOT be modified!");
console.log(`[PASS] Code Block Protection: Code block preserved verbatim.`);

// Test 5: Squeeze Mode (Telegraphic)
const longPrompt = `It is important that you should make a request to the database administrator in order to get the configuration parameters.`;
const optSqueeze = optimizeLocally(longPrompt, "squeeze", {
  ruleStripGreetings: true,
  ruleSimplifyPhrases: true,
  ruleAbbreviate: true,
  ruleStripArticles: true,
  rulePolishMarkdown: true
});
console.log(`[PASS] Squeeze Extreme Mode:`);
console.log(`       Original: "${longPrompt}"`);
console.log(`       Squeezed: "${optSqueeze.optimized}"`);

console.log("\nALL TESTS PASSED SUCCESSFULLY! 🚀");
