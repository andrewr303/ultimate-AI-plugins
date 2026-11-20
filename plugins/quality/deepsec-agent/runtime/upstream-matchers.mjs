// Generated from uploaded DeepSec sources. See LICENSE and NOTICE. Matcher logic unchanged.

// vendor/deepsec-scanner/matcher-registry.ts
var MatcherRegistry = class {
  matchers = /* @__PURE__ */ new Map();
  register(plugin) {
    this.matchers.set(plugin.slug, plugin);
  }
  getAll() {
    return Array.from(this.matchers.values());
  }
  getBySlug(slug) {
    return this.matchers.get(slug);
  }
  getBySlugs(slugs) {
    return slugs.map((s) => this.matchers.get(s)).filter((m) => m !== void 0);
  }
  slugs() {
    return Array.from(this.matchers.keys());
  }
};

// vendor/deepsec-scanner/matchers/agent-loop-no-cap.ts
var agentLoopNoCapMatcher = {
  noiseTier: "normal",
  slug: "agent-loop-no-cap",
  description: "Agent / LLM call without maxSteps / maxTurns / stopWhen \u2014 DoS + cost-burn risk",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `import { streamText } from "ai";
const result = streamText({
  model: openai("gpt-4"),
  prompt: "hi",
});`,
    `import { generateText } from "ai";
await generateText({ model, prompt: "hi" });`,
    `import { generateObject } from "ai";
await generateObject({ model, schema, prompt });`,
    `import { streamObject } from "ai";
await streamObject({ model, schema, prompt });`,
    `import { query } from "@anthropic-ai/claude-agent-sdk";
await query({ prompt: "hi" });`,
    `import { Codex } from "@openai/codex-sdk";
await claude.query({ prompt: "hi" });`,
    `import { openai } from "@ai-sdk/openai";
await generateText({ model: openai("gpt-4"), prompt: "hi" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_AI_SDK = /\bfrom\s+["']ai["']|\bfrom\s+["']@ai-sdk\/[^"']*["']|\bfrom\s+["']@anthropic-ai\/claude-agent-sdk["']|\bfrom\s+["']@openai\/codex-sdk["']/;
    if (!HAS_AI_SDK.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isAgentCall = /\b(?:streamText|generateText|generateObject|streamObject)\s*\(/.test(line) || /\bawait\s+query\s*\(/.test(line) || /\bclaude\.\s*query\s*\(/.test(line);
      if (!isAgentCall) continue;
      const window = lines.slice(i, Math.min(lines.length, i + 30)).join("\n");
      const hasCap = /\bmaxSteps\s*:\s*\d|\bmaxTurns\s*:\s*\d|\bstopWhen\s*:|\bsignal\s*:|\babortSignal\s*:|\btimeout\s*:\s*\d/.test(
        window
      );
      if (hasCap) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 6);
      matches.push({
        vulnSlug: "agent-loop-no-cap",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: "agent/LLM call without maxSteps/maxTurns/stopWhen/signal"
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/agent-tool-definition.ts
var agentToolDefinitionMatcher = {
  noiseTier: "precise",
  slug: "agent-tool-definition",
  description: "AI agent tool definitions \u2014 prompt injection attack surface (code execution, API access)",
  filePatterns: [
    "**/tools/**/*.{ts,tsx,js,jsx}",
    "**/agent/**/*.{ts,tsx,js,jsx}",
    "**/agents/**/*.{ts,tsx,js,jsx}",
    "**/*tool*.{ts,tsx,js,jsx}",
    "**/*agent*.{ts,tsx,js,jsx}"
  ],
  examples: [
    `const myTool = tool({
  description: "do thing",
  parameters: z.object({}),
  execute: async () => ({}),
});`,
    `const t = createTool({ name: "x", execute: async () => ({}) });`,
    `const t = defineTool({ name: "x" });`,
    `import { exec } from "child_process";
exec(userInput);`,
    `eval(userInput);`,
    `import fs from "fs";
fs.writeFile(path, data, () => {});`,
    `await fetch(url);`,
    `import { sandbox } from "sandbox";
await sandbox.runCode(code);`,
    `import { DynamicTool } from "langchain/tools";
const t = new DynamicTool({ name: "x" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const patterns = [
      // AI SDK tool definitions
      { regex: /tool\s*\(\s*\{/, label: "AI SDK tool definition \u2014 agent-callable function" },
      { regex: /createTool|defineTool/, label: "Tool factory \u2014 agent-callable function" },
      // Dangerous tool operations
      {
        regex: /exec\(|execSync\(|spawn\(|child_process/,
        label: "Tool executes shell commands \u2014 RCE via prompt injection"
      },
      {
        regex: /eval\(|new Function\(|vm\.run/,
        label: "Tool evaluates code \u2014 RCE via prompt injection"
      },
      { regex: /writeFile|fs\.write|fs\.mkdir/, label: "Tool writes to filesystem" },
      {
        regex: /fetch\(|axios|http\.request/,
        label: "Tool makes HTTP requests \u2014 SSRF via prompt injection"
      },
      // Sandbox execution
      { regex: /sandbox|Sandbox|runCode|executeCode/, label: "Sandbox code execution tool" },
      // LangChain/similar
      { regex: /DynamicTool|StructuredTool|BaseTool/, label: "LangChain tool definition" }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 4);
          matches.push({
            vulnSlug: "agent-tool-definition",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/agentic-untrusted-prompt-input.ts
var agenticUntrustedPromptInputMatcher = {
  noiseTier: "normal",
  slug: "agentic-untrusted-prompt-input",
  description: "Prompts built from external/untrusted variables \u2014 indirect prompt-injection sink",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `await streamText({
  model,
  prompt: \`Summarize: \${notes}\`,
});`,
    `await generateText({
  system: \`You are an assistant.\`,
  prompt: \`Read this email: \${emailBody}\`,
});`,
    `await generateObject({
  messages: [
    { role: "user", content: \`\${transcript}\` },
  ],
  schema,
});`,
    `await openai.chat.completions.create({
  messages: [{ role: "system", content: \`Context: \${scraped}\` }],
});`,
    `await anthropic.messages.create({
  system: \`Use this KB:
\${kbDocs}\`,
  messages: [],
});`,
    `import { streamText } from "@ai-sdk/openai";
await streamText({
  prompt: \`Notes from CRM: \${leadNotes}\`,
  model,
});`,
    `await generateText({
  input: \`Web research: \${webpage}\`,
  model,
});`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const LLM_HINT = /\b(?:streamText|generateText|generateObject|streamObject|messages\s*:\s*\[|anthropic\.|openai\.|gateway\(|getGatewayModelString|claude_agent|ClaudeAgent|claude-agent|@ai-sdk\/|ai\/sdk)\b/;
    if (!LLM_HINT.test(content)) return [];
    const UNTRUSTED_VAR = /\b(?:notes|description|body|content|text|summary|email|emailBody|transcript|scraped|fetched|webpage|web_research|attachment|document|kb_?[A-Z]?[a-z]+|salesforce[A-Z][a-z]+|sfdc[A-Z][a-z]+|snowflake[A-Z][a-z]+|bigquery[A-Z][a-z]+|leadNotes|accountNotes|opportunityNotes|messageHistory|slackHistory|exaResult|perplexity[A-Z]?|crawlResult|browserbaseResult|crawled|recon[A-Z][a-z]+)\b/;
    const lines = content.split("\n");
    const matches = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isPromptKey = /\b(?:system|user|prompt|content|messages|input|instructions)\s*:\s*[`'"]/.test(line) || /\b(?:system|user|prompt|content|messages|input|instructions)\s*:\s*\[/.test(line);
      if (!isPromptKey) continue;
      const end = Math.min(lines.length, i + 30);
      for (let j = i; j < end; j++) {
        const m = lines[j].match(/\$\{([^}]+)\}/);
        if (!m) continue;
        if (UNTRUSTED_VAR.test(m[1])) {
          const start = Math.max(0, i - 2);
          matches.push({
            vulnSlug: "agentic-untrusted-prompt-input",
            lineNumbers: [j + 1],
            snippet: lines.slice(start, Math.min(lines.length, j + 3)).join("\n"),
            matchedPattern: `prompt interpolates untrusted: ${m[1].slice(0, 80)}`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/algorithm-confusion.ts
var algorithmConfusionMatcher = {
  noiseTier: "precise",
  slug: "algorithm-confusion",
  description: "JWT verification without algorithm pinning \u2014 algorithm confusion attack risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx,lua}"],
  examples: [
    `const decoded = jwt.verify(token, secret);`,
    `const result = await jwtVerify(token, key);`,
    `const claims = verifyJwt(token, publicKey);`,
    `local ok = jwt_obj:verify(secret, token)`,
    `jwt.verify(token, key, { algorithms: ["RS256"] });`,
    `await jwtVerify(token, jwks, { algorithm: "HS256" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const hasJwtVerify = /jwt\.verify|jwtVerify|verifyJwt|jwt_obj:verify|resty\.jwt/.test(content);
    if (!hasJwtVerify) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (/jwt\.verify|jwtVerify|verifyJwt|jwt_obj:verify/.test(lines[i])) {
        const window = lines.slice(i, Math.min(lines.length, i + 5)).join("\n");
        const hasAlgPin = /algorithms\s*:|algorithm\s*:|alg.*RS256|alg.*HS256|alg.*ES256/.test(
          window
        );
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "algorithm-confusion",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: hasAlgPin ? "JWT verification with algorithm pin (verify correct algorithm)" : "JWT verification WITHOUT algorithm pinning \u2014 algorithm confusion risk"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/utils.ts
function regexMatcher(slug, patterns, content) {
  const lines = content.split("\n");
  const matches = [];
  for (const { regex, label } of patterns) {
    const hitLines = [];
    const snippets = [];
    for (let i = 0; i < lines.length; i++) {
      if (regex.test(lines[i])) {
        hitLines.push(i + 1);
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        snippets.push(lines.slice(start, end).join("\n"));
      }
    }
    if (hitLines.length > 0) {
      matches.push({
        vulnSlug: slug,
        lineNumbers: hitLines,
        snippet: snippets[0],
        // first occurrence context
        matchedPattern: label
      });
    }
  }
  return matches;
}

// vendor/deepsec-scanner/matchers/android-manifest-export.ts
var androidManifestExportMatcher = {
  noiseTier: "noisy",
  slug: "android-manifest-export",
  description: "Exported Android components (Activity / Service / Receiver / Provider) \u2014 IPC entry points (gated on android)",
  filePatterns: ["**/AndroidManifest.xml"],
  requires: { tech: ["android"] },
  examples: [
    `<activity android:name=".MainActivity" android:exported="true"/>`,
    `<service android:name=".SyncService" android:exported="true"/>`,
    `<receiver android:name=".BootReceiver" android:exported="true"/>`,
    `<provider android:name=".DataProvider" android:exported="true" android:authorities="com.example"/>`,
    `<intent-filter>
    <action android:name="android.intent.action.VIEW"/>
</intent-filter>`,
    `<activity android:name=".X" android:permission="com.example.PERM"/>`,
    `<service android:name=".S" android:permission="android.permission.BIND_JOB_SERVICE"/>`,
    `<data android:scheme="myapp"/>`,
    `<data android:scheme="https" android:host="example.com"/>`
  ],
  match(content, filePath) {
    if (/\/build\//.test(filePath)) return [];
    return regexMatcher(
      "android-manifest-export",
      [
        {
          regex: /<(?:activity|service|receiver|provider)\b[^>]*android:exported="true"/,
          label: "exported component \u2014 confirm permissions"
        },
        {
          regex: /<intent-filter\b/,
          label: "intent-filter \u2014 implicitly exported on pre-31 SDK"
        },
        {
          regex: /android:permission="[^"]+"/,
          label: "android:permission= guard"
        },
        {
          regex: /<data\s+android:scheme=/,
          label: "deeplink scheme \u2014 review URL handling for SSRF/XSS"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/apex-rest-resource.ts
var apexRestResourceMatcher = {
  noiseTier: "noisy",
  slug: "apex-rest-resource",
  description: "Salesforce Apex REST resources and class sharing (gated on Apex)",
  filePatterns: ["**/*.cls"],
  requires: { tech: ["apex"] },
  examples: [
    `@RestResource(urlMapping='/Account/*')
global with sharing class AccountResource {}`,
    `@RestResource(urlMapping = '/v1/users/*')
global class UserResource {}`,
    `@HttpGet
global static Account doGet() { return null; }`,
    `@HttpPost
global static String doPost(String name) { return name; }`,
    `@HttpPut
global static void doPut() {}`,
    `@HttpPatch
global static void doPatch() {}`,
    `@HttpDelete
global static void doDelete() {}`,
    `@HttpHead
global static void doHead() {}`,
    `public without sharing class AdminOps {}`,
    `global with sharing class SafeOps {}`,
    `@AuraEnabled(cacheable=true)
public static List<Account> getAccounts() { return null; }`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//i.test(filePath)) return [];
    return regexMatcher(
      "apex-rest-resource",
      [
        {
          regex: /@RestResource\s*\(\s*urlMapping\s*=\s*'[^']+'\s*\)/,
          label: "@RestResource declaration"
        },
        {
          regex: /@Http(?:Get|Post|Put|Patch|Delete|Head)\b/,
          label: "@HttpVerb method"
        },
        {
          regex: /\bwithout\s+sharing\b/,
          label: "without sharing \u2014 bypasses record-level security (REVIEW)"
        },
        { regex: /\bwith\s+sharing\b/, label: "with sharing \u2014 record security applied" },
        { regex: /\bAuraEnabled\s*\(/, label: "@AuraEnabled \u2014 exposed to Lightning" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/auth-bypass.ts
var authBypassMatcher = {
  noiseTier: "normal",
  slug: "auth-bypass",
  description: "Auth checks, middleware guards, session validation that may be bypassable",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `if (isAdmin === true) { grant(); }`,
    `user.isAdmin == req.body.isAdmin`,
    `// skip auth in development`,
    `const bypassAuth = true;`,
    `if (!session) return null;`,
    `if ( session ) { /* ok */ }`,
    `await verifyToken(token);`,
    `const ok = verifyJWT(t);`,
    `verifySession(req);`,
    `verifyAuth(headers);`,
    `app.use(authMiddleware);`,
    `const middlewareAuth = compose(...);`,
    `const t = req.headers["authorization"];`,
    `req.headers['authorization']`
  ],
  match(content, _filePath) {
    return regexMatcher(
      "auth-bypass",
      [
        { regex: /isAdmin\s*[=!]==?\s*(true|false|req\.)/, label: "admin check comparison" },
        {
          regex: /auth.{0,30}skip|skip.{0,30}auth|bypass.{0,30}auth/i,
          label: "auth skip/bypass"
        },
        { regex: /if\s*\(\s*!?\s*session\s*\)/, label: "session null check" },
        { regex: /verify(Token|JWT|Session|Auth)\s*\(/, label: "auth verification call" },
        { regex: /middleware.{0,30}auth|auth.{0,30}middleware/i, label: "auth middleware" },
        { regex: /req\.headers\[['"]authorization['"]\]/, label: "authorization header access" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/azure-function-handler.ts
var azureFunctionHandlerMatcher = {
  noiseTier: "noisy",
  slug: "azure-function-handler",
  description: "Azure Functions Node/Python/JS handler signatures (gated on Azure Functions)",
  filePatterns: ["**/*.{ts,js,mjs,cjs,py}", "**/function.json"],
  requires: { tech: ["azure-functions"] },
  examples: [
    `module.exports = async function (context, req) { context.res = { body: "ok" } }`,
    `module.exports = async function(context, req) {
  context.log("hi");
}`,
    `def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("hi")`,
    `{ "authLevel": "anonymous", "type": "httpTrigger" }`,
    `{ "authLevel": "function" }`,
    `{ "authLevel": "admin" }`,
    `app.http('httpTrigger1', { methods: ['GET'], handler: async (req, ctx) => {} })`,
    `app.http("api", { handler: myHandler })`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "azure-function-handler",
      [
        {
          regex: /module\.exports\s*=\s*async\s*function\s*\(\s*context\b/,
          label: "module.exports = async function(context, req) \u2014 Azure Functions Node"
        },
        {
          regex: /^\s*def\s+main\s*\(\s*req\s*:\s*func\.HttpRequest/m,
          label: "Python def main(req: func.HttpRequest)"
        },
        {
          regex: /"authLevel"\s*:\s*"(?:anonymous|function|admin)"/,
          label: "function.json authLevel \u2014 confirm anonymous is intentional"
        },
        {
          regex: /\bapp\.http\s*\(\s*['"][^'"]+['"]\s*,/,
          label: "app.http('name', { handler }) \u2014 Functions v4 model"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/cache-key-poisoning.ts
var cacheKeyPoisoningMatcher = {
  noiseTier: "precise",
  slug: "cache-key-poisoning",
  description: "Cache key construction with attacker-controlled values \u2014 poisoning risk",
  filePatterns: ["**/*.{lua,go,ts,js}"],
  examples: [
    `const cacheKey = "u:" + req.headers.host;`,
    `const cache_key = host + ":" + path;`,
    `const cacheKey = req.headers["x-tenant"];`,
    `const cache_key = req.header("x-trace");`,
    `const cacheKey = url + req.query.foo;`,
    `const cache_key = JSON.stringify(query);`,
    `Vary: Accept-Language, Accept-Encoding`,
    `Vary: Cookie`,
    `ngx.shared.cache:set(ngx.var.host .. path, val)`,
    `ngx.shared.dict:set("k:" .. ngx.var.request_uri, val)`,
    `redis.set("cache:" + req.body.id, value);`,
    `redis.hset("cache:host", host, value);`,
    `store.set("cache:" + req.body.k, v);`,
    `kv.set("cache:" + host, blob);`
  ],
  match(content, filePath) {
    if (/_test\.|_spec\.|\.test\.|\.spec\./.test(filePath)) return [];
    return regexMatcher(
      "cache-key-poisoning",
      [
        {
          regex: /cache.{0,80}key.{0,80}host|cache_key.{0,80}host/i,
          label: "Cache key includes Host header"
        },
        {
          regex: /cache.{0,80}key.{0,80}header|cache_key.{0,80}header/i,
          label: "Cache key includes request header"
        },
        {
          regex: /cache.{0,80}key.{0,80}query|cache_key.{0,80}query/i,
          label: "Cache key includes query params"
        },
        {
          regex: /vary.{0,40}:.{0,80}accept|vary.{0,40}:.{0,80}cookie/i,
          label: "Vary header includes client-controlled values"
        },
        {
          regex: /ngx\.shared\.\w+:set\s*\([^)]{0,200}ngx\.var\.host/,
          label: "Shared dict keyed by Host header"
        },
        {
          regex: /ngx\.shared\.\w+:set\s*\([^)]{0,200}ngx\.var\.request_uri/,
          label: "Shared dict keyed by request URI"
        },
        {
          regex: /redis\.\w*set\s*\([^)]{0,200}req\.|redis\.\w*set\s*\([^)]{0,200}host/i,
          label: "Redis set with request-derived key"
        },
        {
          regex: /\.set\s*\([^)]{0,200}cache[^)]{0,80}req\.|\.set\s*\([^)]{0,200}cache[^)]{0,80}host/i,
          label: "Cache set with request-derived data"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/cache-key-scope.ts
var cacheKeyScopeMatcher = {
  noiseTier: "normal",
  slug: "cache-key-scope",
  description: "Cache keys that may lack user/team scoping \u2014 cross-tenant risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const cached = await redis.get(\`feature:\${name}\`);`,
    `await redis.set(\`config:\${name}\`, value);`,
    `await redis.hget(\`map:\${k}\`, field);`,
    `await redis.hset(\`map:\${k}\`, field, value);`,
    `await redis.setex(\`token:\${name}\`, 60, value);`,
    `await redis.get("global-counter");`,
    `await redis.set("singleton", value);`,
    `await cache.get(\`feature:\${flag}\`);`,
    `await cache.set(\`feature:\${flag}\`, value);`,
    `cache.has(\`flag:\${name}\`);`,
    `cache.get("global-counter");`,
    `cache.set("singleton", payload);`,
    `const cacheKey = \`feature:\${name}\`;`,
    `const cache_key = \`feature:\${name}\`;`,
    `await store.get(\`feature:flag:\${id}\`);`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const cacheKeyPatterns = [
      { regex: /redis\.(get|set|hget|hset|setex)\s*\(\s*`/, label: "Redis template key" },
      { regex: /redis\.(get|set|hget|hset|setex)\s*\(\s*['"]/, label: "Redis string key" },
      { regex: /cache\.(get|set|has)\s*\(\s*`/, label: "cache template key" },
      { regex: /cache\.(get|set|has)\s*\(\s*['"]/, label: "cache string key" },
      { regex: /cacheKey\s*=\s*`/, label: "cacheKey template literal" },
      { regex: /cache_key\s*=\s*`/, label: "cache_key template literal" },
      { regex: /\.get\s*\(\s*`[^`]*:/, label: "KV get with colon-separated key" }
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const { regex, label } of cacheKeyPatterns) {
        if (regex.test(line)) {
          const context = lines.slice(Math.max(0, i - 1), Math.min(lines.length, i + 2)).join("\n");
          const hasScope = /userId|user_id|teamId|team_id|ownerId|owner_id|auth\.|session\.|projectId|project_id/i.test(
            context
          );
          if (!hasScope) {
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            matches.push({
              vulnSlug: "cache-key-scope",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: `${label} \u2014 no user/team scoping visible in key construction`
            });
          }
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/clj-ring-handler.ts
var cljRingHandlerMatcher = {
  noiseTier: "noisy",
  slug: "clj-ring-handler",
  description: "Clojure Ring/Compojure routes and handlers (gated on Clojure)",
  filePatterns: ["**/*.{clj,cljs,cljc}"],
  requires: { tech: ["clojure"] },
  examples: [
    `(defroutes app-routes
  (GET "/" [] "Hello"))`,
    `(defroutes api
  (POST "/users" req (create-user req)))`,
    `  (GET "/users/:id" [id] (get-user id))`,
    `  (PUT "/users/:id" [id :as req] (update-user id req))`,
    `  (DELETE "/users/:id" [id] (delete-user id))`,
    `  (PATCH "/users/:id" [id :as req] (patch id req))`,
    `  (ANY "/healthz" [] "ok")`,
    `(defn handler [request] (response "hi"))`,
    `(defn login [req] (-> req :params :user))`,
    `(-> handler
    (wrap-authentication backend)
    (wrap-authorization backend))`,
    `(wrap-cors handler)`,
    `(wrap-csrf handler)`
  ],
  match(content, filePath) {
    if (/\/(test|spec)\//.test(filePath)) return [];
    return regexMatcher(
      "clj-ring-handler",
      [
        {
          regex: /\bdefroutes\b/,
          label: "defroutes Compojure declaration"
        },
        {
          regex: /\((?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|ANY)\s+"[^"]+"/,
          label: "Compojure route verb"
        },
        {
          regex: /\bdefn\s+\w+\s+\[\s*(?:request|req)\b/,
          label: "Ring handler fn (request-shape arg)"
        },
        { regex: /\bwrap-(?:authentication|authorization|cors|csrf)\b/, label: "Ring middleware" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/connectrpc-handler-impl.ts
var connectrpcHandlerImplMatcher = {
  noiseTier: "precise",
  slug: "connectrpc-handler-impl",
  description: "Go file implementing one or more ConnectRPC handler methods (entry-point surface)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["connectrpc"] },
  examples: [
    `func (s *Service) ExecCommand(ctx context.Context, req *connect.Request[ExecRequest]) (*connect.Response[ExecResponse], error) {
  return nil, nil
}`,
    `func (cs *ControllerService) Run(
  ctx context.Context,
  req *connect.Request[RunRequest],
) (*connect.Response[RunResponse], error) {
  return nil, nil
}`,
    `func (s *Server) Stream(ctx context.Context, stream *connect.ServerStream[Event]) error {
  return nil
}`,
    `func (h *Handler) BidiChat(ctx context.Context, stream *connect.BidiStream[Msg, Msg]) error {
  return nil
}`,
    `func (s *Service) Upload(ctx context.Context, stream *connect.ClientStream[Chunk]) (*connect.Response[Ack], error) {
  return nil, nil
}`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    if (/(?:^|\/)gen\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    let firstContext;
    const FUNC_OPEN = /^\s*func\s*\([^)]+\)\s+[A-Z]\w*\s*\(/;
    const CONNECT_TYPE = /\bconnect\.(?:Request|ClientStream|BidiStream|ServerStream)\b/;
    for (let i = 0; i < lines.length; i++) {
      if (!FUNC_OPEN.test(lines[i])) continue;
      const span = lines.slice(i, i + 8).join("\n");
      if (!/\bcontext\.Context\b/.test(span)) continue;
      if (!CONNECT_TYPE.test(span)) continue;
      hitLines.push(i + 1);
      if (firstContext === void 0) {
        const s = Math.max(0, i - 1);
        const e = Math.min(lines.length, i + 7);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "connectrpc-handler-impl",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: "ConnectRPC handler method body"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/cors-wildcard.ts
var corsWildcardMatcher = {
  noiseTier: "precise",
  slug: "cors-wildcard",
  description: "CORS wildcard or dynamic origin reflection without validation",
  filePatterns: ["**/*.{ts,tsx,js,jsx,lua,go,conf}"],
  examples: [
    `res.setHeader("Access-Control-Allow-Origin", "*");`,
    `headers: { "Access-Control-Allow-Origin": "*" }`,
    `res.setHeader("Access-Control-Allow-Origin", req.headers.origin);`,
    `headers["Access-Control-Allow-Origin"] = origin;`,
    `headers["Access-Control-Allow-Credentials"] = "true"; headers["Access-Control-Allow-Origin"] = origin;`,
    `app.use(cors({ origin: true, credentials: true }));`,
    `add_header Access-Control-Allow-Origin $http_origin;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "cors-wildcard",
      [
        { regex: /Access-Control-Allow-Origin.*\*/, label: "CORS wildcard origin" },
        {
          regex: /Access-Control-Allow-Origin.*req\.headers\.origin|Access-Control-Allow-Origin.*origin/,
          label: "CORS origin reflection (verify validation)"
        },
        {
          regex: /Access-Control-Allow-Credentials.*true.*Allow-Origin|Allow-Origin.*Allow-Credentials.*true/i,
          label: "CORS credentials + origin (dangerous combo)"
        },
        {
          regex: /cors\s*\(\s*\{.*origin:\s*true/,
          label: "CORS middleware with origin: true (reflects all)"
        },
        {
          regex: /add_header\s+Access-Control-Allow-Origin\s+\$http_origin/,
          label: "Nginx CORS origin reflection"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/cr-kemal-route.ts
var crKemalRouteMatcher = {
  noiseTier: "noisy",
  slug: "cr-kemal-route",
  description: "Crystal Kemal route handlers (gated on kemal)",
  filePatterns: ["**/*.cr"],
  requires: { tech: ["kemal"] },
  examples: [
    `get "/" do
  "Hello World!"
end`,
    `post "/users" do |env|
  env.params.json["name"]
end`,
    `put "/users/:id" do |env|
end`,
    `patch "/users/:id" do |env|
end`,
    `delete "/users/:id" do
end`,
    `options "/users" do
end`,
    `ws "/chat" do |socket|
end`,
    `before_all do |env|
  env.response.content_type = "application/json"
end`,
    `before_get do |env|
  env.response.content_type = "application/json"
end`,
    `before_post do |env|
end`,
    `before_put do
end`,
    `before_delete do
end`,
    `name = env.params.url["name"]`,
    `q = env.params.query["q"]`,
    `body = env.params.json["body"]`,
    `file = env.params.files["upload"]`
  ],
  match(content, filePath) {
    if (/\/(spec|test)\//.test(filePath)) return [];
    return regexMatcher(
      "cr-kemal-route",
      [
        {
          regex: /^\s*(?:get|post|put|patch|delete|options|ws)\s+"[^"]+"\s+do\b/m,
          label: "Kemal <verb> '/path' do"
        },
        {
          regex: /^\s*before_(?:all|get|post|put|delete)\s+do\b/m,
          label: "before_* do \u2014 auth filter"
        },
        { regex: /\benv\.params\.(?:url|query|json|body|files)\b/, label: "env.params accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/cron-secret-check.ts
var cronSecretCheckMatcher = {
  noiseTier: "precise",
  slug: "cron-secret-check",
  description: "Cron endpoints \u2014 verify CRON_SECRET validation is present and not bypassable when env unset",
  filePatterns: [
    "**/cron/**/*.{ts,tsx,js,jsx}",
    "**/crons/**/*.{ts,tsx,js,jsx}",
    "**/api/cron*/**/*.{ts,tsx,js,jsx}",
    "**/app/api/**/route.{ts,tsx}"
  ],
  examples: [
    `// CRON_SECRET check on cron route
export async function GET(req: Request) {
  if (req.headers.get("authorization") !== \`Bearer \${process.env.CRON_SECRET}\`) {
    return new Response("unauthorized", { status: 401 });
  }
  return new Response("ok");
}`,
    `// CRON_SECRET handler
export const POST = async (req) => {
  const secret = process.env.CRON_SECRET;
  if (req.headers.get("x-cron-secret") !== secret) {
    return new Response("nope", { status: 401 });
  }
  return Response.json({ ok: true });
};`,
    `// cron auth via CRON_SECRET
export async function GET(req) {
  const auth = req.headers.get("authorization");
  if (auth !== \`Bearer \${process.env.CRON_SECRET}\`) return new Response(null, { status: 401 });
  await runCron();
  return new Response("done");
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (!/cron/i.test(filePath) && !/CRON_SECRET/.test(content)) return [];
    const matches = [];
    const lines = content.split("\n");
    const isCronRoute = /cron/i.test(filePath);
    const hasCronSecret = /CRON_SECRET/.test(content);
    const hasHandler = /export\s+(async\s+)?function\s+(GET|POST)|export\s+(const\s+)?(GET|POST)/.test(content);
    if (isCronRoute && hasHandler) {
      if (!hasCronSecret) {
        for (let i = 0; i < lines.length; i++) {
          if (/export\s+(async\s+)?function|export\s+(const\s+)?(GET|POST)/.test(lines[i])) {
            const start = Math.max(0, i - 1);
            const end = Math.min(lines.length, i + 3);
            matches.push({
              vulnSlug: "cron-secret-check",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: "Cron route handler without CRON_SECRET validation"
            });
            break;
          }
        }
      } else {
        for (let i = 0; i < lines.length; i++) {
          if (/CRON_SECRET/.test(lines[i])) {
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            matches.push({
              vulnSlug: "cron-secret-check",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: "CRON_SECRET check (verify not bypassable when env var unset)"
            });
          }
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/cross-tenant-id.ts
var crossTenantIdMatcher = {
  noiseTier: "precise",
  slug: "cross-tenant-id",
  description: "User-supplied IDs used in DB lookups without ownership verification \u2014 cross-tenant risk",
  filePatterns: [
    "**/services/**/endpoints/**/*.ts",
    "**/services/**/endpoint/**/*.ts",
    "**/services/**/src/index.ts",
    "**/apps/**/route.ts",
    "**/apps/**/route.*.ts",
    "**/app/api/**/*.ts"
  ],
  examples: [
    `const t = await getTeamById(parsed.body.teamId);`,
    `const u = await getUserById(req.params.userId);`,
    `const i = await getInstallationByUid(parsed.query.installationUid);`,
    `const teamId = parsed.body.teamId;`,
    `const ownerId = req.params.ownerId;`,
    `const userId = parsed.query.userId;`,
    `const installationId = parsed.body.installationId;`,
    `const configurationId = parsed.body.configurationId;`,
    `const integrationConfigurationId = req.body.integrationConfigurationId;`,
    `const t = getTeamById(install.ownerId);`,
    `const t = getTeamById(record.teamId);`,
    `const r = await findById(parsed.params.id);`,
    `const r = await findOneById(req.body.id);`,
    `const r = await findByUid(parsed.body.uid);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const patterns = [
      {
        regex: /get\w+By(Id|Uid)\s*\(\s*(parsed\.(body|query|params)|req\.(body|query|params))/,
        label: "DB lookup with user-supplied ID from request"
      },
      {
        regex: /(teamId|ownerId|userId|installationId|configurationId|integrationConfigurationId)\s*[:=]\s*(parsed|req)\.(body|query|params)/,
        label: "Tenant/user ID extracted from request input"
      },
      {
        regex: /getTeamById\s*\(\s*\w+\.(ownerId|teamId)/,
        label: "getTeamById with potentially unverified ownerId"
      },
      {
        regex: /find(One)?By(Id|Uid)\s*\(\s*(parsed|req)\./,
        label: "findById with user-supplied ID"
      }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "cross-tenant-id",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/crypto-usage.ts
var IMPORT_PATTERNS = [
  // Go standard library crypto/*
  {
    regex: /"crypto\/(?:aes|cipher|des|dsa|ecdh|ecdsa|ed25519|elliptic|hmac|md5|rand|rc4|rsa|sha1|sha256|sha512|subtle|x509|tls)"/,
    label: "Go crypto/* import"
  },
  { regex: /"golang\.org\/x\/crypto\//, label: "Go golang.org/x/crypto import" },
  // Node / JS crypto libraries
  { regex: /(?:require|from)\s*\(?\s*['"](?:node:)?crypto['"]/, label: "Node crypto import" },
  {
    regex: /(?:require|from)\s*\(?\s*['"](?:crypto-js|tweetnacl|@noble\/[\w-]+|jose|jsonwebtoken|bcrypt|bcryptjs|argon2|scrypt|tweetsodium|libsodium-wrappers|node-forge|elliptic|sjcl)['"]/,
    label: "JS crypto library import"
  },
  { regex: /crypto\.subtle\.\w+/, label: "Web Crypto API (crypto.subtle.*)" },
  // Python
  {
    regex: /^\s*(?:from|import)\s+(?:cryptography|hashlib|hmac|secrets|Crypto|nacl|jwt|passlib|bcrypt|argon2|pycryptodome)\b/m,
    label: "Python crypto import"
  }
];
var CALL_PATTERNS = [
  // Go
  { regex: /\bed25519\.(Sign|Verify|GenerateKey|NewKeyFromSeed)\s*\(/, label: "Go ed25519 op" },
  { regex: /\brsa\.(Encrypt|Decrypt|Sign|Verify)\w*\s*\(/, label: "Go RSA op" },
  { regex: /\becdsa\.(Sign|Verify|GenerateKey)\w*\s*\(/, label: "Go ECDSA op" },
  { regex: /\bhmac\.(New|Equal)\s*\(/, label: "Go HMAC op" },
  { regex: /\baes\.NewCipher\s*\(/, label: "Go AES init" },
  {
    regex: /\bcipher\.New(?:GCM|CBCEncrypter|CBCDecrypter|CFBEncrypter|CFBDecrypter|CTR|OFB)\s*\(/,
    label: "Go cipher mode"
  },
  {
    regex: /\bsubtle\.ConstantTime(?:Compare|Eq|Select|ByteEq|Copy|LessOrEq)\s*\(/,
    label: "Go subtle compare"
  },
  { regex: /\bx509\.(Parse|Create|Verify)\w*\s*\(/, label: "Go x509 op" },
  { regex: /\btls\.(Config|Certificate|Dial|Listen|Server|Client)\s*[({]/, label: "Go TLS op" },
  { regex: /\b(?:sha256|sha512|sha1|md5)\.(?:New|Sum\d*)\s*\(/, label: "Go hash op" },
  // Node / JS
  {
    regex: /\bcreate(?:Hash|Hmac|Cipher(?:iv)?|Decipher(?:iv)?|Sign|Verify|PrivateKey|PublicKey|SecretKey|DiffieHellman|ECDH)\s*\(/,
    label: "Node crypto.create*"
  },
  { regex: /\brandomBytes\s*\(/, label: "Node randomBytes" },
  { regex: /\brandomUUID\s*\(/, label: "Node randomUUID" },
  { regex: /\bpbkdf2(?:Sync)?\s*\(/, label: "Node pbkdf2" },
  { regex: /\bscrypt(?:Sync)?\s*\(/, label: "Node scrypt" },
  { regex: /\btimingSafeEqual\s*\(/, label: "Node timingSafeEqual" },
  {
    regex: /\bcrypto\.(?:sign|verify|hkdf|generateKeyPair(?:Sync)?|diffieHellman)\s*\(/,
    label: "Node crypto op"
  },
  { regex: /\bjwt\.(sign|verify|decode)\s*\(/, label: "JWT sign/verify" },
  {
    regex: /\bjose\.(SignJWT|jwtVerify|importJWK|importSPKI|importPKCS8|compactSign|compactVerify|flattenedSign|flattenedVerify|generalSign|generalVerify|EncryptJWT|jwtDecrypt|EncryptSHE|compactDecrypt|flattenedDecrypt|generalDecrypt|CompactEncrypt|FlattenedEncrypt|GeneralEncrypt)\b/,
    label: "jose lib"
  },
  // Web Crypto
  {
    regex: /\bcrypto\.subtle\.(encrypt|decrypt|sign|verify|digest|generateKey|deriveKey|deriveBits|importKey|exportKey|wrapKey|unwrapKey)\s*\(/,
    label: "Web Crypto subtle.*"
  },
  // Python
  {
    regex: /\bhashlib\.(?:md5|sha1|sha224|sha256|sha384|sha512|blake2\w*|pbkdf2_hmac)\s*\(/,
    label: "Python hashlib"
  },
  { regex: /\bhmac\.(?:new|compare_digest|HMAC)\s*\(/, label: "Python hmac" },
  {
    regex: /\bsecrets\.(token_bytes|token_hex|token_urlsafe|randbelow|choice|compare_digest|SystemRandom)\s*\(/,
    label: "Python secrets"
  }
];
var ALL_PATTERNS = [...IMPORT_PATTERNS, ...CALL_PATTERNS];
var cryptoUsageMatcher = {
  noiseTier: "normal",
  slug: "crypto-usage",
  description: "Any file that uses cryptographic primitives (sign/verify/encrypt/hash/HMAC/random/key-derivation) \u2014 wide net for AI review",
  filePatterns: ["**/*.go", "**/*.{ts,tsx,js,jsx,mjs,cjs}", "**/*.py"],
  examples: [
    `import "crypto/aes"`,
    `import "crypto/sha256"`,
    `import "golang.org/x/crypto/bcrypt"`,
    `const crypto = require('node:crypto');`,
    `import jwt from "jsonwebtoken";`,
    `import { SignJWT } from "jose";`,
    `const hash = crypto.subtle.digest("SHA-256", data);`,
    `from cryptography.hazmat.primitives import hashes`,
    `import hashlib`,
    `sig := ed25519.Sign(priv, msg)`,
    `cipher := rsa.EncryptPKCS1v15(rand, pub, msg)`,
    `r, s, err := ecdsa.Sign(rand, key, hash)`,
    `mac := hmac.New(sha256.New, key)`,
    `block, _ := aes.NewCipher(key)`,
    `gcm, _ := cipher.NewGCM(block)`,
    `if subtle.ConstantTimeCompare(a, b) == 1 { }`,
    `cert, _ := x509.ParseCertificate(der)`,
    `tls.Config{ MinVersion: tls.VersionTLS12 }`,
    `h := sha256.New()`,
    `const hash = createHash('sha256');`,
    `const buf = randomBytes(32);`,
    `const id = randomUUID();`,
    `const key = pbkdf2Sync(password, salt, 100000, 64, 'sha512');`,
    `scrypt(password, salt, 64, (err, key) => {});`,
    `if (timingSafeEqual(a, b)) ok();`,
    `const sig = jwt.sign({ id: 1 }, secret);`,
    `const out = await jose.jwtVerify(token, key);`,
    `await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, data);`,
    `import hmac
mac = hmac.new(key, msg, hashlib.sha256)`,
    `import secrets
token = secrets.token_hex(16)`,
    `import hashlib
h = hashlib.sha256(b"abc")`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/(?:^|\/)__tests__\//.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/(?:^|\/)gen\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const { regex, label } of ALL_PATTERNS) {
        if (regex.test(line)) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "crypto-usage",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 5).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/dangerous-html.ts
var dangerousHtmlMatcher = {
  noiseTier: "normal",
  slug: "dangerous-html",
  description: "dangerouslySetInnerHTML and innerHTML with source classification",
  filePatterns: ["**/*.{tsx,jsx,ts,js}"],
  examples: [
    `<div dangerouslySetInnerHTML={{ __html: html }} />`,
    `<span dangerouslySetInnerHTML={{ __html: props.body }} />`,
    `el.innerHTML = data;`,
    `node.innerHTML = result;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/dangerouslySetInnerHTML/.test(line) || /\.innerHTML\s*=/.test(line)) {
        const start = Math.max(0, i - 3);
        const end = Math.min(lines.length, i + 5);
        const context = lines.slice(start, end).join("\n");
        const isSafeScript = /\.toString\(\)/.test(context) || /IIFE|function\s*\(/.test(context);
        const isStaticString = /dangerouslySetInnerHTML.*__html:\s*['"`]/.test(context);
        const isFromProps = /props\.|children|content|html|body|text|message/i.test(context);
        const isFromFetch = /data\.|response\.|result\.|await|fetch/i.test(context);
        const isFromSearchParams = /searchParams|query|params|req\./i.test(context);
        let label;
        if (isFromSearchParams) {
          label = "dangerouslySetInnerHTML from URL/request params (HIGH RISK)";
        } else if (isFromFetch) {
          label = "dangerouslySetInnerHTML from fetched data (MEDIUM RISK)";
        } else if (isFromProps) {
          label = "dangerouslySetInnerHTML from props (trace source)";
        } else if (isSafeScript || isStaticString) {
          label = "dangerouslySetInnerHTML with static/safe content (weak candidate)";
        } else {
          label = "dangerouslySetInnerHTML (classify source)";
        }
        matches.push({
          vulnSlug: "dangerous-html",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: label
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/dart-shelf-handler.ts
var dartShelfHandlerMatcher = {
  noiseTier: "noisy",
  slug: "dart-shelf-handler",
  description: "Dart Shelf handlers and Router routes (gated on dart)",
  filePatterns: ["**/*.dart"],
  requires: { tech: ["dart"] },
  examples: [
    `final router = Router();`,
    `var app = Router()..get('/', (req) => Response.ok('hi'));`,
    `router.get('/users', listUsers);`,
    `router.post('/users', (Request req) async => Response.ok(''));`,
    `router.put('/users/<id>', updateUser);`,
    `router.patch('/users/<id>', patchUser);`,
    `router.delete('/users/<id>', deleteUser);`,
    `router.head('/health', healthCheck);`,
    `router.options('/cors', corsHandler);`,
    `router.all('/<ignored|.*>', notFound);`,
    `Response handler(Request request) { return Response.ok(''); }`,
    `Future<Response> _users(Request req) async { return Response.ok(''); }`,
    `final pipeline = Pipeline().addMiddleware(logRequests()).addHandler(router);`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "dart-shelf-handler",
      [
        {
          regex: /\bRouter\s*\(\s*\)/,
          label: "shelf_router Router() factory"
        },
        {
          regex: /\.(?:get|post|put|patch|delete|head|options|all)\s*\(\s*'[^']+'\s*,/,
          label: "router.<verb>('/path', handler)"
        },
        {
          regex: /\bRequest\s+\w+\s*\)/,
          label: "Handler signature taking shelf Request"
        },
        { regex: /\bPipeline\s*\(\s*\)\.addMiddleware\b/, label: "Pipeline().addMiddleware" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/debug-endpoint.ts
var debugEndpointMatcher = {
  noiseTier: "precise",
  slug: "debug-endpoint",
  description: "Dev/debug/test endpoints that might be reachable in production",
  filePatterns: [
    "**/api/debug/**/*.{ts,tsx}",
    "**/api/test/**/*.{ts,tsx}",
    "**/api/dev/**/*.{ts,tsx}",
    "**/api/**/debug*/*.{ts,tsx}",
    "**/api/**/*.{ts,tsx,js}",
    "**/app/api/**/*.{ts,tsx}"
  ],
  examples: [
    `// debug endpoint for inspecting state
export async function GET(req: Request) {
  return Response.json({ env: process.env });
}`,
    `// test endpoint \u2014 internal use only
export const POST = async (req) => {
  return new Response("ok");
};`,
    `// dev only handler
export function DELETE() {
  return new Response(null, { status: 204 });
}`,
    `// uses x-debug header to dump internals
export async function PUT(req) {
  if (req.headers.get("x-debug")) return Response.json(state);
  return new Response("ok");
}`,
    `// development only \u2014 do not ship
if (process.env.NODE_ENV !== 'production') {
  console.log("debug");
}
export async function GET() { return new Response("ok"); }`,
    `// x-internal toggles debug responses
export const GET = async (req) => new Response("hi");`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const isDebugPath = /\/debug|\/test\/|\/dev\/|\/internal\/|\/admin\//.test(filePath);
    const hasDebugCode = /debug.*endpoint|test.*endpoint|dev.*only|development.*only/.test(content);
    const hasDebugHeaders = /x-debug|x-test-|x-internal/.test(content);
    const hasEnvGate = /process\.env\.NODE_ENV\s*[!=]==?\s*['"]production['"]|process\.env\.NODE_ENV\s*[!=]==?\s*['"]development['"]/.test(
      content
    );
    if (!isDebugPath && !hasDebugCode && !hasDebugHeaders) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (/export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE)|export\s+(const\s+)?(GET|POST|PUT|DELETE)\s*=/.test(
        lines[i]
      )) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "debug-endpoint",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: hasEnvGate ? `Debug/test endpoint with env gate (verify ${isDebugPath ? "path" : "code"} not reachable in prod)` : `Debug/test endpoint WITHOUT env gate \u2014 may be reachable in production`
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/dev-auth-bypass.ts
var devAuthBypassMatcher = {
  noiseTier: "precise",
  slug: "dev-auth-bypass",
  description: "Development auth bypasses \u2014 dev endpoints, NODE_ENV guards, test tokens in production",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `app.post("/auth/dev", (req, res) => {
  res.json({ token: "dev-token" });
});`,
    `router.get("/dev/login", handler);`,
    `app.post("/test/auth/login", handler);`,
    `if (NODE_ENV === "development") return skipAuthMiddleware();`,
    `if (NODE_ENV === "test") return mockAuthResponse();`,
    `function shouldBypassAuth() { return skipAuthHandler() && NODE_ENV; }`,
    `if (isDev) {
  ctx.user = { id: 1, role: "admin" };
}`,
    `if (IS_TEST) return adminUser;`,
    `const token = headers.get("test-token") || "";`,
    `if (apiKey === "test_api_key_12345") return ok();`,
    `const session = createMockSession({ userId: 1 });`,
    `await autoLogin(req);`,
    `useFakeAuth(req);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const patterns = [
      // Dev auth endpoints
      {
        regex: /\/auth\/dev|\/api\/dev|\/dev\/login|\/test\/auth/,
        label: "Dev/test auth endpoint \u2014 may be reachable in production"
      },
      // NODE_ENV guards around auth
      {
        regex: /NODE_ENV.{0,40}(?:development|test).{0,80}(?:skip|bypass|disable|return|mock).{0,40}auth/i,
        label: "Auth skipped in development/test \u2014 check production guard"
      },
      {
        regex: /(?:skip|bypass|disable|mock).{0,40}auth.{0,80}NODE_ENV/i,
        label: "Auth bypass gated by NODE_ENV \u2014 check production guard"
      },
      // Explicit dev bypasses
      {
        regex: /if\s*\(\s*(?:!?\s*)?(?:isDev|isTest|isLocal|IS_DEV|IS_TEST)/,
        label: "Auth conditional on isDev/isTest flag \u2014 fails open risk"
      },
      // Test tokens accepted
      {
        regex: /test[_-]?(?:token|bearer|api[_-]?key|secret)/i,
        label: "Test token/secret reference \u2014 may be accepted in production"
      },
      // Auto-login / mock session
      {
        regex: /mock[_-]?(?:session|user|auth)|auto[_-]?login|fake[_-]?auth/i,
        label: "Mock session/auth pattern \u2014 check production guard"
      }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const trimmed = lines[i].trim();
          if (trimmed.startsWith("//") || trimmed.startsWith("*")) continue;
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "dev-auth-bypass",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/dockerfile-curl-pipe-unverified.ts
var dockerfileCurlPipeUnverifiedMatcher = {
  noiseTier: "precise",
  slug: "dockerfile-curl-pipe-unverified",
  description: "RUN curl|wget piped to shell/tar without checksum verification",
  filePatterns: ["**/Dockerfile", "**/Dockerfile.*", "**/*.Dockerfile"],
  requires: { tech: ["docker"] },
  examples: [
    `RUN curl -fsSL https://example.com/install.sh | sh`,
    `RUN curl -L https://get.docker.com/ | bash`,
    `RUN wget -qO- https://example.com/install | sh`,
    `RUN curl -L https://example.com/release.tar.gz | tar -xz`,
    `RUN wget -O- https://example.com/file.zip | unzip -`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const snippets = [];
    const statements = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      if (!/^\s*RUN\b/i.test(line)) {
        i++;
        continue;
      }
      const start = i;
      let text = line;
      while (text.trimEnd().endsWith("\\") && i + 1 < lines.length) {
        i++;
        text += "\n" + lines[i];
      }
      statements.push({ start, text });
      i++;
    }
    const PIPE = /\b(curl|wget)\b[^|\n]*\|\s*(?:sh|bash|zsh|tar\b|gunzip\b|unzip\b)/i;
    const HAS_VERIFY = /(sha256sum|sha1sum|shasum|gpg\s+--?verify|cosign\s+verify|minisign|openssl\s+dgst)/i;
    for (const stmt of statements) {
      if (!PIPE.test(stmt.text)) continue;
      if (HAS_VERIFY.test(stmt.text)) continue;
      hitLines.push(stmt.start + 1);
      const snipStart = Math.max(0, stmt.start - 1);
      const snipEnd = Math.min(lines.length, stmt.start + stmt.text.split("\n").length + 1);
      snippets.push(lines.slice(snipStart, snipEnd).join("\n"));
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "dockerfile-curl-pipe-unverified",
      lineNumbers: hitLines,
      snippet: snippets[0],
      matchedPattern: "curl|wget | sh/tar with no checksum check"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/dockerfile-from-mutable-tag.ts
var dockerfileFromMutableTagMatcher = {
  noiseTier: "precise",
  slug: "dockerfile-from-mutable-tag",
  description: "FROM line uses a mutable tag (no @sha256 digest pin)",
  filePatterns: ["**/Dockerfile", "**/Dockerfile.*", "**/*.Dockerfile"],
  requires: { tech: ["docker"] },
  examples: [
    `FROM node:20`,
    `FROM python:3.11-slim`,
    `FROM ubuntu:22.04`,
    `FROM alpine`,
    `FROM debian:bookworm AS builder`,
    `FROM --platform=linux/amd64 golang:1.21`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const snippets = [];
    const OK_BASES = /* @__PURE__ */ new Set(["scratch"]);
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const m = line.match(/^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)(?:\s+AS\s+\S+)?\s*$/i);
      if (!m) continue;
      const image = m[1];
      if (image.startsWith("$")) continue;
      if (OK_BASES.has(image)) continue;
      if (image.includes("@sha256:")) continue;
      hitLines.push(i + 1);
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 2);
      snippets.push(lines.slice(start, end).join("\n"));
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "dockerfile-from-mutable-tag",
      lineNumbers: hitLines,
      snippet: snippets[0],
      matchedPattern: "FROM without @sha256 digest"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/dockerfile-run-as-root.ts
var dockerfileRunAsRootMatcher = {
  noiseTier: "normal",
  slug: "dockerfile-run-as-root",
  description: "Final Dockerfile stage runs as root (no USER directive, or USER root)",
  filePatterns: ["**/Dockerfile", "**/Dockerfile.*", "**/*.Dockerfile"],
  requires: { tech: ["docker"] },
  examples: [
    `FROM node:20
WORKDIR /app
COPY . .
CMD ["node", "index.js"]`,
    `FROM ubuntu:22.04
RUN apt-get update
USER root
CMD ["bash"]`,
    `FROM python:3.11
USER 0
CMD ["python", "app.py"]`,
    `FROM alpine
FROM debian:bookworm
COPY --from=0 /bin/app /bin/app
CMD ["/bin/app"]`
  ],
  match(content) {
    const lines = content.split("\n");
    let finalStageStart = -1;
    let finalStageBase = "";
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(/^\s*FROM\s+(?:--platform=\S+\s+)?(\S+)/i);
      if (m) {
        finalStageStart = i;
        finalStageBase = m[1];
      }
    }
    if (finalStageStart === -1) return [];
    if (finalStageBase === "scratch") {
      const hasDirectives = lines.slice(finalStageStart + 1).some((l) => /^\s*(CMD|ENTRYPOINT|RUN)\b/i.test(l));
      if (!hasDirectives) return [];
    }
    let lastUser = null;
    for (let i = finalStageStart + 1; i < lines.length; i++) {
      const m = lines[i].match(/^\s*USER\s+(\S+)/i);
      if (m) lastUser = m[1];
    }
    const runsAsRoot = lastUser === null || /^(root|0)(:|\s|$)/.test(lastUser);
    if (!runsAsRoot) return [];
    const snipStart = Math.max(0, finalStageStart);
    const snipEnd = Math.min(lines.length, finalStageStart + 3);
    const match = {
      vulnSlug: "dockerfile-run-as-root",
      lineNumbers: [finalStageStart + 1],
      snippet: lines.slice(snipStart, snipEnd).join("\n"),
      matchedPattern: lastUser === null ? "Final stage has no USER directive" : `Final stage ends with USER ${lastUser}`
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/dotnet-aspnet-controller.ts
var dotnetAspnetControllerMatcher = {
  noiseTier: "noisy",
  slug: "dotnet-aspnet-controller",
  description: "ASP.NET Core controllers and authorization attributes (gated on .NET)",
  filePatterns: ["**/*.cs"],
  requires: { tech: ["dotnet"] },
  examples: [
    `public class UsersController : ControllerBase`,
    `public class HomeController : Controller`,
    `[ApiController]`,
    `[ ApiController ]`,
    `[Route("api/[controller]")]`,
    `[HttpGet("{id}")]`,
    `[HttpPost]`,
    `[HttpPut("{id}")]`,
    `[HttpPatch("{id}")]`,
    `[HttpDelete("{id}")]`,
    `[HttpHead]`,
    `[HttpOptions]`,
    `[AllowAnonymous]`,
    `[Authorize]`,
    `[Authorize(Roles = "Admin")]`
  ],
  match(content, filePath) {
    if (/\/(Tests|UnitTests|IntegrationTests)\//.test(filePath)) return [];
    return regexMatcher(
      "dotnet-aspnet-controller",
      [
        {
          regex: /\bclass\s+\w+\s*:\s*(?:Controller|ControllerBase)\b/,
          label: "ControllerBase / Controller subclass"
        },
        { regex: /\[\s*ApiController\s*\]/, label: "[ApiController] attribute" },
        { regex: /\[\s*Route\s*\(/, label: "[Route] attribute" },
        {
          regex: /\[\s*Http(?:Get|Post|Put|Patch|Delete|Head|Options)\s*\(?/,
          label: "[HttpMethod] attribute"
        },
        { regex: /\[\s*AllowAnonymous\s*\]/, label: "[AllowAnonymous] \u2014 opens public access" },
        { regex: /\[\s*Authorize(?:\s*\([^)]*\))?\s*\]/, label: "[Authorize] auth gate" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/dotnet-azure-function.ts
var dotnetAzureFunctionMatcher = {
  noiseTier: "noisy",
  slug: "dotnet-azure-function",
  description: "Azure Functions C# entry points (gated on Azure Functions)",
  filePatterns: ["**/*.cs"],
  requires: { tech: ["azure-functions", "dotnet"] },
  examples: [
    `[FunctionName("HttpTriggerCSharp")]`,
    `[ FunctionName ( "ProcessOrder" ) ]`,
    `[Function("MyIsolatedFunction")]`,
    `[Function ( "QueueProcessor" )]`,
    `[HttpTrigger(AuthorizationLevel.Anonymous, "get", "post")]`,
    `[HttpTrigger(AuthorizationLevel.Function, "post", Route = "items")]`,
    `[HttpTrigger(AuthorizationLevel.Admin, "delete")]`,
    `[ServiceBusTrigger("orders", Connection = "ServiceBus")]`,
    `[QueueTrigger("myqueue", Connection = "AzureWebJobsStorage")]`
  ],
  match(content, filePath) {
    if (/\/(Tests|UnitTests|IntegrationTests)\//.test(filePath)) return [];
    return regexMatcher(
      "dotnet-azure-function",
      [
        {
          regex: /\[\s*FunctionName\s*\(\s*"[^"]+"\s*\)\s*\]/,
          label: "[FunctionName(...)] attribute"
        },
        { regex: /\[\s*Function\s*\(\s*"[^"]+"\s*\)\s*\]/, label: "[Function(...)] attribute" },
        {
          regex: /\[\s*HttpTrigger\s*\(\s*AuthorizationLevel\.(Anonymous|Function|Admin)\b/,
          label: "[HttpTrigger(AuthorizationLevel.X)] \u2014 verify Anonymous is intentional"
        },
        { regex: /\[\s*ServiceBusTrigger\b|\[\s*QueueTrigger\b/, label: "queue trigger entry" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/dotnet-minimal-api.ts
var dotnetMinimalApiMatcher = {
  noiseTier: "noisy",
  slug: "dotnet-minimal-api",
  description: "ASP.NET Core minimal-API endpoint mappings (gated on .NET)",
  filePatterns: ["**/*.cs"],
  requires: { tech: ["dotnet"] },
  examples: [
    `app.MapGet("/users", () => users);`,
    `app.MapPost("/login", (LoginDto body) => Login(body));`,
    `app.MapPut("/items/{id}", UpdateItem);`,
    `app.MapPatch("/items/{id}", PatchItem);`,
    `app.MapDelete("/items/{id}", DeleteItem);`,
    `app.MapMethods("/api", new[] { "GET", "POST" }, Handler);`,
    `app.MapGet("/admin", AdminHandler).RequireAuthorization();`,
    `app.MapGet("/public", PublicHandler).AllowAnonymous();`,
    `var builder = WebApplication.CreateBuilder(args);`
  ],
  match(content, filePath) {
    if (/\/(Tests|UnitTests|IntegrationTests)\//.test(filePath)) return [];
    return regexMatcher(
      "dotnet-minimal-api",
      [
        {
          regex: /\bapp\.Map(?:Get|Post|Put|Patch|Delete|Methods)\s*\(/,
          label: "app.Map<Verb> registration"
        },
        { regex: /\.RequireAuthorization\s*\(/, label: ".RequireAuthorization() \u2014 auth gate" },
        { regex: /\.AllowAnonymous\s*\(\s*\)/, label: ".AllowAnonymous() \u2014 public route" },
        {
          regex: /\bWebApplication\.CreateBuilder\s*\(/,
          label: "WebApplication.CreateBuilder() init"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/dotnet-razor-pages.ts
var dotnetRazorPagesMatcher = {
  noiseTier: "noisy",
  slug: "dotnet-razor-pages",
  description: "Razor Pages OnGet/OnPost handlers (gated on .NET)",
  filePatterns: ["**/Pages/**/*.cshtml.cs", "**/*.cshtml.cs"],
  requires: { tech: ["dotnet"] },
  examples: [
    `public class IndexModel : PageModel`,
    `public class LoginModel : PageModel {`,
    `public Task OnGet() {`,
    `public Task<IActionResult> OnPost() {`,
    `public async Task OnGetAsync() {`,
    `public async Task<IActionResult> OnPostAsync() {`,
    `public async Task OnPutAsync() {`,
    `public Task<IActionResult> OnDeleteAsync() {`,
    `[BindProperty]`,
    `[BindProperty(SupportsGet = true)]`,
    `[ValidateAntiForgeryToken]`
  ],
  match(content, filePath) {
    if (/\/(Tests|UnitTests|IntegrationTests)\//.test(filePath)) return [];
    return regexMatcher(
      "dotnet-razor-pages",
      [
        {
          regex: /\bclass\s+\w+\s*:\s*PageModel\b/,
          label: "PageModel subclass"
        },
        {
          regex: /\bpublic\s+(?:async\s+)?(?:Task<?[^>]*>?\s+)?On(?:Get|Post|Put|Delete)(?:Async)?\s*\(/,
          label: "OnGet/OnPost handler"
        },
        { regex: /\[\s*BindProperty\b/, label: "[BindProperty] (request-bound input)" },
        {
          regex: /\[\s*ValidateAntiForgeryToken\s*\]/,
          label: "[ValidateAntiForgeryToken] CSRF guard"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/dotnet-sql-raw.ts
var dotnetSqlRawMatcher = {
  noiseTier: "normal",
  slug: "dotnet-sql-raw",
  description: 'Raw SQL across .NET DB libraries (ADO.NET SqlCommand, Dapper, EF Core FromSqlRaw) \u2014 string concat / interpolation is SQL injection (FromSqlInterpolated parameterizes correctly; only FromSqlRaw with concat or $"..." is unsafe)',
  filePatterns: ["**/*.cs"],
  requires: { tech: ["dotnet"] },
  examples: [
    `var cmd = new SqlCommand("SELECT * FROM users WHERE id = " + userId, conn);`,
    `var cmd = new SqlCommand($"SELECT * FROM users WHERE id = {userId}", conn);`,
    `command.CommandText = "DELETE FROM users WHERE id = " + id;`,
    `command.CommandText = $"UPDATE users SET role = '{role}'";`,
    `var users = connection.Query<User>($"SELECT * FROM users WHERE name = '{name}'");`,
    `connection.Execute("DELETE FROM users WHERE id = " + id);`,
    `var rows = connection.QueryAsync<int>($"SELECT id FROM users WHERE id = {id}");`,
    `var blogs = ctx.Blogs.FromSqlRaw($"SELECT * FROM Blogs WHERE Id = {id}").ToList();`,
    `ctx.Database.ExecuteSqlRaw("DELETE FROM Users WHERE Id = " + id);`,
    // SAFE counter-example: FromSqlInterpolated parameterizes correctly
    `// SAFE: ctx.Blogs.FromSqlInterpolated($"SELECT * FROM Blogs WHERE Id = {id}").ToList();`
  ],
  match(content, filePath) {
    if (/\/(Tests|UnitTests|IntegrationTests)\//.test(filePath)) return [];
    return regexMatcher(
      "dotnet-sql-raw",
      [
        // ADO.NET
        {
          regex: /\bnew\s+SqlCommand\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'new SqlCommand("..." + concat)'
        },
        {
          regex: /\bnew\s+SqlCommand\s*\(\s*\$"[^"]{0,400}\{/,
          label: 'new SqlCommand($"...{interp}...")'
        },
        {
          regex: /\bcommand\.CommandText\s*=\s*"[^"]{0,400}"\s*\+/,
          label: 'command.CommandText = "..." + concat'
        },
        {
          regex: /\bcommand\.CommandText\s*=\s*\$"[^"]{0,400}\{/,
          label: 'command.CommandText = $"...{interp}..."'
        },
        // Dapper
        {
          regex: /\bconnection\.(?:Query|QueryAsync|QueryFirst|QueryFirstOrDefault|QueryFirstAsync|Execute|ExecuteAsync|ExecuteScalar|ExecuteScalarAsync)\s*(?:<[^>]+>)?\s*\(\s*\$"[^"]{0,400}\{/,
          label: 'Dapper connection.Query/Execute with $"...{interp}..."'
        },
        {
          regex: /\bconnection\.(?:Query|Execute|ExecuteScalar)\s*(?:<[^>]+>)?\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: "Dapper connection.Query/Execute with string concat"
        },
        // Entity Framework
        {
          regex: /\bFromSqlRaw\s*\(\s*\$"[^"]{0,400}\{/,
          label: 'FromSqlRaw with $"..." \u2014 unsafe; use FromSqlInterpolated'
        },
        {
          regex: /\bFromSqlRaw\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: "FromSqlRaw with string concat"
        },
        {
          regex: /\bExecuteSqlRaw\s*\(\s*\$"/,
          label: 'ExecuteSqlRaw with $"..."'
        },
        {
          regex: /\bExecuteSqlRaw\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: "ExecuteSqlRaw with string concat"
        },
        // Generic interpolated SQL
        {
          regex: /\$"\s*(?:SELECT|INSERT|UPDATE|DELETE)[^"]{0,400}\{/,
          label: "interpolated SQL string with embedded {expr}"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/drizzle-mass-assignment.ts
var drizzleMassAssignmentMatcher = {
  noiseTier: "precise",
  slug: "drizzle-mass-assignment",
  description: "Drizzle insert/update spreading request body \u2014 column-level mass assignment risk",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["drizzle"] },
  examples: [
    `import { users } from "drizzle-orm";
await db.insert(users).values(req.body);`,
    `import { users } from "drizzle-orm";
await db.insert(users).values({ ...req.body });`,
    `import { posts } from "drizzle-orm";
await db.insert(posts).values(payload);`,
    `import { posts } from "drizzle-orm";
await db.insert(posts).values({ ...input });`,
    `import { users } from "drizzle-orm";
await db.update(users).set(body);`,
    `import { users } from "drizzle-orm";
await db.update(users).set({ ...request.body });`,
    `import { users } from "@repo/db";
await db.insert(users).values({ ...formData });`,
    `import { users } from "drizzle-orm";
await db.update(users).set({ ...data });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_DRIZZLE = /\bfrom\s+["'](?:drizzle-orm[^"']*|@repo\/db[^"']*)["']/;
    if (!HAS_DRIZZLE.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const UNTRUSTED = /(?:req(?:uest)?\.body|body|payload|input|formData|data|json|args|params)/;
    const PATTERNS2 = [
      {
        regex: new RegExp(`\\.values\\s*\\(\\s*${UNTRUSTED.source}\\s*\\)`),
        label: ".values(untrusted) \u2014 direct mass assignment"
      },
      {
        regex: new RegExp(`\\.values\\s*\\(\\s*\\{\\s*\\.\\.\\.${UNTRUSTED.source}\\b`),
        label: ".values({ ...untrusted }) \u2014 spread mass assignment"
      },
      {
        regex: new RegExp(`\\.set\\s*\\(\\s*${UNTRUSTED.source}\\s*\\)`),
        label: ".set(untrusted) \u2014 update mass assignment"
      },
      {
        regex: new RegExp(`\\.set\\s*\\(\\s*\\{\\s*\\.\\.\\.${UNTRUSTED.source}\\b`),
        label: ".set({ ...untrusted }) \u2014 spread update mass assignment"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "drizzle-mass-assignment",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/drizzle-raw-sql.ts
var drizzleRawSqlMatcher = {
  noiseTier: "precise",
  slug: "drizzle-raw-sql",
  description: "Drizzle `sql.raw()` / `sql.unsafe()` or risky interpolation \u2014 SQL injection bypass",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["drizzle"] },
  examples: [
    `import { sql } from "drizzle-orm";
await db.execute(sql.raw(userQuery));`,
    `import { sql } from "drizzle-orm";
await db.execute(sql.unsafe(userQuery));`,
    `import { eq } from "drizzle-orm";
await db.execute(sql\`SELECT * FROM users WHERE name = \${"a" + b}\`);`,
    `import { sql } from "drizzle-orm";
const orderBy = "name";
await db.execute(sql\`SELECT * FROM users ORDER BY \${\`\${orderBy}\`}\`);`,
    `import { db } from "@repo/db";
db.execute(sql.raw("SELECT * FROM " + tableName));`,
    `import { drizzle } from "drizzle-orm/node-postgres";
await conn.execute(sql.unsafe(\`DROP TABLE \${name}\`));`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_DRIZZLE = /\bfrom\s+["'](?:drizzle-orm[^"']*|@repo\/db[^"']*|drizzle-zod|drizzle-kit)["']/;
    if (!HAS_DRIZZLE.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let label;
      if (/\bsql\.\s*raw\s*\(/.test(line)) {
        label = "sql.raw() \u2014 bypasses parameterization";
      } else if (/\bsql\.\s*unsafe\s*\(/.test(line)) {
        label = "sql.unsafe() \u2014 bypasses parameterization";
      } else if (/\bsql`[^`]*\$\{[^}]*\+[^}]*\}/.test(line) || /\bsql`[^`]*\$\{`[^`]*\$\{/.test(line)) {
        label = "sql`` interpolates concatenated string \u2014 verify parameter binding";
      }
      if (!label) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 3);
      matches.push({
        vulnSlug: "drizzle-raw-sql",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: label
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/env-exposure.ts
var envExposureMatcher = {
  noiseTier: "normal",
  slug: "env-exposure",
  description: "Environment variable patterns that may expose secrets to clients",
  filePatterns: ["**/*.{ts,tsx,js,jsx}", "**/.env", "**/.env.*", "**/next.config.*"],
  examples: [
    `const k = process.env.NEXT_PUBLIC_API_SECRET;`,
    `const t = process.env.NEXT_PUBLIC_AUTH_TOKEN;`,
    `const p = process.env.NEXT_PUBLIC_USER_PASSWORD;`,
    `const c = process.env.NEXT_PUBLIC_OAUTH_CREDENTIAL;`,
    `const k = process.env.NEXT_PUBLIC_STRIPE_KEY;`,
    `"use client";
const s = process.env.API_SECRET;`,
    `'use client';
const k = process.env.PRIVATE_KEY;`,
    `"use client";
const t = process.env.AUTH_TOKEN;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/NEXT_PUBLIC_.*(SECRET|KEY|TOKEN|PASSWORD|CREDENTIAL)/i.test(line)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 2);
        matches.push({
          vulnSlug: "env-exposure",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "NEXT_PUBLIC_ variable with secret-like name"
        });
      }
      if (/process\.env\.\w*(SECRET|KEY|TOKEN|PASSWORD|CREDENTIAL|PRIVATE)/i.test(line) && /['"]use client['"]/.test(content)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 2);
        matches.push({
          vulnSlug: "env-exposure",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Secret env var accessed in 'use client' component"
        });
      }
      if (/\.env/.test(filePath)) {
        if (/^[A-Z_]+=.{8,}/.test(line) && !/^#/.test(line) && !/<|placeholder|example|xxx/i.test(line)) {
          if (/(SECRET|KEY|TOKEN|PASSWORD|CREDENTIAL|PRIVATE)/i.test(line)) {
            matches.push({
              vulnSlug: "env-exposure",
              lineNumbers: [i + 1],
              snippet: line,
              matchedPattern: "Secret value in committed .env file"
            });
          }
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/env-var-as-bool.ts
var envVarAsBoolMatcher = {
  noiseTier: "normal",
  slug: "env-var-as-bool",
  description: "Security env vars checked with truthy/falsy \u2014 'false' string is truthy in JS",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `if (process.env.DISABLE_AUTH) skipAuth();`,
    `if (!process.env.SKIP_AUTH_CHECK) doAuth();`,
    `if (process.env.BYPASS_AUTH) return next();`,
    `if (process.env.NO_AUTH) return next();`,
    `if (process.env.DISABLE_VERIFY) bypassed = true;`,
    `if (!process.env.SKIP_VALIDATE) validate();`,
    `if (process.env.BYPASS_CHECK) doStuff();`,
    `if (process.env.ENABLE_AUTH) attachAuth();`,
    `if (process.env.REQUIRE_AUTH) doAuth();`,
    `const token = process.env.MY_SECRET;`,
    `auth(process.env.API_TOKEN);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "env-var-as-bool",
      [
        {
          regex: /if\s*\(\s*!?\s*process\.env\.\w*(DISABLE|SKIP|BYPASS|NO_)\w{0,40}AUTH/i,
          label: "Security disable flag checked as truthy"
        },
        {
          regex: /if\s*\(\s*!?\s*process\.env\.\w*(DISABLE|SKIP|BYPASS|NO_)\w{0,40}(VERIFY|CHECK|VALIDATE)/i,
          label: "Verification disable flag checked as truthy"
        },
        {
          regex: /if\s*\(\s*process\.env\.\w*(ENABLE|REQUIRE)\w{0,40}AUTH\b/i,
          label: "Auth enable flag \u2014 falsy when unset"
        },
        {
          regex: /process\.env\.\w*(SECRET|TOKEN|KEY)\w*\s*[^!=?|&]/,
          label: "Secret env var used as boolean"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/erl-cowboy-handler.ts
var erlCowboyHandlerMatcher = {
  noiseTier: "noisy",
  slug: "erl-cowboy-handler",
  description: "Erlang Cowboy HTTP handlers (gated on Erlang)",
  filePatterns: ["**/*.erl"],
  requires: { tech: ["erlang"] },
  examples: [
    `init(Req, State) ->
    {ok, Req, State}.`,
    `init(Req, State) -> {cowboy_rest, Req, State}.`,
    `Dispatch = cowboy_router:compile([{'_', [{"/", hello_handler, []}]}]),`,
    `cowboy_router:compile([{Host, Routes}])`,
    `Id = cowboy_req:binding(id, Req),`,
    `Qs = cowboy_req:qs(Req),`,
    `{ok, Body, Req2} = cowboy_req:read_body(Req),`,
    `Auth = cowboy_req:header(<<"authorization">>, Req),`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "erl-cowboy-handler",
      [
        {
          regex: /\binit\s*\(\s*Req\s*,\s*State\s*\)\s*->/,
          label: "init(Req, State) \u2014 cowboy handler entry"
        },
        {
          regex: /\bcowboy_router:compile\b/,
          label: "cowboy_router:compile([...])"
        },
        { regex: /\bcowboy_req:(?:binding|qs|read_body|header)\b/, label: "cowboy_req accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/error-message-leak.ts
var errorMessageLeakMatcher = {
  noiseTier: "normal",
  slug: "error-message-leak",
  description: "Error messages returned to client \u2014 may leak internal details",
  filePatterns: [
    "**/app/api/**/route.{ts,tsx}",
    "**/app/**/route.{ts,tsx}",
    "**/pages/api/**/*.{ts,tsx}",
    "**/routes/**/*.{ts,tsx}",
    "**/endpoints/**/*.{ts,tsx}"
  ],
  examples: [
    `try { run(); } catch (err) {
  return Response.json({ error: err.message });
}`,
    `try { run(); } catch (error) {
  return NextResponse.json({ message: error.message }, { status: 500 });
}`,
    `try { run(); } catch (err) {
  return Response.json({ stack: err.stack });
}`,
    `try { run(); } catch (error) {
  return res.json({ trace: error.stack });
}`,
    `try { run(); } catch (err) {
  return res.send(err.toString());
}`,
    `try { run(); } catch (err) {
  return Response.json({ error: String(err) });
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const leakPatterns = [
      { regex: /err(or)?\.message/, label: "error.message in response" },
      { regex: /err(or)?\.stack/, label: "error.stack in response" },
      { regex: /\.toString\(\)/, label: "error.toString() in response" },
      { regex: /String\(err/, label: "String(error) in response" }
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const { regex, label } of leakPatterns) {
        if (!regex.test(line)) continue;
        const context = lines.slice(Math.max(0, i - 3), Math.min(lines.length, i + 3)).join("\n");
        if (/Response\.json|NextResponse\.json|res\.json|res\.send|res\.status|new Response|json\s*\(/.test(
          context
        )) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "error-message-leak",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: `${label} \u2014 may leak internal details to client`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/event-handler-mismatch.ts
var eventHandlerMismatchMatcher = {
  noiseTier: "normal",
  slug: "event-handler-mismatch",
  description: "Event handlers where function name contradicts event name",
  filePatterns: [
    "**/event-consumer*.{ts,js}",
    "**/handler*.{ts,js}",
    "**/subscriber*.{ts,js}",
    "**/consumer*.{ts,js}",
    "**/dispatch*.{ts,js}",
    "**/listener*.{ts,js}",
    "**/webhook*.{ts,js}",
    "**/*.{ts,js}"
  ],
  examples: [
    `switch (event.type) {
  case "user.removed":
    return userAdded(event.payload);
  case "user.added":
    return userRemoved(event.payload);
}`,
    `switch (event) {
  case "team.deleted":
    return createTeam(event.id);
}`,
    `switch (eventType) {
  case "membership.added":
    return removeMembership(id);
}`,
    `switch (event.type) {
  case "post.created":
    return deletePost(post.id);
}`,
    `switch (event.kind) {
  case "record.updated":
    return createRecord(input);
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    if (!/switch\s*\(.*event|case\s+['"].*\.(created|updated|deleted|removed|added)/i.test(content))
      return [];
    const matches = [];
    const lines = content.split("\n");
    const opposites = {
      removed: ["add", "create", "insert", "Added"],
      deleted: ["add", "create", "insert", "Added"],
      added: ["remove", "delete", "destroy", "Removed", "Deleted"],
      created: ["remove", "delete", "destroy", "Removed", "Deleted"],
      updated: ["create", "delete", "Created", "Deleted"]
    };
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const caseMatch = line.match(/case\s+['"]([\w.]+)['"]/);
      if (!caseMatch) continue;
      const eventName = caseMatch[1].toLowerCase();
      let eventAction = null;
      for (const action of Object.keys(opposites)) {
        if (eventName.includes(action)) {
          eventAction = action;
          break;
        }
      }
      if (!eventAction) continue;
      const window = lines.slice(i + 1, Math.min(lines.length, i + 6)).join("\n");
      const wrongPatterns = opposites[eventAction];
      for (const wrong of wrongPatterns) {
        const regex = new RegExp(`\\b\\w*${wrong}\\w*\\s*\\(`, "i");
        if (regex.test(window)) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 6);
          matches.push({
            vulnSlug: "event-handler-mismatch",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: `Event "${caseMatch[1]}" calls function matching "${wrong}" \u2014 possible copy-paste bug`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/ex-phoenix-controller.ts
var exPhoenixControllerMatcher = {
  noiseTier: "noisy",
  slug: "ex-phoenix-controller",
  description: "Phoenix controllers, routers, and LiveView modules (gated on Phoenix)",
  filePatterns: ["**/*.{ex,exs}"],
  requires: { tech: ["phoenix"] },
  examples: [
    `defmodule MyAppWeb.UserController do
  use MyAppWeb, :controller
end`,
    `  use MyAppWeb, :controller`,
    `  use MyAppWeb, :live_view`,
    `defmodule MyAppWeb.HomeLive do
  use MyAppWeb, :live_view
end`,
    `  get "/users", UserController, :index`,
    `  post "/users", UserController, :create`,
    `  live "/dashboard", DashboardLive, :index`,
    `  pipeline :api do
    plug :accepts, ["json"]
  end`,
    `    plug :authenticate_user`,
    `Repo.query!("SELECT * FROM users WHERE id = $1", [id])`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "ex-phoenix-controller",
      [
        {
          regex: /^\s*use\s+\w+,\s+:controller\b/m,
          label: "use ..., :controller \u2014 Phoenix controller"
        },
        {
          regex: /^\s*use\s+\w+,\s+:live_view\b/m,
          label: "use ..., :live_view"
        },
        {
          regex: /^\s*(?:get|post|put|patch|delete|live)\s+"[^"]+"\s*,/m,
          label: "router pipeline verb"
        },
        {
          regex: /^\s*pipeline\s+:\w+\s+do\b/m,
          label: "pipeline :name do \u2014 auth scope"
        },
        { regex: /\bplug\s+:\w+/, label: "plug :name (auth/middleware wiring)" },
        { regex: /\bRepo\.query!?\s*\(/, label: "Repo.query \u2014 raw SQL surface" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/expensive-api-abuse.ts
var expensiveApiAbuseMatcher = {
  noiseTier: "precise",
  slug: "expensive-api-abuse",
  description: "Endpoints calling expensive APIs (LLM, AI, paid services) that may lack abuse protection",
  filePatterns: [
    "**/app/api/**/route.{ts,tsx}",
    "**/app/**/route.{ts,tsx}",
    "**/pages/api/**/*.{ts,tsx}",
    "**/routes/**/*.{ts,tsx}",
    "**/server/**/*.{ts,tsx}",
    "**/actions/**/*.{ts,tsx}",
    "**/actions.{ts,tsx}",
    "**/*.{ts,tsx}"
  ],
  examples: [
    `export async function POST(req: Request) {
  const { text } = await generateText({ model, prompt: "hi" });
  return Response.json({ text });
}`,
    `export async function POST(req: Request) {
  const result = streamText({ model, messages: [] });
  return result.toAIStreamResponse();
}`,
    `export async function POST() {
  const out = await generateObject({ model, schema, prompt: "x" });
  return Response.json(out);
}`,
    `export const POST = async () => {
  const stream = streamObject({ model, schema, prompt: "y" });
  return new Response(stream.textStream);
};`,
    `export async function POST() {
  const v = await embed({ model, value: "hello" });
  return Response.json(v);
}`,
    `export async function POST() {
  const vs = await embedMany({ model, values: ["a", "b"] });
  return Response.json(vs);
}`,
    `"use server";
export async function ask(prompt: string) {
  return openai.chat.completions.create({ model: "gpt-4", messages: [] });
}`,
    `export async function POST() {
  return openai.completions.create({ model: "gpt-3.5", prompt: "x" });
}`,
    `export async function POST() {
  return openai.embeddings.create({ model: "text-embed", input: "x" });
}`,
    `export async function POST() {
  return openai.images.generate({ prompt: "x" });
}`,
    `export async function POST() {
  return anthropic.messages.create({ model: "claude", messages: [] });
}`,
    `export async function POST() {
  return anthropic.completions.create({ model: "claude", prompt: "x" });
}`,
    `export async function POST() {
  await fetch("https://ai-gateway.vercel.sh/v1/chat", { method: "POST" });
  return new Response("ok");
}`,
    `export async function POST() {
  await fetch("https://api.openai.com/v1/chat/completions", { method: "POST" });
  return new Response("ok");
}`,
    `export async function POST() {
  await fetch("https://api.openai.com/v1/completions", { method: "POST" });
  return new Response("ok");
}`,
    `export async function POST() {
  await fetch("https://api.openai.com/v1/embeddings", { method: "POST" });
  return new Response("ok");
}`,
    `export async function POST() {
  await fetch("https://api.openai.com/v1/images/generations", { method: "POST" });
  return new Response("ok");
}`,
    `"use server";
export async function notify() {
  await sendgrid.send({ to: "x@x.com", subject: "hi" });
}`,
    `"use server";
export async function notify() {
  await resend.emails.send({ to: "x@x.com" });
}`,
    `"use server";
export async function send() {
  await twilio.messages.create({ to: "+1", body: "hi" });
}`,
    `"use server";
export async function pay() {
  await stripe.charges.create({ amount: 100, currency: "usd" });
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const isRouteHandler = /export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)\b/.test(content) || /export\s+(const|let)\s+(GET|POST|PUT|PATCH|DELETE)\s*=/.test(content) || /export\s+default\s+(async\s+)?function/.test(content);
    const isServerAction = /['"]use server['"]/.test(content);
    if (!isRouteHandler && !isServerAction) return [];
    const expensivePatterns = [
      // AI SDK
      { regex: /\bgenerateText\s*\(/, label: "AI SDK generateText" },
      { regex: /\bstreamText\s*\(/, label: "AI SDK streamText" },
      { regex: /\bgenerateObject\s*\(/, label: "AI SDK generateObject" },
      { regex: /\bstreamObject\s*\(/, label: "AI SDK streamObject" },
      { regex: /\bembed\s*\(/, label: "AI SDK embed" },
      { regex: /\bembedMany\s*\(/, label: "AI SDK embedMany" },
      // OpenAI direct
      { regex: /openai\.chat\.completions\.create/, label: "OpenAI chat completion" },
      { regex: /openai\.completions\.create/, label: "OpenAI completion" },
      { regex: /openai\.embeddings\.create/, label: "OpenAI embedding" },
      { regex: /openai\.images\.generate/, label: "OpenAI image generation" },
      // Anthropic direct
      { regex: /anthropic\.messages\.create/, label: "Anthropic messages" },
      { regex: /anthropic\.completions\.create/, label: "Anthropic completion" },
      // AI gateway
      { regex: /ai-gateway\.vercel\.sh/, label: "Vercel AI Gateway" },
      // Generic LLM patterns
      { regex: /\/v1\/chat\/completions/, label: "Chat completions API" },
      { regex: /\/v1\/completions/, label: "Completions API" },
      { regex: /\/v1\/embeddings/, label: "Embeddings API" },
      { regex: /\/v1\/images\/generations/, label: "Image generation API" },
      // Paid service APIs
      { regex: /\bsendgrid\b.*\.send\b/i, label: "SendGrid email" },
      { regex: /\bresend\b.*\.send\b/i, label: "Resend email" },
      { regex: /\btwilio\b.*\.create\b/i, label: "Twilio SMS" },
      { regex: /\bstripe\b.*\.create\b/i, label: "Stripe API" }
    ];
    const matches = [];
    const lines = content.split("\n");
    for (const { regex, label } of expensivePatterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "expensive-api-abuse",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: `Expensive API call: ${label} \u2014 check for abuse protection (auth, rate limit, captcha)`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/fs-write-symlink-boundary.ts
var PATTERNS = [
  {
    regex: /\bfs\.(?:mkdir|writeFile|createWriteStream|copyFile|symlink|link|rename|appendFile|chmod|chown|truncate)(?:Sync)?\s*\(\s*`[^`]*\$\{/,
    label: "fs write to template-literal path"
  },
  {
    regex: /\bfsp?\.(?:mkdir|writeFile|copyFile|symlink|link|rename|appendFile|chmod|chown|truncate)\s*\(\s*`[^`]*\$\{/,
    label: "fsp/fs.promises write to template-literal path"
  },
  {
    regex: /\bfs\.(?:mkdir|writeFile|createWriteStream|copyFile|symlink|link|rename|appendFile)(?:Sync)?\s*\(\s*[A-Za-z_$][\w$]*\s*\+\s*/,
    label: "fs write to concatenated path"
  },
  {
    regex: /\bfs\.(?:mkdir|writeFile|createWriteStream|copyFile|symlink|link|rename|appendFile)(?:Sync)?\s*\(\s*path\.join\([^)]*req\./,
    label: "fs write to path.join with req.* component"
  },
  {
    regex: /\bfs\.(?:mkdir|writeFile|createWriteStream|copyFile|symlink|link|rename|appendFile)(?:Sync)?\s*\(\s*path\.resolve\([^)]*req\./,
    label: "fs write to path.resolve with req.* component"
  }
];
var HAS_BOUNDARY_HINT = /\b(?:realpath|fs\.realpath|path\.relative|startsWith\s*\(\s*(?:root|base)|resolveWritablePathWithinRoot|withinRoot|insideRoot)\b/;
var fsWriteSymlinkBoundaryMatcher = {
  noiseTier: "noisy",
  slug: "fs-write-symlink-boundary",
  description: "Filesystem write to dynamic path \u2014 verify symlink boundary check (realpath/canonical resolve)",
  filePatterns: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
  examples: [
    `fs.writeFile(\`/tmp/uploads/\${name}\`, data, () => {});`,
    `fs.mkdirSync(\`/var/data/\${userId}\`);`,
    `fs.createWriteStream(\`/cache/\${id}.bin\`);`,
    `fs.copyFileSync(\`/tmp/\${dest}\`, src);`,
    `fs.symlinkSync(target, \`/links/\${name}\`);
fs.symlinkSync(\`/links/\${name}\`, target);`,
    `fs.appendFileSync(\`/logs/\${name}.log\`, line);`,
    `fsp.writeFile(\`/data/\${id}.json\`, JSON.stringify(payload));`,
    `await fsp.copyFile(\`/tmp/\${dest}\`, src);`,
    `fs.writeFileSync(rootDir + "/" + name, data);`,
    `fs.mkdirSync(baseDir + relative);`,
    `fs.writeFileSync(path.join(uploadDir, req.body.name), buf);`,
    `fs.writeFile(path.resolve(uploadDir, req.params.id), data, () => {});`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const hasBoundaryHelper = HAS_BOUNDARY_HINT.test(content);
    const lines = content.split("\n");
    const matches = [];
    for (const { regex, label } of PATTERNS) {
      const hitLines = [];
      const snippets = [];
      for (let i = 0; i < lines.length; i++) {
        if (!regex.test(lines[i])) continue;
        if (hasBoundaryHelper) {
          const window = lines.slice(Math.max(0, i - 5), Math.min(lines.length, i + 5)).join("\n");
          if (HAS_BOUNDARY_HINT.test(window)) continue;
        }
        hitLines.push(i + 1);
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        snippets.push(lines.slice(start, end).join("\n"));
      }
      if (hitLines.length > 0) {
        matches.push({
          vulnSlug: "fs-write-symlink-boundary",
          lineNumbers: hitLines,
          snippet: snippets[0],
          matchedPattern: label
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/gcp-cloud-function.ts
var gcpCloudFunctionMatcher = {
  noiseTier: "noisy",
  slug: "gcp-cloud-function",
  description: "GCP Cloud Functions handlers (gated on gcp-cloud-functions)",
  filePatterns: ["**/*.{ts,js,mjs,cjs,py,go}"],
  requires: { tech: ["gcp-cloud-functions"] },
  examples: [
    `functions.http('helloHttp', (req, res) => { res.send("hi") })`,
    `functions.http("api", async (req, res) => { res.json({}) })`,
    `functions.cloudEvent('myEvent', (event) => {})`,
    `functions.cloudEvent("pubsubHandler", handler)`,
    `@functions_framework.http
def hello_http(request):
    return "Hello"`,
    `functions.HTTP("HelloHTTP", helloHTTP)`,
    `const auth = req.headers.authorization`,
    `const t = req.get('Authorization')`,
    `const t = req.get("Authorization")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "gcp-cloud-function",
      [
        {
          regex: /\bfunctions\.http\s*\(\s*['"][^'"]+['"]\s*,/,
          label: "functions.http('name', handler) \u2014 HTTP function"
        },
        {
          regex: /\bfunctions\.cloudEvent\s*\(/,
          label: "functions.cloudEvent('name', handler) \u2014 event function"
        },
        {
          regex: /^\s*@functions_framework\.http\b/m,
          label: "@functions_framework.http (Python)"
        },
        {
          regex: /\bfunctions\.HTTP\s*\(\s*"[^"]+"\s*,/,
          label: "functions.HTTP() (Go) registration"
        },
        {
          regex: /\breq\.(?:headers\.authorization|get\(['"]Authorization)/,
          label: "Authorization header use"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/git-provider-url-injection.ts
var gitProviderUrlInjectionMatcher = {
  noiseTier: "normal",
  slug: "git-provider-url-injection",
  description: "Git provider API URLs constructed with interpolated user input \u2014 path injection risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const url = \`https://api.github.com/repos/\${owner}/\${repo}\`;`,
    `await fetch(\`https://api.github.com/orgs/\${org}/members\`);`,
    `const link = \`https://github.com/\${user}/\${repo}/commits\`;`,
    `const url = \`https://gitlab.com/api/v4/projects/\${id}\`;`,
    `const url = \`https://bitbucket.org/api/2.0/repositories/\${slug}\`;`,
    `const u = \`https://git.example.com/repos/\${slug}\`;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "git-provider-url-injection",
      [
        { regex: /api\.github\.com[^`'"]{0,200}\$\{/, label: "GitHub API URL with interpolation" },
        { regex: /github\.com\/[^`'"]{0,200}\$\{/, label: "GitHub URL with interpolated path" },
        { regex: /gitlab\.com[^`'"]{0,200}\$\{/, label: "GitLab URL with interpolation" },
        { regex: /bitbucket\.org[^`'"]{0,200}\$\{/, label: "Bitbucket URL with interpolation" },
        {
          regex: /`https?:\/\/[^`]{0,80}git[^`]{0,80}\$\{/,
          label: "Git provider URL with interpolation"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/github-workflow-security.ts
var githubWorkflowSecurityMatcher = {
  noiseTier: "precise",
  slug: "github-workflow-security",
  description: "GitHub Actions workflow / composite-action with supply-chain or injection risk",
  filePatterns: [
    ".github/workflows/**/*.yml",
    ".github/workflows/**/*.yaml",
    ".github/actions/**/*.yml",
    ".github/actions/**/*.yaml"
  ],
  requires: { tech: ["github-actions"] },
  examples: [
    `on:
  pull_request_target:
    types: [opened]`,
    `on:
  workflow_run:
    workflows: [build]`,
    `      - uses: actions/checkout@main`,
    `      - uses: actions/setup-node@v3`,
    `        run: echo "\${{ github.event.pull_request.title }}"`,
    `        run: git log \${{ github.head_ref }}`,
    `          token: \${{ secrets.GITHUB_TOKEN }}`,
    `permissions: write-all`,
    `permissions:
  id-token: write
  contents: read`,
    `      - run: |
          echo \${{ github.event.pull_request.head.ref }}`,
    `      - run: curl -fsSL https://example.com/install.sh | sh`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      {
        regex: /^\s*-\s*pull_request_target\b|^\s*pull_request_target\s*:/,
        label: "pull_request_target trigger"
      },
      { regex: /^\s*-\s*workflow_run\b|^\s*workflow_run\s*:/, label: "workflow_run trigger" },
      {
        regex: /\buses\s*:\s*[\w-]+\/[\w./-]+@(?:main|master|v?\d+|develop)\s*$/m,
        label: "unpinned action ref (branch/major-tag)"
      },
      {
        regex: /\$\{\{\s*github\.event\.(?:pull_request|head_commit|comment|issue|review)\.\w+/,
        label: "github.event interpolation in run:"
      },
      { regex: /\$\{\{\s*github\.head_ref\s*\}\}/, label: "github.head_ref in script" },
      { regex: /\bsecrets\.[A-Z_][A-Z0-9_]+/, label: "secret reference" },
      { regex: /^\s*permissions\s*:\s*write-all\b/, label: "permissions: write-all" },
      { regex: /\bid-token\s*:\s*write\b/, label: "id-token: write (OIDC)" },
      { regex: /\brun\s*:\s*\|.*\$\{\{[^}]*\}\}/s, label: "run block interpolating expression" },
      { regex: /\bcurl\s+[^|]*\|\s*(?:sh|bash)\b/, label: "curl | sh in workflow" }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) {
      const anchor = lines.findIndex((l) => /^\s*(?:on|jobs|name)\s*:/.test(l));
      if (anchor === -1) return [];
      const s = Math.max(0, anchor);
      const e = Math.min(lines.length, anchor + 5);
      const match2 = {
        vulnSlug: "github-workflow-security",
        lineNumbers: [anchor + 1],
        snippet: lines.slice(s, e).join("\n"),
        matchedPattern: "GitHub workflow file (path-based, no specific risk pattern)"
      };
      return [match2];
    }
    const match = {
      vulnSlug: "github-workflow-security",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/go-buffalo-route.ts
var goBuffaloRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-buffalo-route",
  description: "Buffalo app routes and resources (gated on buffalo)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["buffalo"] },
  examples: [
    `app := buffalo.New(buffalo.Options{})`,
    `app.GET("/users", UsersList)`,
    `app.POST("/login", AuthCreate)`,
    `app.PUT("/items/{id}", ItemsUpdate)`,
    `app.PATCH("/profile", ProfilePatch)`,
    `app.DELETE("/items/{id}", ItemsDestroy)`,
    `app.Resource("/users", &UsersResource{})`,
    `id := c.Param("id")`,
    `req := c.Request()`,
    `if err := c.Bind(&u); err != nil {}`,
    `userID := c.Value("current_user_id")`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-buffalo-route",
      [
        {
          regex: /\bapp\.(?:GET|POST|PUT|PATCH|DELETE)\s*\(/,
          label: "Buffalo app.<VERB> registration"
        },
        { regex: /\bapp\.Resource\s*\(/, label: "app.Resource() (CRUD)" },
        { regex: /\bbuffalo\.New\s*\(/, label: "buffalo.New() init" },
        { regex: /\bc\.(?:Param|Request|Bind|Value)\b/, label: "buffalo.Context accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-chi-route.ts
var goChiRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-chi-route",
  description: "Chi router registrations and route groups (gated on Chi)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["chi"] },
  examples: [
    `r := chi.NewRouter()`,
    `r.Get("/users", listUsers)`,
    `router.Post("/login", login)`,
    `api.Put("/items/{id}", update)`,
    `r.Patch("/profile", patch)`,
    `r.Delete("/items/{id}", deleteItem)`,
    `r.Method("OPTIONS", "/cors", corsHandler)`,
    `r.Handle("/static/*", fileServer)`,
    `r.HandleFunc("/health", healthHandler)`,
    `r.Route("/admin", func(r chi.Router) {})`,
    `r.Group(func(r chi.Router) {})`,
    `r.Mount("/api", apiRouter())`,
    `id := chi.URLParam(r, "id")`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-chi-route",
      [
        {
          regex: /\b(?:r|router|api)\.(?:Get|Post|Put|Patch|Delete|Method|Handle|HandleFunc)\s*\(/,
          label: "Chi method registration"
        },
        { regex: /\bchi\.NewRouter\s*\(\s*\)/, label: "chi.NewRouter() init" },
        { regex: /\.Route\s*\(/, label: "Chi .Route (subroute scope)" },
        { regex: /\.Group\s*\(/, label: "Chi .Group (middleware scope)" },
        { regex: /\.Mount\s*\(/, label: "Chi .Mount (subrouter \u2014 middleware inheritance gotcha)" },
        { regex: /\bchi\.URLParam\s*\(/, label: "chi.URLParam (untrusted input)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-cobra-command.ts
var goCobraCommandMatcher = {
  noiseTier: "noisy",
  slug: "go-cobra-command",
  description: "Cobra CLI commands \u2014 privileged-CLI surface (gated on cobra)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["cobra"] },
  examples: [
    `var rootCmd = &cobra.Command{`,
    `cmd := &cobra.Command{Use: "deploy"}`,
    `	Run: func(cmd *cobra.Command, args []string) {`,
    `	RunE: func(cmd *cobra.Command, args []string) error {`,
    `	PreRun: func(cmd *cobra.Command, args []string) {`,
    `	PostRun: func(cmd *cobra.Command, args []string) {`,
    `rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file")`,
    `rootCmd.PersistentFlags().BoolVar(&verbose, "verbose", false, "verbose output")`,
    `rootCmd.PersistentFlags().IntVar(&port, "port", 8080, "port number")`,
    `rootCmd.AddCommand(deployCmd)`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-cobra-command",
      [
        { regex: /&cobra\.Command\s*\{/, label: "cobra.Command{} declaration" },
        {
          regex: /\b(?:Run|RunE|PreRun|PostRun)\s*:\s*func\b/,
          label: "Run/RunE handler \u2014 privileged action body"
        },
        {
          regex: /\.PersistentFlags\s*\(\s*\)\.(?:String|Bool|Int)Var/,
          label: "PersistentFlags()"
        },
        { regex: /\.AddCommand\s*\(/, label: "AddCommand registration" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-command-injection.ts
var goCommandInjectionMatcher = {
  noiseTier: "precise",
  slug: "go-command-injection",
  description: "Go exec.Command with potentially dynamic arguments",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `cmd := exec.Command("sh", "-c", userInput)`,
    `out, err := exec.Command("ls", dir).Output()`,
    `cmd := exec.CommandContext(ctx, "git", "clone", repoURL)`,
    `err := syscall.Exec("/bin/sh", args, env)`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-command-injection",
      [
        { regex: /exec\.Command\s*\(/, label: "exec.Command" },
        { regex: /exec\.CommandContext\s*\(/, label: "exec.CommandContext" },
        { regex: /syscall\.Exec\s*\(/, label: "syscall.Exec" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-echo-route.ts
var goEchoRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-echo-route",
  description: "Echo (labstack) route registrations (gated on Echo)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["echo"] },
  examples: [
    `e := echo.New()`,
    `e.GET("/users", listUsers)`,
    `app.POST("/login", login)`,
    `server.PUT("/items/:id", update)`,
    `g.PATCH("/profile", patch)`,
    `e.DELETE("/items/:id", delete)`,
    `e.Any("/proxy", proxy)`,
    `e.Match([]string{"GET", "POST"}, "/legacy", legacy)`,
    `api := e.Group("/api")`,
    `id := c.Param("id")`,
    `q := c.QueryParam("q")`,
    `name := c.FormValue("name")`,
    `if err := c.Bind(&u); err != nil {}`,
    `req := c.Request()`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-echo-route",
      [
        {
          regex: /\b(?:e|app|server|g)\.(?:GET|POST|PUT|PATCH|DELETE|Any|Match)\s*\(/,
          label: "Echo method registration"
        },
        { regex: /\b(?:e|app|server)\.Group\s*\(/, label: "Echo .Group (auth scope)" },
        { regex: /\becho\.New\s*\(\s*\)/, label: "echo.New() init" },
        {
          regex: /\bc\.(?:Param|QueryParam|FormValue|Bind|Request)\b/,
          label: "Request accessor (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-embed-asset.ts
var goEmbedAssetMatcher = {
  noiseTier: "precise",
  slug: "go-embed-asset",
  description: "Go //go:embed directive (binary assets bundled into the program)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `//go:embed kernel.bin
var kernelImage []byte`,
    `//go:embed rootfs.tar.gz
var rootfs []byte`,
    `//go:embed assets/*
var assets embed.FS`,
    `//go:embed templates/index.html
var indexHTML []byte`,
    `//go:embed config.yaml
var configBytes []byte`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    if (/(?:^|\/)gen\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(/^\s*\/\/go:embed\s+(.+?)\s*$/);
      if (!m) continue;
      hitLines.push(i + 1);
      labels.add(m[1].slice(0, 60));
      if (firstContext === void 0) {
        const s = Math.max(0, i - 2);
        const e = Math.min(lines.length, i + 4);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "go-embed-asset",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(" | ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/go-fiber-route.ts
var goFiberRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-fiber-route",
  description: "Fiber route registrations (gated on Fiber)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["fiber"] },
  examples: [
    `app := fiber.New()`,
    `app.Get("/users", listUsers)`,
    `api.Post("/login", login)`,
    `router.Put("/items/:id", update)`,
    `g.Patch("/profile", patch)`,
    `app.Delete("/items/:id", deleteItem)`,
    `app.All("/proxy", proxy)`,
    `v1 := app.Group("/v1")`,
    `q := c.Query("q")`,
    `id := c.Params("id")`,
    `if err := c.BodyParser(&u); err != nil {}`,
    `body := c.Body()`,
    `auth := c.Get("Authorization")`,
    `name := c.FormValue("name")`,
    `session := c.Cookies("session")`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-fiber-route",
      [
        {
          regex: /\b(?:app|api|router|g)\.(?:Get|Post|Put|Patch|Delete|All)\s*\(/,
          label: "Fiber method registration"
        },
        { regex: /\bfiber\.New\s*\(/, label: "fiber.New() init" },
        { regex: /\.Group\s*\(/, label: "Fiber .Group (auth scope)" },
        {
          regex: /\bc\.(?:Query|Params|Body(?:Parser)?|Get|FormValue|Cookies)\b/,
          label: "Request accessor (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-gin-route.ts
var goGinRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-gin-route",
  description: "Gin route registrations and group middleware (gated on Gin)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["gin"] },
  examples: [
    `r := gin.Default()`,
    `engine := gin.New()`,
    `r.GET("/users", listUsers)`,
    `router.POST("/login", loginHandler)`,
    `api.PUT("/items/:id", updateItem)`,
    `v1.PATCH("/profile", patchProfile)`,
    `engine.DELETE("/sessions/:id", logout)`,
    `r.Any("/proxy", proxyHandler)`,
    `r.Handle("OPTIONS", "/cors", corsHandler)`,
    `admin := r.Group("/admin")`,
    `id := c.Query("id")`,
    `name := c.Param("name")`,
    `email := c.PostForm("email")`,
    `auth := c.GetHeader("Authorization")`,
    `if err := c.ShouldBindJSON(&body); err != nil {}`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-gin-route",
      [
        {
          regex: /\b(?:r|router|engine|api|v\d+)\.(?:GET|POST|PUT|PATCH|DELETE|Any|Handle)\s*\(/,
          label: "Gin method registration"
        },
        { regex: /\.Group\s*\(/, label: "Gin .Group (middleware scope)" },
        { regex: /gin\.Default\s*\(\s*\)|gin\.New\s*\(\s*\)/, label: "Gin engine init" },
        {
          regex: /\bc\.(?:Query|Param|PostForm|GetHeader|ShouldBind\w*)\b/,
          label: "Request data accessor (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-gorilla-route.ts
var goGorillaRouteMatcher = {
  noiseTier: "noisy",
  slug: "go-gorilla-route",
  description: "Gorilla mux router registrations (gated on gorilla)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["gorilla"] },
  examples: [
    `r := mux.NewRouter()`,
    `r.HandleFunc("/users", listUsers)`,
    `router.HandleFunc("/login", login).Methods("POST")`,
    `s.HandleFunc("/items/{id}", updateItem).Methods("PUT")`,
    `r.HandleFunc("/items/{id}", patchItem).Methods("PATCH")`,
    `r.HandleFunc("/items/{id}", deleteItem).Methods("DELETE")`,
    `api := r.PathPrefix("/api").Subrouter()`,
    `vars := mux.Vars(r)`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-gorilla-route",
      [
        {
          regex: /\bmux\.NewRouter\s*\(\s*\)/,
          label: "mux.NewRouter() init"
        },
        {
          regex: /\.HandleFunc\s*\(\s*"[^"]+"\s*,/,
          label: "router.HandleFunc('/path', handler)"
        },
        { regex: /\.Methods\s*\(\s*"(?:GET|POST|PUT|PATCH|DELETE)"/, label: ".Methods('VERB')" },
        { regex: /\.PathPrefix\s*\(/, label: ".PathPrefix() subroute scope" },
        { regex: /\bmux\.Vars\s*\(\s*r\s*\)/, label: "mux.Vars(r) (untrusted input)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-http-handler.ts
var goHttpHandlerMatcher = {
  noiseTier: "normal",
  slug: "go-http-handler",
  description: "Go HTTP handler functions \u2014 entry points for investigation (weak candidate)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `http.HandleFunc("/users", usersHandler)`,
    `http.Handle("/api/", apiHandler)`,
    `mux.HandleFunc("/login", loginHandler)`,
    `mux.Handle("/static/", fs)`,
    `r.GET("/users/:id", getUser)`,
    `router.POST("/items", createItem)`,
    `app.PUT("/users/:id", updateUser)`,
    `e.DELETE("/items/:id", deleteItem)`,
    `func usersHandler(w http.ResponseWriter, r *http.Request) {`,
    `func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-http-handler",
      [
        { regex: /http\.HandleFunc\s*\(/, label: "http.HandleFunc registration" },
        { regex: /http\.Handle\s*\(/, label: "http.Handle registration" },
        { regex: /mux\.Handle(Func)?\s*\(/, label: "mux handler registration" },
        { regex: /\.GET\s*\(|\.POST\s*\(|\.PUT\s*\(|\.DELETE\s*\(/, label: "HTTP method handler" },
        {
          regex: /func\s+\w+\s*\(\s*w\s+http\.ResponseWriter.*r\s+\*http\.Request/,
          label: "HTTP handler function signature"
        },
        { regex: /ServeHTTP\s*\(/, label: "ServeHTTP implementation" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-sql-raw.ts
var goSqlRawMatcher = {
  noiseTier: "normal",
  slug: "go-sql-raw",
  description: "Raw SQL across Go DB libraries (database/sql, GORM, sqlx, pgx) \u2014 fmt.Sprintf or + concatenation into queries is SQL injection",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `rows, err := db.Query("SELECT * FROM users WHERE id = " + userId)`,
    `db.QueryRow(fmt.Sprintf("SELECT * FROM x WHERE y = '%s'", name))`,
    `db.Exec("DELETE FROM users WHERE id = " + id)`,
    `db.Raw("SELECT * FROM users WHERE id = " + id).Scan(&user)`,
    `db.Raw(fmt.Sprintf("UPDATE users SET role = '%s'", role)).Exec()`,
    `db.Where("name = '" + name + "'").First(&user)`,
    `db.Where(fmt.Sprintf("id = %d", id)).First(&u)`,
    `err := sqlxDb.Select(&users, "SELECT * FROM users WHERE name = '" + name + "'")`,
    `row := pool.QueryRow(ctx, "SELECT id FROM users WHERE email = '" + email + "'")`,
    `conn.QueryRowContext(ctx, fmt.Sprintf("SELECT * FROM t WHERE id = %d", id))`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-sql-raw",
      [
        // database/sql
        {
          regex: /\bdb\.(?:Query|QueryRow|Exec|QueryContext|QueryRowContext|ExecContext)\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: "database/sql Query/Exec with string concat"
        },
        {
          regex: /\bdb\.(?:Query|QueryRow|Exec)\s*\(\s*fmt\.Sprintf\s*\(/,
          label: "database/sql Query/Exec with fmt.Sprintf"
        },
        // GORM
        {
          regex: /\bdb\.Raw\s*\(\s*fmt\.Sprintf\s*\(/,
          label: "GORM db.Raw with fmt.Sprintf"
        },
        {
          regex: /\bdb\.Raw\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: "GORM db.Raw with string concat"
        },
        {
          regex: /\bdb\.Exec\s*\(\s*fmt\.Sprintf\s*\(/,
          label: "GORM db.Exec with fmt.Sprintf"
        },
        {
          regex: /\bdb\.Where\s*\(\s*fmt\.Sprintf\s*\(/,
          label: "GORM db.Where with fmt.Sprintf"
        },
        {
          regex: /\bdb\.Where\s*\(\s*"[^"]{0,400}=\s*'?\s*"\s*\+/,
          label: "GORM db.Where with string concat"
        },
        // sqlx
        {
          regex: /\bdb\.(?:Select|Get|QueryxContext|NamedQuery)\s*\(\s*&?\w*,?\s*"[^"]{0,400}"\s*\+/,
          label: "sqlx Select/Get/Queryx with string concat"
        },
        {
          regex: /\bsqlx\.MustExec\s*\(\s*\w+\s*,\s*fmt\.Sprintf/,
          label: "sqlx.MustExec with fmt.Sprintf"
        },
        // pgx
        {
          regex: /\b(?:conn|pool)\.Query(?:Row)?(?:Context)?\s*\(\s*\w*,?\s*"[^"]{0,400}"\s*\+/,
          label: "pgx conn/pool.Query with string concat"
        },
        {
          regex: /\b(?:conn|pool)\.Query(?:Row)?(?:Context)?\s*\(\s*\w*,?\s*fmt\.Sprintf/,
          label: "pgx conn/pool.Query with fmt.Sprintf"
        },
        {
          regex: /\bpgx\.Connect\s*\(/,
          label: "pgx.Connect (informational signal)"
        },
        // Generic Go SQL
        {
          regex: /"\s*(?:SELECT|INSERT|UPDATE|DELETE)[^"]{0,400}"\s*\+\s*\w/,
          label: "SQL keyword string literal followed by concat"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/go-ssrf.ts
var goSsrfMatcher = {
  noiseTier: "normal",
  slug: "go-ssrf",
  description: "Go HTTP requests with string-concatenated or formatted URLs \u2014 SSRF risk",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `resp, err := http.Get(baseURL + path)`,
    `resp, err := http.Post(host + "/api", "application/json", body)`,
    `resp, err := http.Head("https://" + target)`,
    `req, err := http.NewRequest("GET", fmt.Sprintf("https://%s/api", host), nil)`,
    `req, err := http.NewRequest("POST", baseURL + path, body)`,
    `u, err := url.Parse(scheme + "://" + host)`,
    `endpoint := fmt.Sprintf("https://api.example.com/users/%s", userID)`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    return regexMatcher(
      "go-ssrf",
      [
        { regex: /http\.(Get|Post|Head)\s*\(.*\+/, label: "http.Get/Post with string concat URL" },
        {
          regex: /http\.NewRequest\s*\(.*fmt\.Sprintf/,
          label: "http.NewRequest with formatted URL"
        },
        { regex: /http\.NewRequest\s*\(.*\+/, label: "http.NewRequest with concatenated URL" },
        { regex: /url\.Parse\s*\(.*\+/, label: "url.Parse with concatenated string" },
        { regex: /fmt\.Sprintf\s*\(\s*"https?:\/\//, label: "URL built via fmt.Sprintf" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/iam-permissions.ts
var iamPermissionsMatcher = {
  noiseTier: "normal",
  slug: "iam-permissions",
  description: "withAuthentication/IAM permission checks \u2014 audit for correct Action/Resource pairs",
  filePatterns: [
    "**/app/api/**/route.{ts,tsx}",
    "**/app/**/actions.{ts,tsx}",
    "**/api/**/*.{ts,tsx}"
  ],
  examples: [
    `export const POST = withAuthentication(handler, opts);`,
    `const wrapped = withAuthentication(handler);`,
    `const a = Action.READ_PROJECT.with(Resource.PROJECT);`,
    `if (Action.UPDATE_TEAM && Resource.TEAM) ok();`,
    `const opts = { permissions: [Action.READ.PROJECT] };`,
    `permissions: [`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const patterns = [
      {
        regex: /withAuthentication\s*\(/,
        label: "withAuthentication IAM wrapper (verify permissions)"
      },
      {
        regex: /Action\.\w+.*Resource\.\w+/,
        label: "IAM Action/Resource pair (verify correctness)"
      },
      {
        regex: /permissions:\s*\[/,
        label: "Permissions array (verify completeness)"
      }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "iam-permissions",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/insecure-crypto.ts
var insecureCryptoMatcher = {
  noiseTier: "noisy",
  slug: "insecure-crypto",
  description: "Weak cryptographic algorithms and insecure random number generation",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `crypto.createHash("md5").update(s).digest();`,
    `crypto.createHash('sha1').update(s);`,
    `crypto.createCipher("aes", key);`,
    `const cipher = "DES";`,
    `const algo = "RC4";`,
    `const algo = "Blowfish";`,
    `const h = md5(input);`,
    `if (computed === hmac) { ok(); }`,
    `if (digest === expected) { return; }`,
    `if (signature == provided) { return; }`,
    `const token = Math.random().toString(36);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const results = regexMatcher(
      "insecure-crypto",
      [
        { regex: /createHash\s*\(\s*['"]md5['"]/, label: "MD5 hash" },
        { regex: /createHash\s*\(\s*['"]sha1['"]/, label: "SHA1 hash" },
        { regex: /createCipher\s*\(/, label: "deprecated createCipher (use createCipheriv)" },
        { regex: /DES|RC4|Blowfish/i, label: "weak cipher algorithm" },
        { regex: /\bmd5\s*\(/, label: "MD5 function call" },
        {
          regex: /===?\s*.{0,40}\bhmac\b|\bhmac\b.{0,40}===?/,
          label: "Timing-unsafe HMAC comparison (use timingSafeEqual)"
        },
        {
          regex: /===?\s*.{0,40}\bdigest\b|\bdigest\b.{0,40}===?/,
          label: "Timing-unsafe digest comparison"
        },
        {
          regex: /===?\s*.{0,40}\bsignature\b|\bsignature\b.{0,40}===?/,
          label: "Timing-unsafe signature comparison"
        }
      ],
      content
    );
    const securityContext = /\b(token|secret|key|password|nonce|salt|session|csrf|auth|credential|hash)\b/i;
    if (securityContext.test(content)) {
      results.push(
        ...regexMatcher(
          "insecure-crypto",
          [{ regex: /Math\.random\s*\(/, label: "Math.random in security context" }],
          content
        )
      );
    }
    return results;
  }
};

// vendor/deepsec-scanner/matchers/ios-url-scheme.ts
var iosUrlSchemeMatcher = {
  noiseTier: "noisy",
  slug: "ios-url-scheme",
  description: "iOS URL scheme / universal-link entry points and handlers (gated on iOS)",
  filePatterns: ["**/Info.plist", "**/*.swift", "**/*.m"],
  requires: { tech: ["ios"] },
  examples: [
    `<key>CFBundleURLSchemes</key>
<array>
  <string>myapp</string>
</array>`,
    `<key>CFBundleURLSchemes</key>`,
    `<key>NSUserActivityTypes</key>
<array><string>com.example.action</string></array>`,
    `<key>NSUserActivityTypes</key>`,
    `func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey: Any] = [:]) -> Bool { return true }`,
    `func application(_ application: UIApplication, open url: URL) -> Bool { return false }`,
    `func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {}`,
    `let webView = WKWebView(frame: .zero)`,
    `let view = UIWebView()`
  ],
  match(content, filePath) {
    if (/\/(Tests|tests|build)\//i.test(filePath)) return [];
    return regexMatcher(
      "ios-url-scheme",
      [
        {
          regex: /<key>CFBundleURLSchemes<\/key>/,
          label: "CFBundleURLSchemes \u2014 registers URL handler"
        },
        {
          regex: /<key>NSUserActivityTypes<\/key>/,
          label: "NSUserActivityTypes \u2014 universal links"
        },
        {
          regex: /func\s+application\s*\([^)]*open\s+url\s*:\s*URL/,
          label: "application(_:open url:) \u2014 URL entry point"
        },
        {
          regex: /func\s+scene\s*\([^)]*openURLContexts\b/,
          label: "scene(_:openURLContexts:) \u2014 scene URL entry"
        },
        {
          regex: /\bWKWebView\b|\bUIWebView\b/,
          label: "WebView surface \u2014 review JS bridge / file:// loads"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-astro-endpoint.ts
var jsAstroEndpointMatcher = {
  noiseTier: "noisy",
  slug: "js-astro-endpoint",
  description: "Astro API endpoints and SSR routes (gated on Astro)",
  filePatterns: ["**/pages/**/*.{ts,js}", "**/pages/api/**/*.{ts,js}", "**/src/pages/**/*.astro"],
  requires: { tech: ["astro"] },
  examples: [
    `export const GET: APIRoute = async ({ request }) => {}`,
    `export async function POST({ request }) { return new Response(null) }`,
    `export const PUT = ({ request }) => {}`,
    `export function DELETE({ params }) {}`,
    `export const ALL: APIRoute = async ({ request }) => {}`,
    `const url = Astro.request.url`,
    `const token = Astro.cookies.get("session")`,
    `const id = Astro.params.id`,
    `export const prerender = false`,
    `cookies.set("session", value, { httpOnly: true })`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "js-astro-endpoint",
      [
        {
          regex: /export\s+(?:async\s+)?(?:const|function)\s+(GET|POST|PUT|PATCH|DELETE|ALL)\b/,
          label: "Astro endpoint method export"
        },
        { regex: /\bAstro\.(?:request|cookies|params|url)\b/, label: "Astro.* request accessor" },
        { regex: /\bexport\s+const\s+prerender\s*=/, label: "prerender flag (SSR / SSG split)" },
        { regex: /\bSetCookie\s*\(|cookies\.set\s*\(/, label: "cookie write \u2014 auth surface" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-bullmq-processor.ts
var jsBullmqProcessorMatcher = {
  noiseTier: "noisy",
  slug: "js-bullmq-processor",
  description: "BullMQ workers and queue processors \u2014 background-job auth-gap surface (gated on bullmq)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["bullmq"] },
  examples: [
    `const worker = new Worker('emails', async (job) => {});`,
    `new Worker("payments", processPayment, { connection })`,
    `const queue = new Queue('emails', { connection })`,
    `new Queue("notifications")`,
    `queue.process(async (job) => { return doWork(job) })`,
    `const { userId, payload } = job.data;`,
    `console.log(job.data.email)`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-bullmq-processor",
      [
        { regex: /new\s+Worker\s*\(\s*['"][^'"]+['"]\s*,/, label: "new Worker('queue', handler)" },
        { regex: /new\s+Queue\s*\(\s*['"][^'"]+['"]/, label: "new Queue() declaration" },
        {
          regex: /\.process\s*\(\s*async\s*\(\s*job\b/,
          label: "queue.process(async job => ...) handler body"
        },
        { regex: /\bjob\.data\b/, label: "job.data \u2014 payload trust boundary" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-bun-serve.ts
var jsBunServeMatcher = {
  noiseTier: "noisy",
  slug: "js-bun-serve",
  description: "Bun.serve fetch handlers \u2014 entry-point surface (gated on bun)",
  filePatterns: ["**/*.{ts,js,mjs}"],
  requires: { tech: ["bun"] },
  examples: [
    `Bun.serve({
  fetch(req) { return new Response("hi") }
})`,
    `Bun.serve({ port: 3000, async fetch(req) { return new Response() } })`,
    `async fetch(req) { return new Response("ok") }`,
    `fetch(request, server) { return new Response() }`,
    `const url = request.url`,
    `const method = request.method`,
    `const auth = request.headers.get("authorization")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-bun-serve",
      [
        { regex: /\bBun\.serve\s*\(\s*\{/, label: "Bun.serve({ fetch(req) ... })" },
        {
          regex: /(?:async\s+)?fetch\s*\(\s*req(?:uest)?\s*[,)]/,
          label: "fetch(req) handler body"
        },
        { regex: /\brequest\.(?:url|headers|method)\b/, label: "request.* accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-deno-route.ts
var jsDenoRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-deno-route",
  description: "Deno HTTP server / Oak router handlers (gated on deno)",
  filePatterns: ["**/*.{ts,tsx}"],
  requires: { tech: ["deno"] },
  examples: [
    `Deno.serve((req) => new Response("hi"))`,
    `Deno.serve({ port: 8000 }, handler)`,
    `router.get("/users", (ctx) => {})`,
    `router.post('/api/users', createUser)`,
    `router.use(authMiddleware)`,
    `router.delete("/u/:id", removeUser)`,
    `import { Application, Router } from "https://deno.land/x/oak/mod.ts";`,
    `const url = ctx.request.url;`,
    `const body = await ctx.request.body().value`,
    `const auth = ctx.request.headers.get("Authorization")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "js-deno-route",
      [
        { regex: /\bDeno\.serve\s*\(/, label: "Deno.serve() entry point" },
        {
          regex: /\brouter\.(?:get|post|put|patch|delete|all|use)\s*\(/,
          label: "Oak router method"
        },
        {
          regex: /import\s*\{[^}]*\bApplication\b[^}]*\}\s*from\s*['"]https?:\/\/deno\.land\/x\/oak/,
          label: "Oak Application import"
        },
        { regex: /\bctx\.request\.(?:url|body|headers)\b/, label: "Oak ctx.request accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-express-route.ts
var jsExpressRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-express-route",
  description: "Express.js route registrations \u2014 entry points (weak candidate, gated on Express)",
  filePatterns: ["**/*.{ts,js,mjs,cjs,tsx}"],
  requires: { tech: ["express"] },
  examples: [
    `app.get("/users", (req, res) => res.json({}));`,
    `app.post('/login', async (req, res, next) => {})`,
    `app.put("/items/:id", handler);`,
    `app.delete("/x", handler)`,
    `app.all("*", catchAll)`,
    `router.use(authMiddleware);`,
    `router.get("/health", (req, res) => res.send("ok"))`,
    `const r = express.Router();`,
    `function handle(req, res, next) { res.send(""); }`,
    `const h = ( req , res , next ) => res.end();`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-express-route",
      [
        {
          regex: /\b(?:app|router)\.(?:get|post|put|patch|delete|all|use)\s*\(/,
          label: "app/router method registration"
        },
        { regex: /express\.Router\s*\(/, label: "express.Router() factory" },
        {
          regex: /\(\s*req\s*,\s*res(?:\s*,\s*next)?\s*\)\s*=>/,
          label: "(req, res) handler signature"
        },
        {
          regex: /function\s+\w+\s*\(\s*req\s*,\s*res(?:\s*,\s*next)?\s*\)/,
          label: "function (req, res) handler"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-fastify-route.ts
var jsFastifyRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-fastify-route",
  description: "Fastify route registrations \u2014 entry points (weak candidate, gated on Fastify)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["fastify"] },
  examples: [
    `fastify.get("/", async () => "ok");`,
    `fastify.post('/users', handler)`,
    `app.put("/items/:id", async (req, reply) => {});`,
    `instance.register(authPlugin);`,
    `server.route({ method: "POST", url: "/x", handler })`,
    `app.route({ method: 'GET', url: '/y', handler });`,
    `fastify.addHook("preHandler", async (request, reply) => {});`,
    `app.addHook('onRequest', authHook)`,
    `instance.addHook("preValidation", validate);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-fastify-route",
      [
        {
          regex: /\b(?:fastify|instance|app|server)\.(?:get|post|put|patch|delete|head|options|route|register)\s*\(/,
          label: "fastify method/route/register call"
        },
        {
          regex: /\.route\s*\(\s*\{[\s\S]*?method\s*:/,
          label: "fastify .route({ method, ... }) form"
        },
        {
          regex: /addHook\s*\(\s*['"](?:onRequest|preHandler|preValidation)['"]/,
          label: "auth-relevant lifecycle hook"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-graphql-resolver.ts
var jsGraphqlResolverMatcher = {
  noiseTier: "noisy",
  slug: "js-graphql-resolver",
  description: "GraphQL resolvers (Apollo / Yoga / Mercurius) \u2014 entry-point surface (gated on graphql)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["graphql"] },
  examples: [
    `const resolvers = { Query: { user: () => null } }`,
    `const resolver = { Query: { me: () => null } }`,
    `Mutation: { createUser: async (_p, args) => ({}) }`,
    `Subscription: { onMessage: { subscribe: () => pubsub.asyncIterator("MSG") } }`,
    `@Query(() => User)
  async user() {}`,
    `@Mutation(() => Boolean)
  async deleteUser() {}`,
    `@Resolver(() => User)
class UserResolver {}`,
    `const userId = context.userId;`,
    `if (!context.user) throw new Error("unauth")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-graphql-resolver",
      [
        {
          regex: /\bresolvers?\s*[:=]\s*\{\s*Query\s*:/,
          label: "resolvers Query map"
        },
        { regex: /\bMutation\s*:\s*\{/, label: "Mutation resolver map" },
        { regex: /\bSubscription\s*:\s*\{/, label: "Subscription resolver" },
        {
          regex: /@(?:Query|Mutation|Resolver)\s*\(/,
          label: "type-graphql / Nest GraphQL decorator"
        },
        { regex: /\bcontext\.\w+/, label: "context.* (auth identity carrier \u2014 confirm wiring)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-hapi-route.ts
var jsHapiRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-hapi-route",
  description: "Hapi server.route configurations (gated on Hapi)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["hapi"] },
  examples: [
    `const server = Hapi.server({ port: 3000 });`,
    `server.route({ method: "GET", path: "/", handler });`,
    `server.route({
  method: 'POST',
  path: '/login',
  handler,
});`,
    `server.route({ method: "GET", path: "/x", options: { auth: false } });`,
    `options: { auth: 'jwt' }`,
    `strategy: "session"`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-hapi-route",
      [
        {
          regex: /\bserver\.route\s*\(\s*\{/,
          label: "server.route({ method, path, handler })"
        },
        { regex: /Hapi\.server\s*\(/, label: "Hapi.server() init" },
        { regex: /options:\s*\{\s*auth:/, label: "route auth option (verify scope)" },
        { regex: /strategy\s*:\s*['"][^'"]+['"]/, label: "auth strategy declaration" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-hono-route.ts
var jsHonoRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-hono-route",
  description: "Hono route registrations \u2014 entry points (weak candidate, gated on Hono)",
  filePatterns: ["**/*.{ts,js,mjs}"],
  requires: { tech: ["hono"] },
  examples: [
    `const app = new Hono();`,
    `app.get("/users", (c) => c.json({}))`,
    `app.post('/login', async (c) => {})`,
    `app.put("/items/:id", handler);`,
    `app.delete("/x", handler)`,
    `app.use("*", authMiddleware);`,
    `router.all('/health', h)`,
    `c.req.query("page")`,
    `await c.req.json()`,
    `c.req.param("id")`,
    `await c.req.formData();`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-hono-route",
      [
        {
          regex: /\b(?:app|router|hono)\.(?:get|post|put|patch|delete|options|all|use)\s*\(/,
          label: "Hono method/use registration"
        },
        { regex: /new\s+Hono\s*\(/, label: "new Hono() instantiation" },
        {
          regex: /\bc\.req\.(?:query|param|json|formData|text|valid)\b/,
          label: "Request data accessor"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-koa-route.ts
var jsKoaRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-koa-route",
  description: "Koa route registrations and middleware (gated on Koa)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["koa"] },
  examples: [
    `const app = new Koa();`,
    `router.get("/users", handler)`,
    `router.post('/login', handler);`,
    `router.put("/x", h)`,
    `router.del('/y', h)`,
    `app.use(authMiddleware)`,
    `import KoaRouter from "@koa/router";`,
    `const r = KoaRouter();`,
    `app.use(async (ctx, next) => { await next(); })`,
    `async (ctx) => ctx.body = {}`,
    `ctx.request.body`,
    `ctx.query.page`,
    `ctx.params.id`,
    `ctx.state.user`,
    `ctx.throw(401)`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-koa-route",
      [
        {
          regex: /\b(?:router|app)\.(?:get|post|put|patch|del|delete|all|use)\s*\(/,
          label: "Koa router method registration"
        },
        { regex: /new\s+Koa\s*\(/, label: "new Koa() instantiation" },
        { regex: /\bKoaRouter\s*\(|@koa\/router/, label: "@koa/router import or factory" },
        { regex: /async\s*\(\s*ctx\s*[,)]/, label: "Koa middleware (ctx) signature" },
        { regex: /\bctx\.(?:request|query|params|state|throw)\b/, label: "ctx.* accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-nestjs-controller.ts
var jsNestjsControllerMatcher = {
  noiseTier: "normal",
  slug: "js-nestjs-controller",
  description: "NestJS controllers and route methods \u2014 entry-point surface (gated on @nestjs/*)",
  filePatterns: ["**/*.{ts,js}"],
  requires: { tech: ["nestjs"] },
  examples: [
    `@Controller("users")
export class UsersController {}`,
    `@Controller('/api')`,
    `@Get(":id")
findOne() {}`,
    `@Post('login')
login() {}`,
    `@Put("/x")
update() {}`,
    `@Patch(':id') patch() {}`,
    `@Delete("/y")
remove() {}`,
    `@All("*")
catchAll() {}`,
    `@UseGuards(JwtGuard)`,
    `@Public()
open() {}`,
    `findOne(@Body() body: any) {}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-nestjs-controller",
      [
        { regex: /@Controller\s*\(/, label: "@Controller decorator" },
        {
          regex: /@(?:Get|Post|Put|Patch|Delete|Options|Head|All)\s*\(/,
          label: "HTTP method decorator"
        },
        { regex: /@UseGuards\s*\(/, label: "@UseGuards (auth gate)" },
        { regex: /@Public\s*\(\s*\)/, label: "@Public() decorator (skips global auth)" },
        { regex: /@Body\s*\(\s*\)/, label: "@Body() (request body sink)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-catch-all-route-auth.ts
var catchAllRouteAuthMatcher = {
  noiseTier: "precise",
  slug: "catch-all-route-auth",
  description: "Catch-all routes and Payload CMS endpoints \u2014 verify auth covers all sub-paths",
  filePatterns: [
    "**/[[...rest]]/**/*.{ts,tsx}",
    "**/[...slug]/**/*.{ts,tsx}",
    "**/[...path]/**/*.{ts,tsx}",
    "**/(payload)/**/*.{ts,tsx}",
    "**/graphql/route.{ts,tsx}",
    "**/app/api/**/*.{ts,tsx}"
  ],
  requires: { tech: ["nextjs"] },
  examples: [
    `export async function GET(request) { return Response.json({}) }`,
    `export async function POST(request: Request) { const body = await request.json(); return Response.json(body) }`,
    `export const PUT = async (req) => Response.json({})`,
    `export const PATCH = async (req: Request) => Response.json({})`,
    `export function DELETE(request) { return new Response(null, { status: 204 }) }`,
    `export async function GET() { await requireAuth(); return Response.json({}) }`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const isCatchAll = /\[\[\.\.\.|\[\.\.\./.test(filePath);
    const isPayload = /\(payload\)|payload.*graphql|GRAPHQL_POST|GRAPHQL_GET/.test(content) || /\(payload\)/.test(filePath);
    const isGraphQL = /graphql/i.test(filePath);
    if (!isCatchAll && !isPayload && !isGraphQL) return [];
    const hasAuth = [
      /withAuthentication\s*\(/,
      /withSchema\s*\(/,
      /getSession\s*\(/,
      /auth\s*\(\s*\)/,
      /requireAuth/,
      /verifyToken/
    ].some((p) => p.test(content));
    for (let i = 0; i < lines.length; i++) {
      if (/export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)|export\s+(const\s+)?(GET|POST|PUT|DELETE|PATCH)\s*=/.test(
        lines[i]
      )) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        const label = isCatchAll ? `Catch-all route handler${hasAuth ? " (has auth)" : " \u2014 NO auth on catch-all"}` : isPayload || isGraphQL ? `Payload/GraphQL endpoint${hasAuth ? " (has auth)" : " \u2014 NO auth"}` : "Route handler";
        matches.push({
          vulnSlug: "catch-all-route-auth",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: label
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-catchall-router.ts
var catchallRouterMatcher = {
  noiseTier: "precise",
  slug: "catchall-router",
  description: "Catch-all route with internal router (Elysia/Hono/Express) \u2014 single auth entry point",
  filePatterns: [
    "**/[[...rest]]/route.{ts,tsx}",
    "**/[[...slug]]/route.{ts,tsx}",
    "**/[...rest]/route.{ts,tsx}",
    "**/[...slug]/route.{ts,tsx}",
    "**/[[...catchAll]]/route.{ts,tsx}"
  ],
  requires: { tech: ["nextjs"] },
  examples: [
    `import { Elysia } from 'elysia';
const app = new Elysia();
export const GET = app.handle;`,
    `import { Hono } from 'hono';
const app = new Hono();
export const GET = (req) => app.fetch(req);`,
    `import express from 'express';
const app = express();
export const POST = (req) => app(req);`,
    `import { Router } from 'itty-router';
const router = Router();
export const GET = (req) => router.handle(req);`,
    `const router = createRouter();
export const GET = (req) => handleRequest(req);`,
    `export async function GET(request) { return Response.json({}) }`,
    `export const POST = async (req) => Response.json({})`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const routerPatterns = [
      { regex: /from\s+['"]elysia['"]|new\s+Elysia/, label: "Elysia router in catch-all route" },
      { regex: /from\s+['"]hono['"]|new\s+Hono/, label: "Hono router in catch-all route" },
      { regex: /from\s+['"]express['"]|express\(\)/, label: "Express router in catch-all route" },
      { regex: /from\s+['"]itty-router['"]|Router\(\)/, label: "itty-router in catch-all route" },
      { regex: /createRouter|handleRequest/, label: "Custom router in catch-all route" }
    ];
    for (const { regex, label } of routerPatterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 4);
          matches.push({
            vulnSlug: "catchall-router",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
          break;
        }
      }
    }
    if (matches.length === 0) {
      for (let i = 0; i < lines.length; i++) {
        if (/export\s+(const|async\s+function|function)\s+(GET|POST|PUT|PATCH|DELETE)\b/.test(
          lines[i]
        )) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 4);
          matches.push({
            vulnSlug: "catchall-router",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: "Catch-all route handler \u2014 all sub-paths funneled here"
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-edge-sandbox.ts
var frameworkEdgeSandboxMatcher = {
  noiseTier: "precise",
  slug: "framework-edge-sandbox",
  description: "Edge runtime sandbox + global shims (Buffer/process/fetch leak risk)",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["nextjs"] },
  examples: [
    `const fn = new Function('a', 'return a + 1');`,
    `const result = eval(userCode);`,
    `await context.evaluate(moduleSource);`,
    `const script = new vm.Script(code);`,
    `vm.runInNewContext(code, sandbox);`,
    `vm.runInContext(code, ctx);`,
    `const ctx = vm.createContext({});`,
    `globalThis.Buffer = Buffer;`,
    `self.process = process;`,
    `globalThis.fetch = fetch;`,
    `// edge-runtime polyfill setup`,
    `const bindings = createBindings(env);`,
    `const wrapper = buildSandboxFunction(source);`,
    `const buf = Buffer as any;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const PATH_HINT = /(?:^|\/)server\/web\/sandbox\/|(?:^|\/)server\/web\/(?:web-runtime|spec-extension|spec-compliant)\/|(?:^|\/)server\/(?:next-base-server|web-server)\.[tj]sx?$|(?:^|\/)server\/web\/edge-route-module-wrapper\.[tj]sx?$/;
    const CONTENT_HINTS = [
      /\bnew\s+Function\s*\(/,
      /\beval\s*\(/,
      /\bcontext\.evaluate\s*\(/,
      /\bvm\.(?:Script|runInNewContext|runInContext|createContext)\s*\(/,
      /\b(?:globalThis|self)\.(?:Buffer|process|require|fetch)\s*=/,
      /\bedge-?runtime\b/i,
      /\bcreateBindings\s*\(|\bbuildSandboxFunction\s*\(/,
      /\bBuffer\s*as\s*any\b/
    ];
    const isByPath = PATH_HINT.test(filePath);
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      for (const re of CONTENT_HINTS) {
        if (re.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(re.source.slice(0, 40));
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0 && isByPath) {
      const match2 = {
        vulnSlug: "framework-edge-sandbox",
        lineNumbers: [1],
        snippet: lines.slice(0, 5).join("\n"),
        matchedPattern: "edge sandbox file (path)"
      };
      return [match2];
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "framework-edge-sandbox",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-fw-server-action.ts
var frameworkServerActionMatcher = {
  noiseTier: "precise",
  slug: "framework-server-action",
  description: "Server Action dispatcher / encoder / decoder code in the framework",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["nextjs"] },
  examples: [
    `const result = decodeReply(body, manifest);`,
    `const args = await decodeAction(formData, serverModuleMap);`,
    `const state = decodeFormState(rawState, formData);`,
    `const stream = encodeReply(value);`,
    `const action = parseAction(request);`,
    `const fn = getActionFromManifest(actionId, manifest);`,
    `await callServer(actionId, args);`,
    `const id = parseActionId(headers.get('next-action'));`,
    `registerServerReference(actionFn, actionId, null);`,
    `const header = req.headers['__Next-Action'];`,
    `const id = req.headers.get('next-action-id');`,
    `if (action.id === actionId) { /* dispatch */ }`,
    `import actionManifest from './actions.json'`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const PATH_HINT = /(?:^|\/)action-(?:handler|async-storage|encryption|utils|errors)\.[tj]sx?$|(?:^|\/)server-actions?\.[tj]sx?$|(?:^|\/)decodeAction\.|(?:^|\/)decodeReply\./;
    const CONTENT_HINTS = [
      /\b(?:decodeReply|decodeAction|decodeFormState|encodeReply|parseAction|getActionFromManifest|callServer|parseActionId|registerServerReference)\s*\(/,
      /\b__Next[-_]Action\b/,
      /\b['"]next-action(?:-id|-redirect)?['"]/,
      /\baction\.id\s*===|actionManifest\b|actions\.json\b/
    ];
    const isHandlerByPath = PATH_HINT.test(filePath);
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      let matched = false;
      for (const re of CONTENT_HINTS) {
        if (re.test(lines[i])) {
          matched = true;
          labels.add(re.source.slice(0, 40));
          break;
        }
      }
      if (!matched) continue;
      hitLines.push(i + 1);
      if (firstContext === void 0) {
        const s = Math.max(0, i - 2);
        const e = Math.min(lines.length, i + 4);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    if (hitLines.length === 0 && isHandlerByPath) {
      const match2 = {
        vulnSlug: "framework-server-action",
        lineNumbers: [1],
        snippet: lines.slice(0, 5).join("\n"),
        matchedPattern: "action handler file (path)"
      };
      return [match2];
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "framework-server-action",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-image-optimizer.ts
var frameworkImageOptimizerMatcher = {
  noiseTier: "precise",
  slug: "framework-image-optimizer",
  description: "Next.js image-optimizer and private-IP allow-list code (SSRF risk surface)",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["nextjs"] },
  examples: [
    `await imageOptimizer({ req, res, parsedUrl, nextConfig });`,
    `const buf = await optimizeImage(input, { width });`,
    `const remotePatterns = config.images.remotePatterns;`,
    `if (config.domains.includes(host)) return true;`,
    `const loaderFile = require(config.images.loaderFile);`,
    `if (isPrivateIP(addr)) throw new Error('blocked');`,
    `const m = host.match(IP_ADDRESS_REGEX);`,
    `if (matchRemotePattern(p, parsed)) return true;`,
    `if (matchHost(p.hostname, parsed.hostname)) return true;`,
    `if (host === '169.254.169.254') throw new Error('metadata blocked');`,
    `if (ip === '127.0.0.1' || ip === '0.0.0.0') return false;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const PATH_HINT = /(?:^|\/)(?:image-optimizer|image-blur-svg|is-private-ip|match-remote-pattern|match-host|image-config|image-config-context\.shared-runtime|image-content-disposition|require-fonts|next-image-loader)\.[tj]sx?$/;
    const CONTENT_HINTS = [
      /\bimageOptimizer\s*\(|\boptimizeImage\s*\(/,
      /\b(?:remotePatterns|domains|loaderFile)\b/,
      /\bisPrivateIP\s*\(|\bIP_ADDRESS_REGEX\b/,
      /\bmatchRemotePattern\s*\(|\bmatchHost\s*\(/,
      /\b(?:169\.254\.169\.254|0\.0\.0\.0|127\.0\.0\.1|::1|::ffff:)/
    ];
    const isByPath = PATH_HINT.test(filePath);
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      for (const re of CONTENT_HINTS) {
        if (re.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(re.source.slice(0, 40));
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0 && isByPath) {
      const match2 = {
        vulnSlug: "framework-image-optimizer",
        lineNumbers: [1],
        snippet: lines.slice(0, 5).join("\n"),
        matchedPattern: "image optimizer file (path)"
      };
      return [match2];
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "framework-image-optimizer",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-internal-header.ts
var frameworkInternalHeaderMatcher = {
  noiseTier: "precise",
  slug: "framework-internal-header",
  description: "Reads/writes of Next.js internal headers (x-middleware-*, x-next-*, __Next-*)",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["nextjs"] },
  examples: [
    `const subreq = headers.get('x-middleware-subrequest');`,
    `res.headers.set('x-middleware-rewrite', target);`,
    `res.headers.set('x-middleware-redirect', loc);`,
    `if (req.headers.get('x-middleware-prefetch')) return;`,
    `headers['x-next-prerender-bypass'] = token;`,
    `const tags = res.headers.get('x-next-cache-tags');`,
    `if (req.headers['__Next-Action']) handle();`,
    `const id = req.headers.get('next-action-id');`,
    `const tree = req.headers.get('next-router-state-tree');`,
    `if (req.headers.get('rsc')) return rscResponse();`,
    `const original = req.headers.get('next-url');`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const HEADERS = [
      "x-middleware-subrequest",
      "x-middleware-prefetch",
      "x-middleware-rewrite",
      "x-middleware-redirect",
      "x-middleware-next",
      "x-middleware-cookie",
      "x-middleware-set-cookie",
      "x-middleware-override-headers",
      "x-middleware-skip",
      "x-next-prerender-bypass",
      "x-next-revalidated-tags",
      "x-next-cache-tags",
      "x-next-debug-logging",
      "__Next-Action",
      "next-action-id",
      "next-router-state-tree",
      "next-router-prefetch",
      "next-router-segment-prefetch",
      "rsc",
      "next-url"
    ];
    const re = new RegExp(
      `['"\`](${HEADERS.map((h) => h.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&")).join("|")})['"\`]`,
      "i"
    );
    for (let i = 0; i < lines.length; i++) {
      const m = lines[i].match(re);
      if (!m) continue;
      hitLines.push(i + 1);
      labels.add(m[1].toLowerCase());
      if (firstContext === void 0) {
        const s = Math.max(0, i - 2);
        const e = Math.min(lines.length, i + 3);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "framework-internal-header",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-middleware.ts
var nextjsMiddlewareMatcher = {
  noiseTier: "precise",
  slug: "nextjs-middleware",
  description: "Next.js middleware.ts files \u2014 auth, redirects, header rewriting, access control",
  filePatterns: ["**/middleware.{ts,tsx,js,jsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `export function middleware(request) { return NextResponse.next() }`,
    `export async function middleware(request: NextRequest) { return NextResponse.redirect(new URL('/login', request.url)) }`,
    `export const middleware = (req) => NextResponse.next()`,
    `export let middleware = async (req) => NextResponse.rewrite(new URL('/foo', req.url))`,
    `export default function middleware(request) { return NextResponse.next() }`,
    `export default async function (req) { return NextResponse.next() }`,
    `export function middleware(req) { return NextResponse.next() }
export const config = { matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'] }`,
    `export default function middleware(req) { return NextResponse.next() }
export const config = { matcher: '/dashboard/:path*' }`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const hasMiddleware = /export\s+(default\s+|async\s+)?function\s+middleware/i.test(content) || /export\s+(const|let)\s+middleware/i.test(content) || /export\s+default/.test(content);
    if (!hasMiddleware) return [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/export\s+(default\s+|async\s+)?function\s+middleware/i.test(line) || /export\s+(const|let)\s+middleware/i.test(line) || /export\s+default\s+(async\s+)?function/.test(line)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 6);
        matches.push({
          vulnSlug: "nextjs-middleware",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Next.js middleware \u2014 security-critical request interceptor"
        });
      }
    }
    for (let i = 0; i < lines.length; i++) {
      if (/export\s+const\s+config/.test(lines[i])) {
        const start = Math.max(0, i);
        const end = Math.min(lines.length, i + 10);
        matches.push({
          vulnSlug: "nextjs-middleware",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Middleware route matcher config \u2014 controls scope of protection"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-middleware-only-auth.ts
var nextjsMiddlewareOnlyAuthMatcher = {
  noiseTier: "normal",
  slug: "nextjs-middleware-only-auth",
  description: "Route handlers in protected route groups without their own auth check \u2014 relying solely on Next.js middleware",
  filePatterns: [
    "**/app/**(protected)**/route.{ts,tsx}",
    "**/app/**(dashboard)**/route.{ts,tsx}",
    "**/app/**(auth)**/route.{ts,tsx}",
    "**/app/api/**/route.{ts,tsx}"
  ],
  requires: { tech: ["nextjs"] },
  examples: [
    `export async function GET(request) { return Response.json({ ok: true }) }`,
    `export async function POST(request: Request) { const body = await request.json(); return Response.json(body) }`,
    `export const PUT = async (req) => Response.json({})`,
    `export const PATCH = async (req: Request) => Response.json({})`,
    `export function DELETE(request) { return new Response(null, { status: 204 }) }`,
    `export const GET = async () => Response.json([])`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const isRoute = /route\.(ts|tsx)$/.test(filePath);
    if (!isRoute) return [];
    const hasHandler = /export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)|export\s+(const\s+)?(GET|POST|PUT|PATCH|DELETE)\s*=/.test(
      content
    );
    if (!hasHandler) return [];
    const hasBackendAuth = [
      /withSchema\s*\(/,
      /withAuthentication\s*\(/,
      /getSession\s*\(/,
      /auth\s*\(\s*\)/,
      /requireAuth/,
      /verifyToken/,
      /authMiddleware/,
      /withAuth\s*\(/
    ].some((p) => p.test(content));
    if (hasBackendAuth) return [];
    const matches = [];
    const lines = content.split("\n");
    const isProtectedGroup = /\(protected\)|\(dashboard\)|\(auth\)/.test(filePath);
    for (let i = 0; i < lines.length; i++) {
      if (/export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE)|export\s+(const\s+)?(GET|POST|PUT|PATCH|DELETE)\s*=/.test(
        lines[i]
      )) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "nextjs-middleware-only-auth",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: isProtectedGroup ? "Route in protected group with no backend auth \u2014 relies solely on Next.js middleware" : "API route without backend auth check (weak candidate)"
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-page-data-fetch.ts
var pageDataFetchMatcher = {
  noiseTier: "normal",
  slug: "page-data-fetch",
  description: "Server Component pages reading searchParams/params for data fetching \u2014 IDOR/SSRF risk",
  filePatterns: ["**/app/**/page.{ts,tsx}", "**/pages/**/*.{ts,tsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `export default async function Page({ searchParams }) {
  const id = searchParams.get('id');
  const data = await fetch('/api/x?id=' + id);
  return null
}`,
    `export default async function Page({ params }) {
  const r = await fetch('/api/users/' + params.id);
  return null
}`,
    `export default async function Page({ searchParams }) {
  const q = searchParams['q'];
  const data = await fetchApi('/search?q=' + q);
  return null
}`,
    `export async function getServerSideProps(ctx) {
  const data = await fetch('/api/foo?id=' + ctx.query.id);
  return { props: { data, query: ctx.params.id } }
}`,
    `export async function getStaticProps(ctx) {
  const data = await fetch('/api/items/' + ctx.params.slug);
  return { props: { data } }
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const hasParams = /searchParams|params\.\w+/.test(content);
    const hasFetch = /fetch\(|fetchApi|getServerSideProps|getStaticProps/.test(content);
    if (!hasParams || !hasFetch) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (/searchParams\.get|searchParams\[|params\.\w+/.test(lines[i]) && /fetch|Api|query/.test(lines.slice(i, Math.min(lines.length, i + 10)).join("\n"))) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "page-data-fetch",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Page reads URL params and fetches data \u2014 verify auth scoping"
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-page-without-auth-fetch.ts
var pageWithoutAuthFetchMatcher = {
  noiseTier: "precise",
  slug: "page-without-auth-fetch",
  description: "Server Component pages fetching resources by URL params without verifying user access",
  filePatterns: ["**/app/**/page.{ts,tsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `export default async function Page({ params }) {
  const data = await fetch('/api/orders/' + params.id);
  return null
}`,
    `export default async function Page({ params }) {
  const r = await fetchApi('/users/' + params.userId);
  return null
}`,
    `export default async function Page({ params }) {
  const session = await getServerSession();
  const r = await fetch('/api/x/' + params.id);
  return null
}`,
    `export default async function Page({ params }) {
  const session = await auth();
  const data = await fetch('/api/items/' + params.id);
  return null
}`,
    `export default async function Page({ params }) {
  await requireAuth();
  const r = await fetch('/api/orgs/' + params.orgId);
  return null
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const hasParamFetch = /params\.\w+/.test(content) && /fetch|fetchApi|getServerSession/.test(content);
    if (!hasParamFetch) return [];
    const hasAccessCheck = /auth|getSession|requireAuth|withAuthentication|checkAccess|verifyAccess|can\s*\(/.test(
      content
    );
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (/params\.\w+/.test(lines[i]) && /fetch|Api|query/.test(lines.slice(i, Math.min(lines.length, i + 8)).join("\n"))) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "page-without-auth-fetch",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: hasAccessCheck ? "Page fetches by URL param with auth (verify scoping)" : "Page fetches by URL param WITHOUT access check \u2014 IDOR risk"
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-route-handlers.ts
var allRouteHandlersMatcher = {
  noiseTier: "noisy",
  slug: "all-route-handlers",
  description: "All route.ts HTTP handlers \u2014 comprehensive entry point coverage (weak candidate)",
  filePatterns: ["**/route.{ts,tsx,js,jsx}", "**/route.*.{ts,tsx,js,jsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `export async function GET(request) { return Response.json({}) }`,
    `export async function POST(request: Request) { return Response.json({ ok: true }) }`,
    `export const PUT = async (req) => Response.json({})`,
    `export const PATCH = async (req: Request) => Response.json({})`,
    `export function DELETE(request) { return new Response(null, { status: 204 }) }`,
    `export async function HEAD(request) { return new Response() }`,
    `export const OPTIONS = (req) => new Response()`,
    `export default async function (req, res) { res.json({}) }`,
    `export default function (req, res) { res.send('ok') }`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const methodMatch = line.match(
        /export\s+(?:const|async\s+function|function)\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b/
      );
      if (!methodMatch) continue;
      const method = methodMatch[1];
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 4);
      matches.push({
        vulnSlug: "all-route-handlers",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: `${method} route handler \u2014 HTTP entry point (weak candidate)`
      });
    }
    for (let i = 0; i < lines.length; i++) {
      if (/export\s+default\s+(async\s+)?(function\s*)?\(/.test(lines[i])) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "all-route-handlers",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Default export route handler \u2014 HTTP entry point (weak candidate)"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-server-action.ts
var serverActionMatcher = {
  noiseTier: "precise",
  slug: "server-action",
  description: "Next.js Server Actions \u2014 every export is a publicly callable POST endpoint",
  filePatterns: [
    "**/app/**/actions.{ts,tsx}",
    "**/app/**/*action*.{ts,tsx}",
    "**/**/actions/**/*.{ts,tsx}",
    "**/components/**/*.{ts,tsx}",
    "**/lib/**/*.{ts,tsx}",
    "**/src/**/*.{ts,tsx}"
  ],
  requires: { tech: ["nextjs"] },
  examples: [
    `"use server";
export async function createPost(title: string) { return { title } }`,
    `'use server'
export function deleteRecord(id) { return id }`,
    `"use server";
export const updateUser = async (data) => ({ ok: true })`,
    `'use server'
export let saveDraft = (input) => input`,
    `export async function archiveItem(id) {
  "use server";
  return id
}`,
    `export const submitForm = async (data) => {
  'use server'
  return data
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/content\/|docs\/|\.mdx?$/i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const hasFileDirective = /^['"]use server['"]/.test(content.trim());
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isExportedFn = /export\s+(async\s+)?function\s+\w+/.test(line);
      const isExportedConst = /export\s+(const|let)\s+\w+\s*=\s*(async\s+)?\(/.test(line);
      if (!isExportedFn && !isExportedConst) continue;
      const hasInlineDirective = i + 1 < lines.length && /['"]use server['"]/.test(lines[i + 1]);
      if (!hasFileDirective && !hasInlineDirective) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 4);
      matches.push({
        vulnSlug: "server-action",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: hasInlineDirective ? "Server Action (inline 'use server') \u2014 publicly callable POST endpoint" : "Server Action (file-level 'use server') \u2014 publicly callable POST endpoint"
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-server-action-no-auth.ts
var serverActionNoAuthMatcher = {
  noiseTier: "precise",
  slug: "server-action-no-auth",
  description: "Server Action exports without any auth call \u2014 every export is a public POST endpoint",
  filePatterns: ["**/*.{ts,tsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `"use server";
export async function createUser(name: string) { return { name } }`,
    `'use server'
export function deleteAccount(id) { return id }`,
    `export async function doThing(x) {
  "use server";
  return x
}`,
    `"use server";
export async function fetchSecret() {
  return { secret: 'no auth call' }
}`,
    `"use server";
export async function getProfile(id) {
  const session = await getSession();
  return { id, session }
}`,
    `"use server";
export async function adminWipe() {
  await requireAuth();
  return { ok: true }
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/content\/|docs\/|\.mdx?$/i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const hasFileDirective = /^['"]use server['"]/.test(content.trim());
    const authCalls = [
      /getSession\s*\(/,
      /auth\s*\(\s*\)/,
      /requireAuth/,
      /withAuth/,
      /verifyToken/,
      /authUserAndTeamByAuthAPI/,
      /isAuthenticated/,
      /assertAuth/,
      /checkAuth/,
      /parseAuthToken/,
      /withOidcTokenAuth/
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isInlineServerAction = i + 1 < lines.length && /['"]use server['"]/.test(lines[i + 1]) && /export\s+(async\s+)?function/.test(line);
      const isFileExport = hasFileDirective && /export\s+(async\s+)?function\s+\w+/.test(line);
      if (!isInlineServerAction && !isFileExport) continue;
      const fnBody = lines.slice(i, Math.min(lines.length, i + 30)).join("\n");
      const hasAuth = authCalls.some((p) => p.test(fnBody));
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 4);
      matches.push({
        vulnSlug: "server-action-no-auth",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: hasAuth ? "Server Action with auth call (verify correctness)" : "Server Action WITHOUT any auth call \u2014 publicly callable"
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-server-actions.ts
var allServerActionsMatcher = {
  noiseTier: "noisy",
  slug: "all-server-actions",
  description: 'All "use server" exported functions \u2014 every export is a public POST endpoint (weak candidate)',
  filePatterns: ["**/*.{ts,tsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `"use server";
export async function createUser(name: string) { return { name } }`,
    `'use server'
export function deleteAccount(id) { return { id } }`,
    `"use server";
export const updateProfile = async (data) => ({ ok: true })`,
    `'use server'
export let fetchData = (q) => q`,
    `export async function doThing(x) {
  "use server";
  return x
}`,
    `export const archiveItem = async (id) => {
  'use server'
  return id
}`,
    `"use server";
export async function getList() {
  return []
}
export function helper() {}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    if (/content\/|docs\/|\.mdx?$/i.test(filePath)) return [];
    if (!/['"]use server['"]/.test(content)) return [];
    const matches = [];
    const lines = content.split("\n");
    const hasFileDirective = /^['"]use server['"]/.test(content.trim());
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isExport = /export\s+(async\s+)?function\s+\w+/.test(line) || /export\s+(const|let)\s+\w+\s*=\s*(async\s+)?\(/.test(line);
      if (!isExport) continue;
      const hasInlineDirective = i + 1 < lines.length && /['"]use server['"]/.test(lines[i + 1]);
      const hasBodyDirective = !hasInlineDirective && lines.slice(i + 1, Math.min(lines.length, i + 6)).some((l) => /['"]use server['"]/.test(l));
      if (!hasFileDirective && !hasInlineDirective && !hasBodyDirective) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 4);
      const nameMatch = line.match(/(?:function|const|let)\s+(\w+)/);
      const name = nameMatch?.[1] ?? "anonymous";
      matches.push({
        vulnSlug: "all-server-actions",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: `Server Action export: ${name} \u2014 public POST endpoint (weak candidate)`
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-untrusted-fetch.ts
var frameworkUntrustedFetchMatcher = {
  noiseTier: "precise",
  slug: "framework-untrusted-fetch",
  description: "Framework code calling fetch with a URL derived from request input",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["nextjs"] },
  examples: [
    `const url = req.url;
const res = await fetch(url);`,
    `const target = request.headers.get('x-target');
const data = await fetch(target);`,
    `const u = new URL(req.url);
await fetch(u.searchParams.get('href'));`,
    `const upstream = req.query.upstream;
await globalThis.fetch(upstream);`,
    `const path = request.nextUrl.searchParams.get('path');
const r = await fetch(path);`,
    `const meta = getRequestMeta(req, 'origin');
const r = await fetch(meta + '/api');`,
    `const cookieVal = request.cookies.get('redirect')?.value;
const r = await fetch(cookieVal);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    const isFrameworkPath = /(?:^|\/)packages\/(?:next|next-server|next-mdx|next-codemod|next-bundle-analyzer)\/src\//.test(
      filePath
    ) || /(?:^|\/)src\/server\//.test(filePath) || /(?:^|\/)src\/lib\/router-utils\//.test(filePath);
    if (!isFrameworkPath) return [];
    const lines = content.split("\n");
    const hitLines = [];
    let firstContext;
    const FETCH_LINE = /\b(?:globalThis\.|window\.)?fetch\s*\(/;
    const TAINT_HINTS = /\b(?:req\.(?:url|query|headers|body)|request\.(?:url|nextUrl|headers|query|body)|searchParams\.get\b|new\s+URL\s*\(\s*req\b|nextUrl\.(?:searchParams|pathname)|getRequestMeta\b|request\.cookies)/;
    for (let i = 0; i < lines.length; i++) {
      if (!FETCH_LINE.test(lines[i])) continue;
      const span = lines.slice(Math.max(0, i - 8), Math.min(lines.length, i + 6)).join("\n");
      if (!TAINT_HINTS.test(span)) continue;
      hitLines.push(i + 1);
      if (firstContext === void 0) {
        const s = Math.max(0, i - 3);
        const e = Math.min(lines.length, i + 4);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "framework-untrusted-fetch",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: "fetch in framework code with URL from req/headers/query/body"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/js-nextjs-use-server-export.ts
var useServerExportMatcher = {
  noiseTier: "precise",
  slug: "use-server-export",
  description: "Server Action files that export functions accepting identity/auth objects as parameters \u2014 trusting client input",
  filePatterns: ["**/*.{ts,tsx}"],
  requires: { tech: ["nextjs"] },
  examples: [
    `"use server";
export async function deletePost(owner: string, postId: string) { return { owner, postId } }`,
    `'use server'
export async function transferFunds(authenticatedOwner, target, amount) { return { authenticatedOwner } }`,
    `"use server";
export function getProfile(user) { return user }`,
    `'use server'
export async function logEvent(session: any, event: string) { return { session, event } }`,
    `"use server";
export function setRole(actor, role) { return { actor, role } }`,
    `'use server'
export async function audit(caller: string, action: string) { return { caller, action } }`,
    `"use server";
export async function actAs(
  identity: string,
  payload: any,
) { return { identity, payload } }`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (!/['"]use server['"]/.test(content)) return [];
    const matches = [];
    const lines = content.split("\n");
    const identityParams = /\b(owner|authenticatedOwner|user|auth|session|identity|actor|caller)\b/i;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/export\s+(async\s+)?function\s+\w+/.test(line)) {
        const sigLines = lines.slice(i, Math.min(lines.length, i + 5)).join(" ");
        if (identityParams.test(sigLines)) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 4);
          matches.push({
            vulnSlug: "use-server-export",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: "Server Action exports function accepting identity/auth parameter \u2014 client can supply arbitrary values"
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-nosql-injection.ts
var jsNosqlInjectionMatcher = {
  noiseTier: "normal",
  slug: "js-nosql-injection",
  description: "NoSQL injection \u2014 Mongoose / MongoDB driver raw operators ($where, JSON.parse(input)) and unsafe aggregations",
  filePatterns: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
  examples: [
    `User.find({ $where: "this.name == '" + name + "'" })`,
    `db.collection.find({ $where: \`this.x == '\${input}'\` })`,
    `Model.find({ $where: function() { return this.x == y; } })`,
    `Model.find(JSON.parse(req.body.filter))`,
    `coll.aggregate([{ $match: { $where: "this.score > " + score } }])`,
    `User.find({ name: new RegExp(req.query.q) })`,
    `Model.findOne({ email: req.body.email })`,
    `User.find({ username: req.query.username })`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    return regexMatcher(
      "js-nosql-injection",
      [
        // $where with string concat / function body / template-literal interp.
        // The concat shape allows ' or " inside the inner string (the closing
        // quote of the $where value is matched by the [`"'] in the lookahead).
        {
          regex: /\$where\s*:\s*"[^"]{0,200}"\s*\+|\$where\s*:\s*'[^']{0,200}'\s*\+|\$where\s*:\s*function|\$where\s*:\s*`[^`]{0,200}\$\{/,
          label: "MongoDB $where with concatenation/function/template \u2014 server-side JS execution, injection"
        },
        // .find(JSON.parse(req.<...>))
        {
          regex: /\.find\s*\(\s*JSON\.parse\s*\(\s*req\./,
          label: "find(JSON.parse(req.*)) \u2014 operator injection via raw user JSON"
        },
        // aggregate pipeline containing $where
        {
          regex: /\.aggregate\s*\(\s*\[?\s*\{[^}]{0,400}\$where/,
          label: "MongoDB aggregate() pipeline using $where \u2014 server-side JS execution"
        },
        // new RegExp(req.<...>)
        {
          regex: /\bnew\s+RegExp\s*\(\s*req\./,
          label: "new RegExp from req.* \u2014 ReDoS and NoSQL query-shape injection"
        },
        // findOne / find with a single field bound to req.<obj>.<prop>.
        // `\.find(?:One)?` matches both `.find(...)` and `.findOne(...)` —
        // an earlier draft used `\.findOne?` which only matches `.findOn`
        // or `.findOne` and silently skipped plain `.find()`.
        {
          regex: /\.find(?:One)?\s*\(\s*\{[^}]{0,200}:\s*req\.\w+\.\w+/,
          label: "find/findOne with untyped req.* value \u2014 coerce to string or operator injection (e.g. { $ne: null })"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-nuxt-route.ts
var jsNuxtRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-nuxt-route",
  description: "Nuxt server routes / event handlers (gated on Nuxt)",
  filePatterns: ["**/server/api/**/*.{ts,js}", "**/server/routes/**/*.{ts,js}"],
  requires: { tech: ["nuxt"] },
  examples: [
    `export default defineEventHandler(async (event) => {})`,
    `export default eventHandler((event) => ({ ok: true }))`,
    `const id = getRouterParam(event, "id")`,
    `const params = getRouterParams(event)`,
    `const q = getQuery(event)`,
    `const body = await readBody(event)`,
    `throw createError({ statusCode: 401, message: "nope" })`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "js-nuxt-route",
      [
        {
          regex: /\bdefineEventHandler\s*\(/,
          label: "defineEventHandler \u2014 Nuxt server entry point"
        },
        { regex: /\beventHandler\s*\(/, label: "h3 eventHandler factory" },
        {
          regex: /\bgetRouterParam(?:s)?\s*\(|\bgetQuery\s*\(|\breadBody\s*\(/,
          label: "h3 request accessor (untrusted input)"
        },
        { regex: /\bcreateError\s*\(/, label: "createError() throw site" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-react-unsafe-json-in-html.ts
var unsafeJsonInHtmlMatcher = {
  noiseTier: "precise",
  slug: "unsafe-json-in-html",
  description: "JSON.stringify into dangerouslySetInnerHTML or script tags \u2014 </script> injection risk",
  filePatterns: ["**/*.{tsx,jsx,ts,js}"],
  requires: { tech: ["react"] },
  examples: [
    `<div dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />`,
    `return <script dangerouslySetInnerHTML={{ __html: 'window.__DATA__ = ' + JSON.stringify(state) }} />`,
    `const html = '<script>window.X = ' + JSON.stringify(payload) + '</script>'`,
    `return (
  <script>
    {'window.STATE = ' + JSON.stringify(state)}
  </script>
)`,
    `const json = JSON.stringify(props);
return <div dangerouslySetInnerHTML={{ __html: json }} />`,
    `import { safeJsonStringify } from './util';
const payload = JSON.stringify(state);
return <script dangerouslySetInnerHTML={{ __html: 'window.X = ' + payload }} />`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const usesSafe = /safeJsonStringify/.test(content);
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const hasJsonStringify = /JSON\.stringify/.test(line);
      const hasDangerousHtml = /dangerouslySetInnerHTML/.test(line);
      const context = lines.slice(Math.max(0, i - 3), Math.min(lines.length, i + 3)).join("\n");
      const contextHasJson = /JSON\.stringify/.test(context);
      const contextHasDangerous = /dangerouslySetInnerHTML/.test(context);
      const contextHasScript = /<script/.test(context);
      if (hasJsonStringify && (contextHasDangerous || contextHasScript)) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "unsafe-json-in-html",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: usesSafe ? "JSON.stringify near HTML injection point (safeJsonStringify in scope \u2014 verify usage)" : "JSON.stringify into dangerouslySetInnerHTML/script \u2014 use safeJsonStringify to escape </script>"
        });
      } else if (hasDangerousHtml && contextHasJson) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "unsafe-json-in-html",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: usesSafe ? "dangerouslySetInnerHTML with JSON data (safeJsonStringify in scope)" : "dangerouslySetInnerHTML with JSON.stringify \u2014 XSS via </script> in data"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/js-remix-route.ts
var jsRemixRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-remix-route",
  description: "Remix route loaders and actions (gated on Remix)",
  filePatterns: ["**/app/routes/**/*.{ts,tsx,js,jsx}", "**/routes/**/*.{ts,tsx,js,jsx}"],
  requires: { tech: ["remix"] },
  examples: [
    `export const loader = async ({ request }) => json({});`,
    `export const action = async ({ request }) => redirect("/x");`,
    `export async function loader({ request }) { return json({}); }`,
    `export async function action({ request }) {}`,
    `export default function Route() { return null; }`,
    `return json({ user }, { headers: { "Set-Cookie": session } });`,
    `await requireUserId(request);`,
    `const userId = await requireUser(request);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "js-remix-route",
      [
        {
          regex: /export\s+(?:async\s+)?(?:const|function)\s+(?:loader|action)\b/,
          label: "Remix loader/action export"
        },
        {
          regex: /export\s+default\s+function\s+\w+/,
          label: "Remix default export route component"
        },
        {
          regex: /\bjson\s*\(\s*\{[^}]*\}\s*,\s*\{\s*headers/,
          label: "json() with custom headers (auth response)"
        },
        { regex: /\brequireUser(?:Id)?\s*\(/, label: "common Remix auth helper" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-socketio-handler.ts
var jsSocketioHandlerMatcher = {
  noiseTier: "noisy",
  slug: "js-socketio-handler",
  description: "Socket.IO event handlers \u2014 entry-point surface (gated on socketio)",
  filePatterns: ["**/*.{ts,js,mjs,cjs}"],
  requires: { tech: ["socketio"] },
  examples: [
    `io.on('connection', (socket) => { console.log('hi') })`,
    `io.on("connection", socket => {})`,
    `socket.on('chat:message', (msg) => broadcast(msg))`,
    `socket.on("disconnect", () => {})`,
    `io.use((socket, next) => next())`,
    `const token = socket.handshake.auth.token`,
    `const ua = socket.handshake.headers["user-agent"]`,
    `const room = socket.handshake.query.room`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-socketio-handler",
      [
        {
          regex: /\bio\.on\s*\(\s*['"]connection['"]/,
          label: "io.on('connection', ...) \u2014 connection entry"
        },
        {
          regex: /\bsocket\.on\s*\(\s*['"][^'"]+['"]/,
          label: "socket.on('event', handler)"
        },
        { regex: /\bio\.use\s*\(/, label: "io.use(authMiddleware) \u2014 auth gate" },
        {
          regex: /\bsocket\.handshake\.(?:auth|headers|query)\b/,
          label: "handshake.auth/headers/query (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-solidstart-action.ts
var jsSolidstartActionMatcher = {
  noiseTier: "noisy",
  slug: "js-solidstart-action",
  description: "SolidStart server actions and cached server functions (gated on SolidStart)",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  requires: { tech: ["solidstart"] },
  examples: [
    `export const updateUser = action(async (form: FormData) => {})`,
    `const getUsers = cache(async (id: string) => {}, "users")`,
    `const search = query(async (q: string) => {}, "search")`,
    `return"use server";`,
    `x'use server';`,
    `const create = action$(async (data) => { return data })`,
    `const me = server$(async () => ({ id: 1 }))`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-solidstart-action",
      [
        {
          regex: /\b(?:action|cache|query)\s*\(\s*async\s*\(/,
          label: "action/cache/query factory"
        },
        { regex: /\b['"]use server['"]\s*;?/, label: "'use server' directive (publicly callable)" },
        { regex: /\baction\$\s*\(|\bserver\$\s*\(/, label: "action$ / server$ helper" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-sql-raw.ts
var jsSqlRawMatcher = {
  noiseTier: "normal",
  slug: "js-sql-raw",
  description: "Raw SQL escape hatches across popular JS/TS DB drivers (pg, mysql2, TypeORM, Sequelize, Knex, Kysely, postgres.js, better-sqlite3) \u2014 interpolated input is SQL injection",
  filePatterns: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
  examples: [
    `client.query("SELECT * FROM users WHERE id = " + userId)`,
    `pool.query(\`SELECT * FROM users WHERE id = \${id}\`)`,
    `await conn.query("DELETE FROM x WHERE y = '" + name + "'")`,
    `repo.query(\`UPDATE users SET role = '\${role}' WHERE id = \${id}\`)`,
    `sequelize.query(\`SELECT * FROM t WHERE col = '\${input}'\`)`,
    `Sequelize.literal(\`COUNT(*) FILTER (WHERE x = \${x})\`)`,
    `knex.raw(\`SELECT * FROM users WHERE id = \${id}\`)`,
    `qb.whereRaw("col = '" + value + "'")`,
    `db.selectFrom("users").where(sql.raw("col = " + x))`,
    `sql.unsafe(\`SELECT * FROM x WHERE y = \${y}\`)`,
    `db.prepare(\`SELECT * FROM users WHERE name = '\${name}'\`)`,
    `@Query(\`SELECT * FROM x WHERE y = '\${z}'\` + suffix)`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    return regexMatcher(
      "js-sql-raw",
      [
        // node-postgres / pg-pool / generic `client|pool|conn.query("SELECT ...${x}")`
        {
          regex: /\b(?:client|pool|conn)\.query\s*\(\s*['"`]\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|DROP)\b[^)]{0,400}\$\{/i,
          label: "node-postgres/pg: client/pool/conn.query with template-literal interpolation \u2014 SQL injection"
        },
        // Generic .query("...") + something — concatenation onto a SQL literal
        {
          regex: /\.query\s*\(\s*['"`][^'"`]{0,200}['"`]\s*\+/,
          label: ".query('...') with string concatenation \u2014 SQL injection"
        },
        // mysql2 / mysql informational signal — flags use of the library so a
        // reviewer spots the import alongside any unsafe pattern matches above.
        {
          regex: /\bmysql\.createConnection\s*\(|require\(\s*['"]mysql2?['"]\s*\)/,
          label: "mysql/mysql2 driver in use \u2014 verify all query() calls use placeholders, not concatenation"
        },
        // TypeORM raw query API
        {
          regex: /\b(?:repo|repository|entityManager|manager|connection|dataSource|getRepository\(\w+\))\.query\s*\(/,
          label: "TypeORM repository/manager.query \u2014 raw SQL, must use parameter array not interpolation"
        },
        // TypeORM @Query decorator with string concat
        {
          regex: /@Query\s*\(\s*['"`][^'"`]{0,400}['"`]\s*\+/,
          label: "TypeORM @Query with string concatenation \u2014 SQL injection"
        },
        // Sequelize: sequelize.query with template interpolation
        {
          regex: /\bsequelize\.query\s*\(\s*`?[^`)]{0,400}\$\{/,
          label: "Sequelize sequelize.query with template-literal interpolation \u2014 pass replacements/bind instead"
        },
        // Sequelize.literal — bypasses parameterization
        {
          regex: /Sequelize\.literal\s*\(/,
          label: "Sequelize.literal \u2014 bypasses escaping; must not include user input"
        },
        // Sequelize.fn with interpolated argument
        {
          regex: /Sequelize\.fn\s*\(\s*['"`][A-Z]+['"`]\s*,\s*\$\{/,
          label: "Sequelize.fn with template-literal interpolation \u2014 SQL injection"
        },
        // Knex .raw with interpolation
        {
          regex: /\.raw\s*\(\s*['"`][^'"`]{0,400}\$\{/,
          label: "Knex .raw with template-literal interpolation \u2014 SQL injection"
        },
        // Knex .whereRaw / .orderByRaw / .havingRaw — any use is worth a look
        {
          regex: /\.whereRaw\s*\(/,
          label: "Knex .whereRaw \u2014 verify bindings are passed as second argument, not interpolated"
        },
        {
          regex: /\.orderByRaw\s*\(/,
          label: "Knex .orderByRaw \u2014 verify bindings are passed as second argument, not interpolated"
        },
        {
          regex: /\.havingRaw\s*\(/,
          label: "Knex .havingRaw \u2014 verify bindings are passed as second argument, not interpolated"
        },
        // Kysely sql.raw / sql.lit
        {
          regex: /\bsql\.raw\s*\(/,
          label: "Kysely sql.raw \u2014 bypasses parameterization, must not include user input"
        },
        {
          regex: /\bsql\.lit\s*\(/,
          label: "Kysely sql.lit \u2014 inserts literal SQL, must not include user input"
        },
        // postgres.js (porsager) sql.unsafe
        {
          regex: /\bsql\.unsafe\s*\(/,
          label: "postgres.js sql.unsafe \u2014 bypasses parameterization, must not include user input"
        },
        // better-sqlite3: db.prepare(`...${x}...`)
        {
          regex: /\bdb\.prepare\s*\(\s*`[^`]{0,400}\$\{/,
          label: "better-sqlite3 db.prepare with template-literal interpolation \u2014 use bound parameters"
        },
        // better-sqlite3: db.exec(`...${x}...`)
        {
          regex: /\bdb\.exec\s*\(\s*`[^`]{0,400}\$\{/,
          label: "better-sqlite3 db.exec with template-literal interpolation \u2014 db.exec cannot bind, refactor to prepare()"
        },
        // Generic catch-all: query("SELECT ...") + ... for drivers we don't name
        {
          regex: /\bquery\s*\(\s*['"`]\s*(?:SELECT|INSERT|UPDATE|DELETE)\b[^)]{0,400}['"`]\s*\+/i,
          label: "Generic .query('SELECT/INSERT/...') with string concatenation \u2014 SQL injection"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-sveltekit-route.ts
var jsSveltekitRouteMatcher = {
  noiseTier: "noisy",
  slug: "js-sveltekit-route",
  description: "SvelteKit endpoint and load handlers (gated on SvelteKit)",
  filePatterns: ["**/+page.server.{ts,js}", "**/+server.{ts,js}", "**/+layout.server.{ts,js}"],
  requires: { tech: ["sveltekit"] },
  examples: [
    `export const GET = async ({ request }) => json({});`,
    `export async function POST({ request }) { return new Response(); }`,
    `export const PUT = async () => json({});`,
    `export async function DELETE({ params }) {}`,
    `export const load = async ({ locals }) => ({ user: locals.user });`,
    `export async function load({ params, fetch }) {}`,
    `export const actions = { default: async ({ request }) => {} };`,
    `throw redirect(302, "/login");`,
    `throw error(401, "unauthorized");`,
    `return fail(400, { message });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "js-sveltekit-route",
      [
        {
          regex: /export\s+(?:async\s+)?(?:const|function)\s+(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\b/,
          label: "+server method handler"
        },
        {
          regex: /export\s+(?:async\s+)?(?:const|function)\s+load\b/,
          label: "+page.server.ts / +layout.server.ts load function"
        },
        {
          regex: /export\s+const\s+actions\s*[:=]/,
          label: "+page.server.ts actions export (form actions)"
        },
        { regex: /\b(?:fail|redirect|error)\s*\(/, label: "SvelteKit response helper" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/js-workers-fetch.ts
var jsWorkersFetchMatcher = {
  noiseTier: "noisy",
  slug: "js-workers-fetch",
  description: "Cloudflare Workers / edge runtime default-export fetch handler (gated on workers)",
  filePatterns: ["**/*.{ts,js,mjs}"],
  requires: { tech: ["workers"] },
  examples: [
    `export default { async fetch(req, env, ctx) { return new Response("ok") } }`,
    `export default { fetch(request, env, ctx) { return new Response() } }`,
    `addEventListener('fetch', (event) => { event.respondWith(handle(event.request)) })`,
    `addEventListener("fetch", e => e.respondWith(handler(e.request)))`,
    `const value = await env.MY_KV.get("key")`,
    `const obj = env.R2_BUCKET`,
    `const secret = env.API_TOKEN`,
    `const cache = caches.default`,
    `const c = await caches.open("v1")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    return regexMatcher(
      "js-workers-fetch",
      [
        {
          regex: /export\s+default\s*\{\s*(?:async\s+)?fetch\s*\(/,
          label: "Workers default export { fetch(req, env, ctx) }"
        },
        {
          regex: /addEventListener\s*\(\s*['"]fetch['"]/,
          label: "addEventListener('fetch', ...) \u2014 service worker"
        },
        {
          regex: /\benv\.[A-Z][A-Z0-9_]+/,
          label: "env.* binding access (KV, R2, secrets)"
        },
        {
          regex: /\bcaches\.default\b|\bcaches\.open\s*\(/,
          label: "Workers cache API \u2014 review key composition"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jvm-jaxrs-resource.ts
var jvmJaxrsResourceMatcher = {
  noiseTier: "noisy",
  slug: "jvm-jaxrs-resource",
  description: "JAX-RS resources (Jersey, RESTEasy, Quarkus) \u2014 entry-point surface (gated on JAX-RS)",
  filePatterns: ["**/*.{java,kt}"],
  requires: { tech: ["jaxrs"] },
  examples: [
    `@Path("/users")`,
    `@Path ( "/api/v1/items" )`,
    `@GET`,
    `@POST`,
    `@PUT`,
    `@PATCH`,
    `@DELETE`,
    `@HEAD`,
    `@OPTIONS`,
    `@RolesAllowed("admin")`,
    `@PermitAll`,
    `public User getUser(@PathParam("id") String id) {`,
    `void search(@QueryParam("q") String q) {`,
    `void custom(@HeaderParam("X-Auth") String token) {`,
    `void submit(@FormParam("name") String name) {`,
    `void session(@CookieParam("sid") String sid) {`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "jvm-jaxrs-resource",
      [
        { regex: /@Path\s*\(\s*"[^"]+"\s*\)/, label: "@Path declaration" },
        {
          regex: /@(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b/,
          label: "JAX-RS method annotation"
        },
        { regex: /@RolesAllowed\s*\(/, label: "@RolesAllowed auth gate" },
        { regex: /@PermitAll\b/, label: "@PermitAll opens public access" },
        {
          regex: /@(?:Path|Query|Header|Form|Cookie)Param\s*\(/,
          label: "param extractor (untrusted)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jvm-ktor-route.ts
var jvmKtorRouteMatcher = {
  noiseTier: "noisy",
  slug: "jvm-ktor-route",
  description: "Ktor routing DSL (gated on Ktor)",
  filePatterns: ["**/*.kt"],
  requires: { tech: ["ktor"] },
  examples: [
    `routing {`,
    `routing { get("/") { call.respondText("hi") } }`,
    `get("/users") {`,
    `post("/login") {`,
    `put("/items/{id}") {`,
    `patch("/items/{id}") {`,
    `delete("/items/{id}") {`,
    `authenticate("jwt") {`,
    `authenticate("auth-session") { get("/me") { ... } }`,
    `val body = call.receive<UserDto>()`,
    `val multipart = call.receive<Multipart>()`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "jvm-ktor-route",
      [
        {
          regex: /\brouting\s*\{/,
          label: "routing { ... } block"
        },
        {
          regex: /\b(?:get|post|put|patch|delete)\s*\(\s*"[^"]+"\s*\)\s*\{/,
          label: "<verb>('/path') { ... }"
        },
        {
          regex: /\bauthenticate\s*\(\s*"[^"]+"\s*\)\s*\{/,
          label: "authenticate('jwt') { ... } scope"
        },
        { regex: /\bcall\.receive\b/, label: "call.receive (untrusted body)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jvm-micronaut-controller.ts
var jvmMicronautControllerMatcher = {
  noiseTier: "noisy",
  slug: "jvm-micronaut-controller",
  description: "Micronaut controllers and route methods (gated on Micronaut)",
  filePatterns: ["**/*.{java,kt}"],
  requires: { tech: ["micronaut"] },
  examples: [
    `@Controller("/users")`,
    `@Controller ( "/api/v1" )`,
    `@Get("/{id}")`,
    `@Post("/")`,
    `@Put("/{id}")`,
    `@Patch("/{id}")`,
    `@Delete("/{id}")`,
    `@Head("/health")`,
    `@Options("/items")`,
    `@Secured("ROLE_ADMIN")`,
    `@PermitAll`,
    `public User getUser(Authentication authentication) {`,
    `fun me(Authentication auth): UserDto {`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "jvm-micronaut-controller",
      [
        { regex: /@Controller\s*\(/, label: "@Controller(...) declaration" },
        {
          regex: /@(?:Get|Post|Put|Patch|Delete|Head|Options)\s*\(/,
          label: "Micronaut HTTP method annotation"
        },
        { regex: /@Secured\s*\(/, label: "@Secured(...) auth annotation" },
        { regex: /@PermitAll\b/, label: "@PermitAll \u2014 public access" },
        { regex: /\bAuthentication\s+\w+/, label: "Authentication arg in handler" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jvm-spring-controller.ts
var jvmSpringControllerMatcher = {
  noiseTier: "noisy",
  slug: "jvm-spring-controller",
  description: "Spring controllers, mappings, and security config (gated on Spring)",
  filePatterns: ["**/*.{java,kt}"],
  requires: { tech: ["spring"] },
  examples: [
    `@RestController`,
    `@Controller`,
    `@GetMapping("/users")`,
    `@PostMapping("/login")`,
    `@PutMapping`,
    `@PatchMapping("/items/{id}")`,
    `@DeleteMapping("/items/{id}")`,
    `@RequestMapping(value = "/api", method = RequestMethod.GET)`,
    `@PreAuthorize("hasRole('ADMIN')")`,
    `http.authorizeRequests().antMatchers("/public/**").permitAll();`,
    `.antMatcher("/admin/**")`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "jvm-spring-controller",
      [
        { regex: /@(?:Rest)?Controller\b/, label: "@Controller / @RestController" },
        {
          regex: /@(?:Get|Post|Put|Patch|Delete|Request)Mapping\b/,
          label: "@<Verb>Mapping"
        },
        { regex: /@PreAuthorize\s*\(/, label: "@PreAuthorize SpEL expression" },
        { regex: /\.permitAll\s*\(\s*\)/, label: ".permitAll() \u2014 opens public access" },
        { regex: /\bantMatchers?\s*\(/, label: "antMatcher(...) auth scope" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jvm-sql-raw.ts
var jvmSqlRawMatcher = {
  noiseTier: "normal",
  slug: "jvm-sql-raw",
  description: "Raw SQL across JVM DB libraries (JDBC, JPA/Hibernate, Spring JdbcTemplate, MyBatis, jOOQ, Exposed) \u2014 string concatenation or interpolation is SQL injection",
  filePatterns: ["**/*.{java,kt}"],
  requires: { tech: ["jvm"] },
  examples: [
    `stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);`,
    `stmt.executeQuery("SELECT * FROM x WHERE y = '" + name + "'")`,
    `stmt.executeUpdate("DELETE FROM users WHERE id = " + id)`,
    `Connection conn = DriverManager.getConnection(url);`,
    `connection.prepareStatement("SELECT * FROM users WHERE name = '" + name + "'")`,
    `em.createNativeQuery("SELECT * FROM users WHERE id = " + id)`,
    `em.createQuery("FROM User u WHERE u.name = '" + name + "'")`,
    `session.createSQLQuery("SELECT * FROM x WHERE col = '" + col + "'")`,
    `jdbcTemplate.query("SELECT * FROM users WHERE id = " + id, mapper)`,
    `jdbcTemplate.update("UPDATE users SET role = '" + role + "' WHERE id = " + id)`,
    `@Select("SELECT * FROM users WHERE id = \${id}")`,
    `val rows = exec("SELECT * FROM users WHERE name = '\${name}'")`,
    `val sql = "SELECT * FROM t WHERE col = '\${input}'"`,
    `DSL.field("a." + col)`
  ],
  match(content, filePath) {
    if (/\/(test|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "jvm-sql-raw",
      [
        // JDBC
        {
          regex: /\b(?:Statement|stmt)\.executeQuery\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'Statement.executeQuery("..." + ...) \u2014 concat into JDBC query'
        },
        {
          regex: /\b(?:Statement|stmt)\.execute(?:Update|Query|LargeUpdate)?\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'Statement.execute*("..." + ...) \u2014 concat into JDBC statement'
        },
        {
          regex: /\.createStatement\s*\(\s*\)\s*\.execute(?:Query|Update|LargeUpdate)?\s*\(/,
          label: "createStatement().execute*(...) \u2014 JDBC Statement (no parameterization)"
        },
        {
          // Match both `Connection.prepareStatement` and any `<conn>.prepareStatement(...)`
          // shape since instance variable names vary (`conn`, `connection`, `db`, …).
          regex: /\b\w*[Cc]on(?:nection)?\.prepareStatement\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: '<conn>.prepareStatement("..." + ...) \u2014 concat defeats parameterization'
        },
        {
          regex: /\bDriverManager\.getConnection\s*\(/,
          label: "DriverManager.getConnection(...) \u2014 JDBC in use (informational)"
        },
        // JPA / Hibernate
        {
          regex: /\b(?:em|entityManager|session)\.createNativeQuery\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'createNativeQuery("..." + ...) \u2014 concat into JPA/Hibernate native SQL'
        },
        {
          regex: /\b(?:em|entityManager|session)\.createQuery\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'createQuery("..." + ...) \u2014 concat into HQL/JPQL (still injectable)'
        },
        {
          regex: /\bsession\.createSQLQuery\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'session.createSQLQuery("..." + ...) \u2014 concat into Hibernate SQL'
        },
        // Spring JdbcTemplate
        {
          regex: /\bjdbcTemplate\.(?:query|update|queryForObject|queryForList|execute|batchUpdate)\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'jdbcTemplate.<op>("..." + ...) \u2014 concat into Spring JdbcTemplate'
        },
        {
          regex: /\bnamedParameterJdbcTemplate\.(?:query|update)\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'namedParameterJdbcTemplate.<op>("..." + ...) \u2014 concat defeats named params'
        },
        // MyBatis
        {
          regex: /@Select\s*\(\s*"[^"]{0,400}\$\{/,
          label: '@Select("...${...}") \u2014 MyBatis ${param} is unsafe (use #{param})'
        },
        {
          regex: /\bselectList\s*\(\s*"[^"]{0,400}"\s*\+|\bselectOne\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'selectList/selectOne("..." + ...) \u2014 concat into MyBatis statement id'
        },
        // jOOQ
        {
          regex: /\bDSL\.field\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'DSL.field("..." + ...) \u2014 jOOQ raw field with concat'
        },
        {
          regex: /\bdsl\.execute\s*\(\s*"[^"]{0,400}"\s*\+/,
          label: 'dsl.execute("..." + ...) \u2014 concat into jOOQ raw execute'
        },
        {
          regex: /\bDSL\.sql\s*\(/,
          label: "DSL.sql(...) \u2014 jOOQ raw SQL escape hatch"
        },
        // Exposed (Kotlin)
        {
          regex: /\bexec\s*\(\s*"[^"]{0,400}\$\{/,
          label: 'exec("...${...}") \u2014 Exposed exec with Kotlin template interpolation'
        },
        {
          regex: /\bTransactionManager\.current\(\)\.exec\s*\(/,
          label: "TransactionManager.current().exec(...) \u2014 Exposed raw exec"
        },
        // Kotlin string templates with SQL keywords
        {
          regex: /"\s*(?:SELECT|INSERT|UPDATE|DELETE)[^"]{0,400}\$\{/,
          label: '"SELECT/INSERT/UPDATE/DELETE ...${...}" \u2014 Kotlin string template into raw SQL'
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/jwt-handling.ts
var jwtHandlingMatcher = {
  noiseTier: "precise",
  slug: "jwt-handling",
  description: "JWT signing, verification, and cookie-based session handling",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `import { jwtVerify } from "jose"; await jwtVerify(token, key);`,
    `import jwt from "jsonwebtoken"; jwt.verify(token, key);`,
    `await verifyJwt(token); // jwt`,
    `import { SignJWT } from "jose"; new SignJWT({}).sign(key);`,
    `import jwt from "jsonwebtoken"; jwt.sign(payload, key);`,
    `const j = jwtSign(payload); // jwt`,
    `const j = createBypassJwt(uid); // jwt`,
    `import { jwtDecrypt } from "jose"; await jwtDecrypt(token, key);`,
    `import { EncryptJWT } from "jose"; new EncryptJWT({}).encrypt(key);`,
    `const opts = { cookie: { secret: "x" } }; // jwt`,
    `const c = SESSION_COOKIE; // jwt`,
    `const c = USER_CACHE_COOKIE; // jwt`,
    `await refreshToken(); // jwt`,
    `force_refresh_access_token(); // jwt`,
    `const t = jwt.sign(p, k, { algorithm: "none" });`,
    `const t = jwt.sign(p, k, { alg: "none" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    if (!/jwt|jose|jsonwebtoken|token|session[\w\s]{0,20}cookie/i.test(content)) return [];
    return regexMatcher(
      "jwt-handling",
      [
        {
          regex: /jwtVerify|jwt\.verify|verifyJwt/,
          label: "JWT verification (verify algorithm pinning)"
        },
        {
          regex: /SignJWT|jwt\.sign|jwtSign|createBypassJwt/,
          label: "JWT signing (verify key management)"
        },
        { regex: /jwtDecrypt|jwtEncrypt|EncryptJWT/, label: "JWT encryption (verify algorithm)" },
        {
          regex: /cookie.*secret|SESSION_COOKIE|USER_CACHE_COOKIE/,
          label: "Session cookie handling"
        },
        {
          regex: /refreshToken|force_refresh_access_token/,
          label: "Token refresh logic (verify validation)"
        },
        {
          regex: /algorithm.{0,40}none|alg.{0,40}none/i,
          label: "JWT 'none' algorithm (CRITICAL if not test)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/k8s-secret-reference.ts
var k8sSecretReferenceMatcher = {
  noiseTier: "normal",
  slug: "k8s-secret-reference",
  description: "K8s manifest references a Secret (secretKeyRef, secretName, ExternalSecret, etc.)",
  filePatterns: ["**/*.yaml", "**/*.yml"],
  examples: [
    `env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db
        key: password`,
    `volumes:
  - name: certs
    secret:
      secretName: tls-certs`,
    `apiVersion: v1
kind: Secret
metadata:
  name: db
type: Opaque`,
    `apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db`,
    `metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"`,
    `spec:
  containers:
    - image: ghcr.io/example/secrets-init-container:v1
      name: init`,
    `apiVersion: v1
kind: Secret
stringData:
  password: hunter2-very-secret`,
    `env:
  - name: API_TOKEN
    value: "AKIAIOSFODNN7EXAMPLE_aws_access_key"`
  ],
  match(content, filePath) {
    if (/(?:^|\/)(?:node_modules|vendor|charts|\.github)\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      { regex: /^\s*-?\s*secretKeyRef\s*:/, label: "env.valueFrom.secretKeyRef" },
      { regex: /^\s*secretName\s*:\s*\S/, label: "volumes.secret.secretName" },
      {
        regex: /^\s*kind\s*:\s*(?:Secret|ExternalSecret|SealedSecret|ClusterSecretStore|SecretStore)\b/,
        label: "Secret kind manifest"
      },
      { regex: /\bexternal-secrets\.io\//, label: "external-secrets.io CRD" },
      { regex: /\bvault\.hashicorp\.com\/agent-inject\b/, label: "vault-injector annotation" },
      { regex: /\bsecrets-init-container\b/, label: "secrets-init-container reference" },
      { regex: /^\s*stringData\s*:/, label: "Secret stringData (plaintext in manifest!)" },
      // Commonly leaked: env var values that are literal secrets
      {
        regex: /^\s*value\s*:\s*(?:['"]?[A-Za-z0-9+/=_-]{24,})/,
        label: "env.value literal (possibly a secret)"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "k8s-secret-reference",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 5).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/k8s-secrets-init-container.ts
var k8sSecretsInitContainerMatcher = {
  noiseTier: "precise",
  slug: "k8s-secrets-init-container",
  description: "K8s manifest uses the secrets-init-container decryption pipeline",
  filePatterns: ["**/*.yaml", "**/*.yml"],
  examples: [
    `initContainers:
  - name: init
    image: ghcr.io/example/secrets-init-container:v1`,
    `env:
    name: ENCRYPTED_V1_DATABASE_URL
    value: "..."`,
    `env:
    name: ENCRYPTED_V2_API_TOKEN
    value: "..."`,
    `volumeMounts:
  - name: decrypted
    mountPath: /usr/share`,
    `volumes:
  - name: decrypted-env
    emptyDir:
      medium: Memory`,
    `secretKeyRef:
  name: encrypted-v1-database
  key: payload`
  ],
  match(content, filePath) {
    if (/(?:^|\/)(?:node_modules|vendor|charts|\.github)\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      { regex: /\bsecrets-init-container\b/, label: "secrets-init-container image reference" },
      {
        regex: /^\s*name\s*:\s*ENCRYPTED_V[12]_[A-Z0-9_]+/,
        label: "ENCRYPTED_V*_ env var (init-container consumer)"
      },
      {
        regex: /^\s*mountPath\s*:\s*["']?\/usr\/share["']?\s*$/,
        label: "/usr/share decrypted-env mount"
      },
      { regex: /\bdecrypted-env\b/, label: "decrypted-env volume reference" },
      { regex: /^\s*name\s*:\s*encrypted-v[12]-\S+/, label: "encrypted-v{1,2}-* secret name" }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "k8s-secrets-init-container",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 5).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/lambda-aws-handler.ts
var lambdaAwsHandlerMatcher = {
  noiseTier: "noisy",
  slug: "lambda-aws-handler",
  description: "AWS Lambda handler signatures across Node/Python/Java (gated on aws-lambda)",
  filePatterns: ["**/*.{ts,js,mjs,cjs,py,java,kt}"],
  requires: { tech: ["aws-lambda"] },
  examples: [
    `exports.handler = async (event, context) => { return { statusCode: 200 } }`,
    `exports.handler = (event, context, callback) => callback(null, {})`,
    `def lambda_handler(event, context):
    return {"statusCode": 200}`,
    `public class Handler implements RequestHandler<APIGatewayProxyEvent, APIGatewayProxyResponseEvent> {}`,
    `class MyHandler implements RequestHandler<S3Event, String> { }`,
    `import { APIGatewayProxyEvent, APIGatewayProxyResult } from "aws-lambda";`,
    `const evt: APIGatewayV2Event = event;`,
    `const claims = event.requestContext.authorizer.claims;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    if (/\b(?:tests?|test)\b/i.test(filePath)) return [];
    return regexMatcher(
      "lambda-aws-handler",
      [
        {
          regex: /exports\.handler\s*=\s*(?:async\s*)?\(\s*event\b/,
          label: "Node.js exports.handler = (event, context) => ..."
        },
        {
          regex: /^\s*def\s+lambda_handler\s*\(\s*event\s*,\s*context\s*\)/m,
          label: "Python def lambda_handler(event, context)"
        },
        {
          regex: /\bimplements\s+RequestHandler<[^>]+>/,
          label: "Java RequestHandler<I,O> impl"
        },
        {
          regex: /\bAPIGateway(?:Proxy|V2)Event\b|\bAPIGatewayProxyResult\b/,
          label: "API Gateway event types"
        },
        {
          regex: /\bevent\.requestContext\.authorizer\b/,
          label: "API Gateway authorizer claim"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/lua-crypto-weakness.ts
var luaCryptoWeaknessMatcher = {
  noiseTier: "precise",
  slug: "lua-crypto-weakness",
  description: "Weak crypto patterns in Lua \u2014 hardcoded IVs, ECB mode, timing-unsafe comparisons",
  filePatterns: ["**/*.lua"],
  examples: [
    `local cipher = aes:new(key, "cbc", "ecb")`,
    `if computed_hmac == provided_hmac then end`,
    `if hmac_value == header_token then return true end`,
    `if hash_value == expected_hash then end`,
    `local digest = md5(payload)`,
    `local h = ngx.sha1(data)`,
    `local iv = "0123456789abcdef"`,
    `local d = ngx.md5(payload)`
  ],
  match(content, filePath) {
    if (/_test\.lua$|_spec\.lua$/.test(filePath)) return [];
    return regexMatcher(
      "lua-crypto-weakness",
      [
        { regex: /aes.{0,40}ecb|ecb.{0,40}aes/i, label: "AES ECB mode (no IV, deterministic)" },
        {
          regex: /==\s*.{0,40}hmac|hmac.{0,40}==/,
          label: "Timing-unsafe HMAC comparison (use constant-time)"
        },
        { regex: /==\s*.{0,40}hash|hash.{0,40}==/, label: "Timing-unsafe hash comparison" },
        { regex: /md5\s*\(|\.md5/, label: "MD5 usage" },
        { regex: /sha1\s*\(|\.sha1\b/, label: "SHA1 usage" },
        { regex: /local\s+iv\s*=\s*["']/, label: "Hardcoded IV value" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/lua-ngx-exec.ts
var luaNgxExecMatcher = {
  noiseTier: "precise",
  slug: "lua-ngx-exec",
  description: "Lua ngx.exec/ngx.redirect/os.execute/io.popen with dynamic content",
  filePatterns: ["**/*.lua"],
  examples: [
    `ngx.exec("/internal/" .. user_path)`,
    `ngx.redirect("https://example.com/" .. target)`,
    `os.execute("rm -rf " .. dir)`,
    `local fh = io.popen(cmd)`,
    `local res = ngx.location.capture("/proxy")`,
    `ngx.exec("@upstream")`
  ],
  match(content, filePath) {
    if (/_test\.lua$|_spec\.lua$/.test(filePath)) return [];
    return regexMatcher(
      "lua-ngx-exec",
      [
        { regex: /ngx\.exec\s*\(/, label: "ngx.exec (internal redirect)" },
        { regex: /ngx\.redirect\s*\(/, label: "ngx.redirect (external redirect)" },
        { regex: /os\.execute\s*\(/, label: "os.execute (shell command)" },
        { regex: /io\.popen\s*\(/, label: "io.popen (shell command)" },
        { regex: /ngx\.location\.capture\s*\(/, label: "ngx.location.capture (subrequest)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/lua-regex-bypass.ts
var luaRegexBypassMatcher = {
  noiseTier: "precise",
  slug: "lua-regex-bypass",
  description: "Lua regex patterns validating URLs/hosts \u2014 potential bypass via greedy wildcards",
  filePatterns: ["**/*.lua"],
  examples: [
    `local m = ngx.re.match(host, "^https://api\\\\.example\\\\.com")`,
    `if string.match(target, "^https://trusted") then end`,
    `local ok = string.find(host, "internal.host")`,
    `local valid_url = host:match(".+%.example%.com$")`,
    `if redirect_target:match(".*allowed.com.*") then end`,
    `local ok = ngx.re.match(host, "https?://[^/]+\\\\.com$")`
  ],
  match(content, filePath) {
    if (/_test\.lua$|_spec\.lua$/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const hasUrlRegex = /ngx\.re\.match\s*\(/.test(line) && /https?|host|domain|\.com|\.sh/.test(line) || /string\.(match|find)\s*\(/.test(line) && /https?|host|domain/.test(line);
      const hasGreedy = /\.\+|\.\*|%.+/.test(line);
      if (hasUrlRegex || hasGreedy && /url|host|domain|redirect/i.test(line)) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "lua-regex-bypass",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: hasUrlRegex ? "URL/host validation regex (verify not bypassable)" : "Greedy pattern in URL/host context"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/lua-shared-dict-poisoning.ts
var luaSharedDictPoisoningMatcher = {
  noiseTier: "normal",
  slug: "lua-shared-dict-poisoning",
  description: "Writes to ngx.shared dictionaries \u2014 cross-worker cache poisoning risk",
  filePatterns: ["**/*.lua"],
  examples: [
    `ngx.shared.cache:set(key, value)`,
    `ngx.shared.ratelimit:add(client_ip, 1, 60)`,
    `ngx.shared.tokens:replace("token_" .. user_id, payload)`,
    `ngx.shared.counters:incr(metric, 1)`,
    `local ok, err = ngx.shared.sessions:set(sid, data, 3600)`
  ],
  match(content, filePath) {
    if (/_test\.lua$|_spec\.lua$/.test(filePath)) return [];
    return regexMatcher(
      "lua-shared-dict-poisoning",
      [
        {
          regex: /ngx\.shared\.\w+:set\s*\(/,
          label: "ngx.shared dict :set() (verify key not request-derived)"
        },
        { regex: /ngx\.shared\.\w+:add\s*\(/, label: "ngx.shared dict :add()" },
        { regex: /ngx\.shared\.\w+:replace\s*\(/, label: "ngx.shared dict :replace()" },
        { regex: /ngx\.shared\.\w+:incr\s*\(/, label: "ngx.shared dict :incr()" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/lua-string-concat-url.ts
var luaStringConcatUrlMatcher = {
  noiseTier: "normal",
  slug: "lua-string-concat-url",
  description: "Lua URL construction via string concatenation \u2014 SSRF risk",
  filePatterns: ["**/*.lua"],
  examples: [
    `local url = "https://api.example.com/" .. user_path`,
    `local target = "http://internal.svc/v1/" .. ngx.var.arg_id`,
    `local endpoint = path .. "https://upstream.local/data"`,
    `local res = ngx.location.capture("/proxy/" .. backend_id)`,
    `request_uri = "/api/" .. tenant_id .. "/users"`,
    `local u = base .. "https://service" .. suffix`
  ],
  match(content, filePath) {
    if (/_test\.lua$|_spec\.lua$/.test(filePath)) return [];
    return regexMatcher(
      "lua-string-concat-url",
      [
        { regex: /["']https?:\/\/.*\.\./, label: "URL string concatenated with .." },
        { regex: /\.\..*["']https?:\/\//, label: "String concatenated into URL" },
        {
          regex: /ngx\.location\.capture\s*\(.*\.\./,
          label: "ngx.location.capture with concatenation"
        },
        { regex: /request_uri\s*=.*\.\./, label: "request_uri built via concatenation" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/mcp-tool-handler.ts
var mcpToolHandlerMatcher = {
  noiseTier: "precise",
  slug: "mcp-tool-handler",
  description: "MCP server tool handlers \u2014 verify per-tool authz + input validation",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["mcp"] },
  examples: [
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
server.tool("read_file", schema, async (args) => ({}));`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
registerTool(server, { name: "exec" });`,
    `import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";
server.setRequestHandler(CallToolRequestSchema, async (req) => ({}));`,
    `import { ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: [] }));`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
const server = new McpServer({ name: "x", version: "1" });`,
    `import { McpAgent } from "@modelcontextprotocol/sdk/server/index.js";
const agent = new McpAgent({ name: "x" });`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
server.resource("memo", uri, async () => ({}));`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
server.prompt("greet", schema, async (args) => ({}));`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
registerResource(server, { uri: "x" });`,
    `import { McpServer } from "@modelcontextprotocol/sdk/server/index.js";
registerPrompt(server, { name: "x" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_MCP = /\bfrom\s+["']@modelcontextprotocol\/sdk[^"']*["']|\bMcpServer\b|\bMcpAgent\b/;
    if (!HAS_MCP.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const PATTERNS2 = [
      { regex: /\bserver\.\s*tool\s*\(/, label: "MCP tool registration: server.tool(...)" },
      { regex: /\bregisterTool\s*\(/, label: "MCP registerTool(...)" },
      {
        regex: /setRequestHandler\s*\(\s*CallToolRequestSchema/,
        label: "MCP CallTool handler"
      },
      {
        regex: /setRequestHandler\s*\(\s*ListToolsRequestSchema/,
        label: "MCP ListTools handler \u2014 verify scope to authenticated client"
      },
      { regex: /\bnew McpServer\s*\(/, label: "MCP server construction site" },
      { regex: /\bnew McpAgent\s*\(/, label: "MCP agent construction site" },
      {
        regex: /\bregisterResource\s*\(|\bserver\.\s*resource\s*\(/,
        label: "MCP resource registration"
      },
      {
        regex: /\bregisterPrompt\s*\(|\bserver\.\s*prompt\s*\(/,
        label: "MCP prompt registration"
      }
    ];
    const hits = /* @__PURE__ */ new Set();
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          if (hits.has(i)) continue;
          hits.add(i);
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 5);
          matches.push({
            vulnSlug: "mcp-tool-handler",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/missing-auth.ts
var missingAuthMatcher = {
  noiseTier: "normal",
  slug: "missing-auth",
  description: "All HTTP request entry points \u2014 flagged as weak candidates for auth review",
  filePatterns: [
    "**/api/**/*.{ts,tsx,js,jsx}",
    "**/app/api/**/*.{ts,tsx,js,jsx}",
    "**/pages/api/**/*.{ts,tsx,js,jsx}",
    "**/routes/**/*.{ts,tsx,js,jsx}",
    "**/server/**/*.{ts,tsx,js,jsx}",
    "**/*.{ts,tsx,js,jsx}"
    // catch-all for non-standard layouts
  ],
  examples: [
    `export async function GET(req) { return Response.json({}); }`,
    `export function POST(req) { return new Response(""); }`,
    `export const GET = async () => Response.json({});`,
    `export let PUT = (req) => new Response("");`,
    `export default async function handler(req, res) { res.json({}); }`,
    `export default function (req, res) { res.end(); }`,
    `router.get("/items", (req, res) => res.json([]));`,
    `app.post("/login", handler);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const hasBackendAuth = [
      /withSchema\s*\(/,
      /withAuthentication\s*\(/,
      /authMiddleware/,
      /withAuth\s*\(/,
      /requireAuth/,
      /authTeamOrUserReq/,
      /performOIDCOrTeamOrUserAuth/
    ].some((p) => p.test(content));
    if (hasBackendAuth) return [];
    const matches = [];
    const lines = content.split("\n");
    const handlerPatterns = [
      // Next.js App Router route handlers
      {
        regex: /export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\b/,
        label: "Next.js App Router handler"
      },
      {
        regex: /export\s+(const|let)\s+(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s*=/,
        label: "Next.js App Router handler (arrow)"
      },
      // Next.js Pages API routes
      {
        regex: /export\s+default\s+(async\s+)?function/,
        label: "default export handler"
      },
      // Express / Fastify / Hono style
      {
        regex: /router\.(get|post|put|patch|delete|all)\s*\(/,
        label: "router method handler"
      },
      {
        regex: /app\.(get|post|put|patch|delete|all)\s*\(/,
        label: "app method handler"
      },
      // Hono
      {
        regex: /\.route\s*\(\s*['"]\//,
        label: "route definition"
      }
    ];
    for (const { regex, label } of handlerPatterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "missing-auth",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: `HTTP entry point: ${label} (weak candidate)`
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/missing-await.ts
var missingAwaitMatcher = {
  noiseTier: "normal",
  slug: "missing-await",
  description: "Async calls that may be missing await \u2014 race conditions, lost errors",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `withMutex(() => doStuff());`,
    `withUserMutex(() => updateUser(id));`,
    `withLock(key, () => criticalSection());`,
    `withDistributedLock(key, fn);`,
    `withTransaction(async (tx) => {
  await tx.user.update({ id });
});`,
    `withDbTransaction(fn);`,
    `redis.get("key");`,
    `redis.set(key, value);`,
    `prisma.user.findUnique({ where: { id } });`,
    `prisma.session.delete({ where: { id } });`,
    `db.users.findOne({ id });`,
    `db.posts.update({ id });`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const criticalPatterns = [
      { regex: /(?<!await\s)(?<!return\s)with\w*Mutex\s*\(/, label: "mutex without await" },
      { regex: /(?<!await\s)(?<!return\s)with\w*Lock\s*\(/, label: "lock without await" },
      {
        regex: /(?<!await\s)(?<!return\s)with\w*Transaction\s*\(/,
        label: "transaction without await"
      },
      { regex: /(?<!await\s)(?<!return\s)redis\.\w+\s*\(/, label: "redis call without await" },
      {
        regex: /(?<!await\s)(?<!return\s)prisma\.\w+\.\w+\s*\(/,
        label: "prisma call without await"
      },
      { regex: /(?<!await\s)(?<!return\s)db\.\w+\.\w+\s*\(/, label: "db call without await" }
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.startsWith("//") || line.startsWith("*")) continue;
      for (const { regex, label } of criticalPatterns) {
        if (regex.test(line)) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "missing-await",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/non-atomic-operation.ts
var nonAtomicOperationMatcher = {
  noiseTier: "normal",
  slug: "non-atomic-operation",
  description: "Read-then-write without transaction/lock \u2014 TOCTOU race condition risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `async function transfer(id) {
  const account = await db.account.findById(id);
  if (account.balance < 100) return;
  await db.account.update({ id, balance: account.balance - 100 });
}`,
    `const user = await prisma.user.findUnique({ where: { id } });
if (!user) throw new Error("missing");
await prisma.user.delete({ where: { id } });`,
    `const item = await repo.findOne({ id });
await repo.save({ ...item, count: item.count + 1 });`,
    `const row = await store.findFirst({ where: { key } });
const next = row.value + 1;
await store.update({ where: { key }, data: { value: next } });`,
    `const order = await orders.findUnique({ where: { id } });
await orders.modify({ id: order.id });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const hasReadWrite = /findById|getById|findOne|findUnique|findFirst/.test(content) && /update|delete|remove|modify|save|create/.test(content);
    if (!hasReadWrite) return [];
    if (/transaction\s*\(|\.transact\(|BEGIN|COMMIT|withLock|mutex|atomicUpdate/.test(content))
      return [];
    const matches = [];
    const lines = content.split("\n");
    const readPatterns = [
      /await.*find(ById|One|Unique|First)\s*\(/,
      /await.*get\w+By(Id|Uid)\s*\(/
    ];
    for (let i = 0; i < lines.length; i++) {
      if (!readPatterns.some((p) => p.test(lines[i]))) continue;
      const window = lines.slice(i + 1, Math.min(lines.length, i + 15)).join("\n");
      if (/await.*(update|delete|remove|modify|save)\s*\(/.test(window)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 5);
        matches.push({
          vulnSlug: "non-atomic-operation",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Read-then-write without transaction \u2014 verify atomicity"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/non-atomic-read-delete.ts
var nonAtomicReadDeleteMatcher = {
  noiseTier: "normal",
  slug: "non-atomic-read-delete",
  description: "Non-atomic read-then-delete/update \u2014 TOCTOU race conditions",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const cached = await redis.get(key);
if (!cached) return null;
await redis.del(key);`,
    `const value = await redis.hget(bucket, field);
await redis.hdel(bucket, field);`,
    `const session = await redis.hgetall(\`session:\${id}\`);
await redis.set(\`session:\${id}\`, "expired");`,
    `const row = await db.findFirst({ where: { id } });
await db.deleteMany({ where: { id: row.id } });`,
    `const r = await client.findUnique({ where: { id } });
await client.destroy(r.id);`,
    `// SELECT something
const r = await query("SELECT * FROM tokens WHERE id = $1", [id]);
await query("DELETE FROM tokens WHERE id = $1", [id]);`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/redis\.(get|hget|hgetall)\s*\(/.test(line)) {
        const window = lines.slice(i, Math.min(lines.length, i + 10)).join("\n");
        if (/redis\.(del|hdel|set|hset|expire)\s*\(/.test(window)) {
          const txWindow = lines.slice(Math.max(0, i - 5), Math.min(lines.length, i + 15)).join("\n");
          if (!/\.multi\s*\(|\.pipeline\s*\(|\.transaction\s*\(|WATCH/.test(txWindow)) {
            const start = Math.max(0, i - 1);
            const end = Math.min(lines.length, i + 5);
            matches.push({
              vulnSlug: "non-atomic-read-delete",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: "Redis get-then-delete/set without transaction \u2014 TOCTOU race"
            });
          }
        }
      }
      if (/\b(SELECT|findFirst|findUnique|findOne)\b/i.test(line)) {
        const window = lines.slice(i, Math.min(lines.length, i + 15)).join("\n");
        if (/\b(DELETE|UPDATE|destroy|remove|deleteMany)\b/i.test(window)) {
          const txWindow = lines.slice(Math.max(0, i - 5), Math.min(lines.length, i + 20)).join("\n");
          if (!/\$transaction\s*\(|BEGIN|SERIALIZABLE|\.transaction\s*\(/.test(txWindow)) {
            const start = Math.max(0, i - 1);
            const end = Math.min(lines.length, i + 5);
            matches.push({
              vulnSlug: "non-atomic-read-delete",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: "Read-then-modify without transaction \u2014 potential TOCTOU race"
            });
          }
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/oauth-flow.ts
var oauthFlowMatcher = {
  noiseTier: "normal",
  slug: "oauth-flow",
  description: "OAuth authorize/callback endpoints and token-bearing redirects",
  filePatterns: [
    "**/oauth/**/*.{ts,tsx}",
    "**/auth/**/*.{ts,tsx}",
    "**/callback/**/*.{ts,tsx}",
    "**/app/api/**/*.{ts,tsx}",
    "**/api/**/*.{ts,tsx}"
  ],
  examples: [
    `const redirect_uri = req.query.redirect_uri;`,
    `params.append("redirect_uri", url);`,
    `body.set("grant_type", "authorization_code");`,
    `const grantType = "authorization_code";`,
    `params.set("code_verifier", verifier);`,
    `const code_challenge = sha256(code_verifier);`,
    `const u = "https://idp/cb?state=" + s + "&redirect=" + r;`,
    `// redirect handler with state= param parsing`,
    `const url = "https://app/cb?code=" + c;`,
    `if (qs.includes("&code=")) handle();`,
    `// access_token in redirect URL`,
    `// access_token returned via callback URL token=`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const isOAuthPath = /oauth|callback|authorize/i.test(filePath);
    const hasOAuthCode = /redirect_uri|authorization_code|code_verifier|state=|code=|access_token/.test(content);
    if (!isOAuthPath && !hasOAuthCode) return [];
    return regexMatcher(
      "oauth-flow",
      [
        { regex: /redirect_uri/, label: "OAuth redirect_uri handling" },
        { regex: /authorization_code|grant_type/, label: "OAuth authorization code flow" },
        { regex: /code_verifier|code_challenge/, label: "PKCE flow" },
        {
          regex: /state=.{0,80}redirect|redirect.{0,80}state=/,
          label: "OAuth state + redirect"
        },
        { regex: /\?code=|&code=/, label: "Authorization code in URL" },
        {
          regex: /access_token.{0,80}redirect|redirect.{0,80}access_token/,
          label: "Token in redirect URL"
        },
        {
          regex: /callback.{0,80}token|token.{0,80}callback/,
          label: "Token in callback"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/object-injection.ts
var objectInjectionMatcher = {
  noiseTier: "normal",
  slug: "object-injection",
  description: "Prototype pollution via Object.assign/merge/defaults with user input",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const merged = Object.assign({}, req.body);`,
    `Object.assign({ }, params, defaults);`,
    `const out = _.merge({}, defaults, req.body);`,
    `lodash.merge(target, source);`,
    `import { merge } from "lodash/merge";
const out = lodash.merge(target, userInput);`,
    `deepMerge(target, payload);`,
    `_.defaultsDeep(opts, userOpts);`,
    `defaultsDeep(target, source);`,
    `obj[req.query] = "value";`,
    `body[userKey] = req.params.id;`,
    `params[someKey] = 1;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "object-injection",
      [
        {
          regex: /Object\.assign\s*\(\s*\{\s*\}\s*,\s*(req|body|params|query)/,
          label: "Object.assign from user input"
        },
        {
          regex: /lodash[\w./]{0,20}merge\s*\(|_\.merge\s*\(|deepMerge\s*\(/,
          label: "Deep merge (prototype pollution risk)"
        },
        {
          regex: /_\.defaultsDeep\s*\(|defaultsDeep\s*\(/,
          label: "defaultsDeep (prototype pollution)"
        },
        {
          regex: /\[req\.\w+\]|body\[[^\]]{0,80}\]\s*=|params\[[^\]]{0,80}\]\s*=/,
          label: "Dynamic property assignment from user input"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/open-redirect.ts
var openRedirectMatcher = {
  noiseTier: "normal",
  slug: "open-redirect",
  description: "Redirects with user-controlled URLs",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `redirect(req.body.next);`,
    `redirect(query.target);`,
    "redirect(`${origin}/${req.body.path}`);",
    `res.redirect(req.body.url);`,
    `res.redirect(params.next);`,
    `headers: { Location: req.body.next }`,
    `window.location = params.next;`,
    `const u = returnUrl;`,
    `const r = redirectUrl;`,
    `const x = returnTo;`
  ],
  match(content, _filePath) {
    return regexMatcher(
      "open-redirect",
      [
        {
          regex: /redirect\s*\(\s*(req\.|request\.|params\.|query\.|body\.)/,
          label: "redirect with request-derived URL"
        },
        { regex: /redirect\s*\(\s*`[^`]*\$\{/, label: "redirect with interpolated URL" },
        {
          regex: /res\.redirect\s*\(\s*(req\.|request\.|params\.|query\.|body\.)/,
          label: "res.redirect with request-derived URL"
        },
        {
          regex: /Location.*:\s*(req\.|request\.|params\.|query\.|body\.)/,
          label: "Location header from request data"
        },
        {
          regex: /window\.location\s*=\s*(req|params|query|searchParams)/,
          label: "window.location from user input"
        },
        { regex: /returnUrl|redirectUrl|returnTo|next.*url/i, label: "redirect URL parameter" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/path-traversal.ts
var pathTraversalMatcher = {
  noiseTier: "noisy",
  slug: "path-traversal",
  description: "File system operations with user-controlled paths",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `readFile(req.body.path, cb);`,
    `readFileSync(params.file);`,
    "readFile(`${root}/${req.body.path}`);",
    `writeFile(req.body.target, data, cb);`,
    "writeFileSync(`/data/${request.body.name}`, blob);",
    `path.join(root, req.body.subdir);`,
    `path.resolve(base, params.dir);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const _userInputPattern = /req\.|request\.|params\.|query\.|body\.|parsed\.|searchParams|\.input\b/;
    return regexMatcher(
      "path-traversal",
      [
        {
          regex: /readFile(Sync)?\s*\(\s*(req\.|request\.|params\.|query\.|body\.|parsed\.)/,
          label: "readFile with request-derived path"
        },
        {
          regex: /readFile(Sync)?\s*\(\s*`[^`]*(req\.|request\.|params\.|query\.|body\.)/,
          label: "readFile with request-derived interpolation"
        },
        {
          regex: /writeFile(Sync)?\s*\(\s*(req\.|request\.|params\.|query\.|body\.|parsed\.)/,
          label: "writeFile with request-derived path"
        },
        {
          regex: /writeFile(Sync)?\s*\(\s*`[^`]*(req\.|request\.|params\.|query\.|body\.)/,
          label: "writeFile with request-derived interpolation"
        },
        {
          regex: /path\.join\s*\([^)]*\b(req\.|request\.|params\.|query\.|body\.|parsed\.)/,
          label: "path.join with request-derived input"
        },
        {
          regex: /path\.resolve\s*\([^)]*\b(req\.|request\.|params\.|query\.|body\.|parsed\.)/,
          label: "path.resolve with request-derived input"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-cakephp-controller.ts
var phpCakephpControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-cakephp-controller",
  description: "CakePHP controllers and component callbacks (gated on CakePHP)",
  filePatterns: ["**/src/Controller/**/*.php", "**/Controller/**/*.php"],
  requires: { tech: ["cakephp"] },
  examples: [
    `class UsersController extends AppController { }`,
    `class PostsController extends AppController
{
    public function index() {}
}`,
    `$this->Auth->allow(['login', 'register']);`,
    `$this->Auth->allow();`,
    `$this->loadComponent('Auth', ['authenticate' => ['Form']]);`,
    `$this->loadComponent("Auth");`,
    `$data = $this->request->getData();`,
    `$name = $this->request->getData('name');`,
    `$this->Flash->success(__('Saved.'));`,
    `$this->Flash->error('Failed');`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-cakephp-controller",
      [
        {
          regex: /class\s+\w+Controller\s+extends\s+AppController\b/,
          label: "CakePHP controller class"
        },
        { regex: /\$this->Auth->allow\s*\(/, label: "Auth->allow() \u2014 opens public access" },
        { regex: /\$this->loadComponent\s*\(\s*['"]Auth['"]/, label: "Auth component wiring" },
        { regex: /\$this->request->getData\s*\(/, label: "request data accessor" },
        { regex: /\$this->Flash->/, label: "flash response (post-redirect-get)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-codeigniter-controller.ts
var phpCodeigniterControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-codeigniter-controller",
  description: "CodeIgniter 4 controllers and route mappings (gated on CodeIgniter)",
  filePatterns: ["**/app/Controllers/**/*.php", "**/Controllers/**/*.php"],
  requires: { tech: ["codeigniter"] },
  examples: [
    `class Home extends BaseController { public function index() {} }`,
    `class Users extends ResourceController
{
    protected $modelName = 'App\\Models\\UserModel';
}`,
    `class Auth extends Controller { }`,
    `$name = $this->request->getVar('name');`,
    `$body = $this->request->getPost();`,
    `$id = $this->request->getPost("id");`,
    `$routes->get('/', 'Home::index');`,
    `$routes->post("/login", 'Auth::login');`,
    `$routes->add('/x', 'X::y', ['GET', 'POST']);`,
    `helper('form');`,
    `helper("url");`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-codeigniter-controller",
      [
        {
          regex: /class\s+\w+\s+extends\s+(?:BaseController|ResourceController|Controller)\b/,
          label: "CI Controller class"
        },
        {
          regex: /\$this->request->getVar\s*\(|\$this->request->getPost\s*\(/,
          label: "request var accessor"
        },
        {
          regex: /\$routes->(?:get|post|put|patch|delete|add)\s*\(/,
          label: "$routes-> registration"
        },
        {
          regex: /helper\s*\(\s*['"][^'"]+['"]\s*\)/,
          label: "helper() \u2014 review for unsafe loaders"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-drupal-controller.ts
var phpDrupalControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-drupal-controller",
  description: "Drupal controllers, routes, and form callbacks (gated on Drupal)",
  filePatterns: [
    "**/src/Controller/**/*.php",
    "**/modules/**/*.php",
    "**/modules/**/*.routing.yml"
  ],
  requires: { tech: ["drupal"] },
  examples: [
    `class UserController extends ControllerBase { public function view() {} }`,
    `class NodeListController extends ControllerBase
{
    public function build() { return []; }
}`,
    `requirements:
  _permission: 'access content'`,
    `requirements: { _permission: "access content" }`,
    `public function buildForm(array $form, FormStateInterface $form_state) { return $form; }`,
    `public function buildForm( array $form, FormStateInterface $form_state ) {}`,
    `$request = \\Drupal::request();`,
    `$ip = \\Drupal::request()->getClientIp();`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor|core\/tests)\//.test(filePath)) return [];
    return regexMatcher(
      "php-drupal-controller",
      [
        {
          regex: /class\s+\w+\s+extends\s+ControllerBase\b/,
          label: "Drupal ControllerBase subclass"
        },
        {
          regex: /_permission\s*:\s*['"]access\s+content['"]/,
          label: "permission: access content (public-ish route)"
        },
        { regex: /buildForm\s*\(\s*array\s+\$form/, label: "FormBase::buildForm() entry" },
        { regex: /\\Drupal::request\s*\(\s*\)/, label: "request() service accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-laravel-route.ts
var phpLaravelRouteMatcher = {
  noiseTier: "noisy",
  slug: "php-laravel-route",
  description: "Laravel route registrations and controller actions (gated on Laravel)",
  filePatterns: ["**/routes/**/*.php", "**/app/Http/Controllers/**/*.php"],
  requires: {
    tech: ["laravel"],
    sentinelFiles: ["composer.json", "artisan"],
    sentinelContains: (path, content) => {
      if (path === "artisan") return true;
      try {
        const pkg = JSON.parse(content);
        const deps = { ...pkg.require, ...pkg["require-dev"] };
        return Object.keys(deps ?? {}).some((k) => k.startsWith("laravel/"));
      } catch {
        return false;
      }
    }
  },
  examples: [
    `Route::get('/users', [UsersController::class, 'index']);`,
    `Route::post("/login", [AuthController::class, "login"])->middleware('guest');`,
    `Route::match(['get', 'post'], '/x', $handler);`,
    `Route::resource('posts', PostsController::class);`,
    `Route::group(['middleware' => 'auth'], function () { /* ... */ });`,
    `class UsersController extends Controller { public function show($id) {} }`,
    `Route::get('/me', fn () => auth()->user())->middleware('auth:sanctum');`,
    `$data = $request->all();`,
    `DB::raw("COUNT(*) as total")`,
    `User::whereRaw('LOWER(email) = ?', [$email])->orderByRaw('created_at DESC')->selectRaw('id, name');`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-laravel-route",
      [
        {
          regex: /Route::(get|post|put|patch|delete|any|match)\s*\(/,
          label: "Route::* registration"
        },
        { regex: /Route::resource\s*\(/, label: "Route::resource (CRUD)" },
        { regex: /Route::group\s*\(/, label: "Route::group (middleware scope)" },
        {
          regex: /class\s+\w+Controller\s+extends\s+\w*Controller\b/,
          label: "Controller class"
        },
        { regex: /->middleware\s*\(\s*['"]auth/, label: "Auth middleware (verify scope)" },
        {
          regex: /\$request->all\s*\(\s*\)/,
          label: "$request->all() \u2014 mass-assignment surface"
        },
        { regex: /DB::raw\s*\(/, label: "DB::raw (SQL injection if interpolated)" },
        {
          regex: /\b(?:whereRaw|selectRaw|orderByRaw)\s*\(/,
          label: "*Raw query helper"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-magento-controller.ts
var phpMagentoControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-magento-controller",
  description: "Magento 2 controllers and webapi routes (gated on Magento)",
  filePatterns: ["**/Controller/**/*.php", "**/etc/webapi.xml"],
  requires: { tech: ["magento"] },
  examples: [
    `class Index extends \\Magento\\Framework\\App\\Action\\Action { public function execute() {} }`,
    `class View extends Magento\\Framework\\App\\Action\\Action
{
    public function execute() {}
}`,
    `class Get implements \\Magento\\Framework\\App\\Action\\HttpGetActionInterface { }`,
    `class List implements Magento\\Framework\\App\\HttpGetActionInterface { }`,
    `<route url="/V1/products" method="GET">`,
    `<route url='/V1/orders/:orderId' method='POST'>`,
    `<route url="/V1/customers/me" method="PUT">`,
    `$id = $this->getRequest()->getParam('id');`,
    `$sku = $this->getRequest( )->getParam("sku");`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor|dev\/tests)\//.test(filePath)) return [];
    return regexMatcher(
      "php-magento-controller",
      [
        {
          regex: /extends\s+\\?Magento\\Framework\\App\\Action\\Action\b/,
          label: "Magento Action subclass"
        },
        {
          regex: /implements\s+\\?Magento\\Framework\\App\\(?:Action\\)?HttpGetActionInterface/,
          label: "HttpGetActionInterface implementation"
        },
        {
          regex: /<route\s+url=["'][^"']+["']\s+method=["'][A-Z]+["']/,
          label: "webapi.xml <route> declaration"
        },
        { regex: /\$this->getRequest\s*\(\s*\)->getParam\s*\(/, label: "request param accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-slim-route.ts
var phpSlimRouteMatcher = {
  noiseTier: "noisy",
  slug: "php-slim-route",
  description: "Slim Framework route registrations (gated on Slim)",
  filePatterns: ["**/*.php"],
  requires: { tech: ["slim"] },
  examples: [
    `$app->get('/users', function ($request, $response) { return $response; });`,
    `$app->post("/login", LoginAction::class);`,
    `$app->put('/items/{id}', $handler);`,
    `$app->patch('/items/{id}', $handler);`,
    `$app->delete('/items/{id}', $handler);`,
    `$app->any('/health', $healthHandler);`,
    `$app->map(['GET', 'POST'], '/x', $h);`,
    `$app->group('/api', function ($group) { /* ... */ })->add(new AuthMiddleware());`,
    `$app->add(new SessionMiddleware($settings));`,
    `$body = $request->getParsedBody();`,
    `$id = $request->getAttribute('id');`,
    `$q = $request->getQueryParams();`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-slim-route",
      [
        {
          regex: /\$app->(?:get|post|put|patch|delete|map|any)\s*\(/,
          label: "$app->method route registration"
        },
        { regex: /\$app->group\s*\(/, label: "$app->group(...) middleware scope" },
        { regex: /->add\s*\(\s*new\s+\w+Middleware/, label: "->add(new ...Middleware) attach" },
        {
          regex: /\$request->(?:getQueryParams|getParsedBody|getAttribute)\s*\(/,
          label: "PSR-7 request accessor"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-sql-raw.ts
var phpSqlRawMatcher = {
  noiseTier: "normal",
  slug: "php-sql-raw",
  description: "Raw SQL across PHP DB drivers (PDO, mysqli, Doctrine ORM/DBAL) \u2014 string concatenation is SQL injection",
  filePatterns: ["**/*.php"],
  requires: { tech: ["php"] },
  examples: [
    `<?php
$result = $pdo->query("SELECT * FROM users WHERE id = " . $id);`,
    `$pdo->exec("DELETE FROM users WHERE name = '" . $name . "'");`,
    `$stmt = $pdo->prepare("SELECT * FROM t WHERE col = '" . $col . "'");`,
    `mysqli_query($conn, "SELECT * FROM users WHERE id = " . $userId);`,
    `$conn->executeQuery("UPDATE users SET role = '" . $role . "' WHERE id = " . $id);`,
    `$conn->executeStatement("DELETE FROM users WHERE id = " . $id);`,
    `$em->createQuery("SELECT u FROM App\\User u WHERE u.name = '" . $name . "'");`,
    `$em->createNativeQuery("SELECT * FROM users WHERE id = " . $id, $rsm);`,
    `$sql = "INSERT INTO logs (msg) VALUES ('" . $msg . "')";`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    const QSTR = `(?:"[^"]{0,400}"|'[^']{0,400}')`;
    return regexMatcher(
      "php-sql-raw",
      [
        // PDO
        {
          regex: new RegExp(`\\$\\w+->query\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "PDO->query with string concat (SQL injection)"
        },
        {
          regex: new RegExp(`\\$\\w+->exec\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "PDO->exec with string concat (SQL injection)"
        },
        {
          regex: new RegExp(`\\$\\w+->prepare\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "PDO->prepare with concat (defeats parameterization)"
        },
        { regex: /new\s+PDO\s*\(/, label: "PDO connection (informational)" },
        // mysqli
        {
          regex: new RegExp(`mysqli_query\\s*\\(\\s*[^,]+,\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "mysqli_query with string concat (SQL injection)"
        },
        {
          regex: /mysqli_real_escape_string/,
          label: "mysqli_real_escape_string (informational \u2014 manual escaping)"
        },
        // Doctrine DBAL
        {
          regex: new RegExp(`\\$\\w+->executeQuery\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "Doctrine DBAL executeQuery with concat (SQL injection)"
        },
        {
          regex: new RegExp(`\\$\\w+->executeStatement\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "Doctrine DBAL executeStatement with concat (SQL injection)"
        },
        // Doctrine ORM
        {
          regex: new RegExp(`\\$\\w+->createQuery\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "Doctrine ORM createQuery (DQL) with concat (injection)"
        },
        {
          regex: new RegExp(`\\$\\w+->createNativeQuery\\s*\\(\\s*${QSTR}\\s*\\.\\s*\\$`),
          label: "Doctrine ORM createNativeQuery with concat (SQL injection)"
        },
        // Generic SQL keywords with concat — match a quoted SQL literal
        // followed by `.` `$var`. The opening quote dictates the matching
        // closing quote, so `'` inside a `"..."` string is fine.
        {
          regex: /(?:"\s*(?:SELECT|INSERT|UPDATE|DELETE)\s+[^"]{0,400}"|'\s*(?:SELECT|INSERT|UPDATE|DELETE)\s+[^']{0,400}')\s*\.\s*\$\w+/,
          label: "Raw SQL string with concat (SQL injection)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-symfony-controller.ts
var phpSymfonyControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-symfony-controller",
  description: "Symfony controllers and route attributes (gated on Symfony)",
  filePatterns: ["**/src/**/*.php", "**/src/Controller/**/*.php", "**/Controller/**/*.php"],
  requires: { tech: ["symfony"] },
  examples: [
    `#[Route('/users', name: 'users_index', methods: ['GET'])]`,
    `#[ Route("/api/items/{id}", methods: ["GET", "POST"]) ]`,
    `class UsersController extends AbstractController { }`,
    `class PostController extends AbstractController
{
    public function index(): Response {}
}`,
    `#[IsGranted('ROLE_ADMIN')]`,
    `#[ IsGranted ( 'ROLE_USER' )]`,
    `#[AsEventListener(event: 'kernel.request')]`,
    `#[AsMessageHandler()]`,
    `$user = $this->getUser();`,
    `if ($this->getUser() === null) { throw new AccessDeniedException(); }`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-symfony-controller",
      [
        { regex: /#\[\s*Route\s*\(/, label: "#[Route] attribute" },
        {
          regex: /class\s+\w+Controller\s+extends\s+AbstractController\b/,
          label: "Symfony controller class"
        },
        { regex: /#\[\s*IsGranted\s*\(/, label: "#[IsGranted] auth gate" },
        { regex: /#\[\s*AsEventListener\s*\(/, label: "Event listener entry point" },
        { regex: /#\[\s*AsMessageHandler\s*\(/, label: "Messenger handler entry point" },
        { regex: /\$this->getUser\s*\(\s*\)/, label: "auth identity accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-wordpress-rest.ts
var phpWordpressRestMatcher = {
  noiseTier: "noisy",
  slug: "php-wordpress-rest",
  description: "WordPress REST routes, AJAX hooks, and shortcodes (gated on WordPress)",
  filePatterns: ["**/*.php"],
  requires: { tech: ["wordpress"] },
  examples: [
    `register_rest_route('myplugin/v1', '/items', ['methods' => 'GET', 'callback' => 'my_cb']);`,
    `register_rest_route( 'myplugin/v1', '/users/(?P<id>\\d+)', array( 'methods' => 'POST', 'callback' => 'cb' ) );`,
    `add_action('wp_ajax_save_settings', 'my_save_settings');`,
    `add_action("wp_ajax_nopriv_get_data", 'public_get_data');`,
    `add_shortcode('my_widget', 'render_my_widget');`,
    `add_shortcode("featured_posts", "render_featured");`,
    `register_rest_route('ns/v1', '/public', ['permission_callback' => '__return_true', 'callback' => 'cb']);`,
    `$id = $_GET['id'];`,
    `$body = $_POST;`,
    `$ua = $_SERVER['HTTP_USER_AGENT'];`,
    `$token = $_COOKIE['token'];`,
    `$val = $_REQUEST['x'];`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor|wp-includes|wp-admin)\//.test(filePath)) return [];
    return regexMatcher(
      "php-wordpress-rest",
      [
        { regex: /register_rest_route\s*\(/, label: "register_rest_route() \u2014 REST endpoint" },
        {
          regex: /add_action\s*\(\s*['"]wp_ajax_(?:nopriv_)?[^'"]+['"]/,
          label: "wp_ajax_*/wp_ajax_nopriv_* hook (nopriv = unauthenticated)"
        },
        { regex: /add_shortcode\s*\(/, label: "add_shortcode() \u2014 user-content surface" },
        {
          regex: /'permission_callback'\s*=>\s*'__return_true'/,
          label: "permission_callback => __return_true (public REST route)"
        },
        {
          regex: /\$_(?:GET|POST|REQUEST|COOKIE|SERVER)\b/,
          label: "PHP superglobal (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/php-yii-controller.ts
var phpYiiControllerMatcher = {
  noiseTier: "noisy",
  slug: "php-yii-controller",
  description: "Yii2 controller classes and actionXxx methods (gated on Yii)",
  filePatterns: ["**/controllers/**/*.php", "**/src/controllers/**/*.php"],
  requires: { tech: ["yii"] },
  examples: [
    `class SiteController extends Controller { }`,
    `class UsersController extends ActiveController
{
    public $modelClass = 'app\\models\\User';
}`,
    `class ApiController extends RestController { }`,
    `public function actionIndex() { return $this->render('index'); }`,
    `public function actionCreate ($id) { /* ... */ }`,
    `public function actionViewProfile() { }`,
    `public function behaviors() {
    return [
        'access' => ['class' => AccessControl::class],
    ];
}`,
    `'authenticator' => ['class' => HttpBearerAuth::class, 'except' => ContentNegotiator::class],`,
    `return ['access' => ['class' => AccessControl::class, 'rules' => []]];`
  ],
  match(content, filePath) {
    if (/\/(tests|vendor)\//.test(filePath)) return [];
    return regexMatcher(
      "php-yii-controller",
      [
        {
          regex: /class\s+\w+Controller\s+extends\s+(?:Controller|ActiveController|RestController)\b/,
          label: "Yii Controller class"
        },
        {
          regex: /public\s+function\s+action[A-Z]\w*\s*\(/,
          label: "actionXxx() \u2014 Yii public action"
        },
        { regex: /\bbehaviors\s*\(\s*\)\s*[:{]/, label: "behaviors() \u2014 verify auth filter" },
        {
          regex: /AccessControl::class|ContentNegotiator::class/,
          label: "auth/behavior class wired up"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/postmessage-origin.ts
var postmessageOriginMatcher = {
  noiseTier: "precise",
  slug: "postmessage-origin",
  description: "postMessage handlers without origin validation \u2014 XSS via malicious parent frame",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `window.addEventListener("message", (event) => {
  document.body.innerHTML = event.data;
});`,
    `window.addEventListener('message', handleMsg);`,
    `iframe.onmessage = (e) => {
  console.log(e.data);
};`,
    `frame.onmessage = function (e) { dispatch(e.data); };`,
    `addEventListener("message", function (event) {
  if (event.origin !== "https://trusted.example") return;
  doStuff(event.data);
});`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (!/addEventListener.*message|onmessage/.test(content)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      if (/addEventListener\s*\(\s*['"]message['"]/.test(lines[i]) || /\.onmessage\s*=/.test(lines[i])) {
        const window = lines.slice(i, Math.min(lines.length, i + 10)).join("\n");
        const hasOriginCheck = /event\.origin|\.origin\s*[!=]==?|origin.*check|validat.*origin/.test(window);
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 5);
        matches.push({
          vulnSlug: "postmessage-origin",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: hasOriginCheck ? "postMessage handler with origin check (verify strictness)" : "postMessage handler WITHOUT origin validation"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/prisma-raw-sql.ts
var prismaRawSqlMatcher = {
  noiseTier: "precise",
  slug: "prisma-raw-sql",
  description: "Prisma raw SQL ($queryRaw / $executeRaw / *Unsafe) \u2014 verify parameterization and source of inputs",
  filePatterns: ["**/*.{ts,tsx,js,jsx,mjs,cjs}"],
  requires: { tech: ["prisma"] },
  examples: [
    `await prisma.$queryRawUnsafe(\`SELECT * FROM users WHERE name = '\${name}'\`);`,
    `await prisma.$executeRawUnsafe("DELETE FROM users WHERE id = " + id);`,
    `await prisma.$queryRaw(query);`,
    `await prisma.$executeRaw(query);`,
    `await prisma.$queryRaw\`SELECT * FROM users WHERE name = \${name}\`;`,
    `await prisma.$executeRaw\`UPDATE users SET name = \${name}\`;`,
    `await prisma.$queryRaw(Prisma.raw(\`SELECT * FROM \${tableName}\`));`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    return regexMatcher(
      "prisma-raw-sql",
      [
        {
          regex: /\$queryRawUnsafe\s*\(/,
          label: "$queryRawUnsafe \u2014 string-built SQL, no parameterization"
        },
        {
          regex: /\$executeRawUnsafe\s*\(/,
          label: "$executeRawUnsafe \u2014 string-built SQL, no parameterization"
        },
        // Tagged-template form is safe; non-template invocation is not.
        // Heuristic: flag $queryRaw/$executeRaw followed by `(` instead of a backtick.
        {
          regex: /\$queryRaw\s*\(/,
          label: "$queryRaw called as function (not tagged template) \u2014 verify parameterization"
        },
        {
          regex: /\$executeRaw\s*\(/,
          label: "$executeRaw called as function (not tagged template) \u2014 verify parameterization"
        },
        // Tagged-template form: still worth a look because the interpolated values
        // could still be unsafe if mixed with Prisma.sql/raw constructions.
        {
          regex: /\$queryRaw\s*`[^`]*\$\{/,
          label: "$queryRaw template with interpolation \u2014 verify Prisma.raw isn't mixed in"
        },
        {
          regex: /\$executeRaw\s*`[^`]*\$\{/,
          label: "$executeRaw template with interpolation \u2014 verify Prisma.raw isn't mixed in"
        },
        {
          regex: /Prisma\.raw\s*\(/,
          label: "Prisma.raw \u2014 bypasses parameterization, must not include user input"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/process-env-access.ts
var processEnvAccessMatcher = {
  noiseTier: "noisy",
  slug: "process-env-access",
  description: "Direct process.env access \u2014 check for fallbacks, leaks, and misuse",
  filePatterns: ["**/*.{ts,tsx,js,jsx}", "**/*.lua", "**/*.go"],
  examples: [
    `const url = process.env.DATABASE_URL;`,
    `const key = process.env.API_KEY ?? "fallback";`,
    `if (process.env.NODE_ENV === "development") doStuff();`,
    `const cfg = process.env["MY_VAR"];`,
    `const secret = process.env['SESSION_SECRET'];`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\/|\.d\.ts$/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const envMatch = line.match(/process\.env\.(\w+)|process\.env\[['"](\w+)['"]\]/);
      if (!envMatch) continue;
      const varName = envMatch[1] || envMatch[2];
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 2);
      matches.push({
        vulnSlug: "process-env-access",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: `process.env.${varName}`
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/prompt-leaks-system-prompt.ts
var promptLeaksSystemPromptMatcher = {
  noiseTier: "normal",
  slug: "prompt-leaks-system-prompt",
  description: "System prompt embeds env-var secrets / API tokens \u2014 verify nothing leaks via traces or model output",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  // Examples cover the env-var leak path (the higher-signal one — most
  // hardcoded-secret bugs are also caught by `secrets-exposure`). The
  // hardcoded-token-prefix path is exercised by the SECRET_ENV_VAR /
  // HARDCODED_SECRET regexes below; we don't include literal example
  // strings of those shapes here because GitHub push-protection rejects
  // any diff that contains a contiguous Stripe / GitHub-PAT / Slack /
  // AWS key shape, even when the body is obvious-placeholder.
  examples: [
    `await streamText({
  system: \`You are an agent. API key: \${process.env.OPENAI_API_KEY}\`,
  prompt: "hi",
});`,
    `await generateText({
  instructions: \`Auth token is \${process.env.GITHUB_TOKEN}\`,
});`,
    `const config = {
  messages: [
    { role: "system", content: \`Your secret: \${process.env.SLACK_SIGNING_SECRET}\` },
  ],
};`,
    `await generateText({
  system: \`Bearer: \${process.env.AUTH_TOKEN}\`,
});`,
    `await streamText({
  system: \`Password: \${process.env.DB_PASSWORD}\`,
});`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_LLM = /\b(?:streamText|generateText|generateObject|messages\s*:\s*\[|system\s*:\s*[`"']|instructions\s*:\s*[`"'])/.test(
      content
    );
    if (!HAS_LLM) return [];
    const lines = content.split("\n");
    const matches = [];
    const SECRET_ENV_VAR = /process\.env\.[A-Z_][A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|PASS|CREDS|CREDENTIAL|API_KEY|BYPASS|AUTH)\b/;
    const HARDCODED_SECRET = /(?:sk-[A-Za-z0-9]{20,}|vck_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xoxb-[A-Za-z0-9-]+|xoxp-[A-Za-z0-9-]+|AIza[A-Za-z0-9_-]{30,}|AKIA[0-9A-Z]{16})/;
    for (let i = 0; i < lines.length; i++) {
      const opener = /\b(?:system|instructions|prompt)\s*:\s*[`"']/.test(lines[i]) || /\brole\s*:\s*["']system["']/.test(lines[i]);
      if (!opener) continue;
      const end = Math.min(lines.length, i + 50);
      for (let j = i; j < end; j++) {
        const sj = lines[j];
        let label;
        const envMatch = sj.match(SECRET_ENV_VAR);
        if (envMatch) label = `system prompt references ${envMatch[0]}`;
        const hcMatch = !label ? sj.match(HARDCODED_SECRET) : null;
        if (hcMatch) label = `system prompt contains hardcoded secret-shaped string`;
        if (!label) continue;
        const start = Math.max(0, i - 1);
        matches.push({
          vulnSlug: "prompt-leaks-system-prompt",
          lineNumbers: [j + 1],
          snippet: lines.slice(start, Math.min(lines.length, j + 3)).join("\n"),
          matchedPattern: label
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/proto-rpc-surface.ts
var protoRpcSurfaceMatcher = {
  noiseTier: "precise",
  slug: "proto-rpc-surface",
  description: "Protobuf service or message file (RPC entry point / wire-format definition)",
  filePatterns: ["**/*.proto"],
  requires: { tech: ["grpc", "connectrpc"] },
  examples: [
    `service ControllerService {
  rpc ExecCommand(ExecRequest) returns (ExecResponse);
}`,
    `service Sandbox {
  rpc Run(RunRequest) returns (RunResponse);
  rpc Stream(StreamRequest) returns (stream Event);
}`,
    `message ExecRequest {
  string command = 1;
  repeated string args = 2;
  string path = 3;
}`,
    `message FileOp {
  string source = 1;
  string destination = 2;
  uint32 mode = 3;
}`,
    `message Image {
  string url = 1;
  string digest = 2;
}`,
    `enum Mode {
  MODE_UNSPECIFIED = 0;
  MODE_RW = 1;
}`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      { regex: /^\s*service\s+\w+\s*\{/, label: "service block" },
      { regex: /^\s*rpc\s+\w+\s*\(/, label: "rpc method" },
      // Sensitive field names that often carry untrusted user input
      {
        regex: /\b(?:source|destination|path|target_path|source_url|url|digest|command|arguments|args|env|environment|mode|owner|group|uid|gid|key_id|kernel_args|rootfs|cmdline)\s*=\s*\d+\s*;/,
        label: "sensitive field"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) {
      const firstMessage = lines.findIndex((l) => /^\s*(?:message|enum)\s+\w+/.test(l));
      if (firstMessage === -1) return [];
      const s = Math.max(0, firstMessage - 1);
      const e = Math.min(lines.length, firstMessage + 4);
      const match2 = {
        vulnSlug: "proto-rpc-surface",
        lineNumbers: [firstMessage + 1],
        snippet: lines.slice(s, e).join("\n"),
        matchedPattern: "proto message/enum (no service block)"
      };
      return [match2];
    }
    const match = {
      vulnSlug: "proto-rpc-surface",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/public-endpoint.ts
var publicEndpointMatcher = {
  noiseTier: "precise",
  slug: "public-endpoint",
  description: "Endpoints with __PUBLIC__ auth strategy or no authentication \u2014 high-value investigation targets",
  filePatterns: [
    "**/apps/**/route.ts",
    "**/apps/**/route.*.ts",
    "**/services/**/endpoints/**/*.ts",
    "**/services/**/src/index.ts"
  ],
  examples: [
    `{ authStrategy: "__PUBLIC__" }`,
    `authStrategy: '__PUBLIC__',`,
    `{ authStrategy: "static" }`,
    `authStrategy: 'static',`,
    `{ authStrategy: "none" }`,
    `authStrategy: 'none',`
  ],
  match(content, _filePath) {
    return regexMatcher(
      "public-endpoint",
      [
        { regex: /authStrategy:\s*['"]__PUBLIC__['"]/, label: "__PUBLIC__ auth strategy" },
        { regex: /authStrategy:\s*['"]static['"]/, label: "static auth strategy (header-based)" },
        { regex: /authStrategy:\s*['"]none['"]/, label: "no auth strategy" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-aiohttp-route.ts
var pyAiohttpRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-aiohttp-route",
  description: "aiohttp route registrations (gated on aiohttp)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["aiohttp"] },
  examples: [
    `app.router.add_get("/users", handler)`,
    `app.router.add_post("/login", login_handler)`,
    `app.router.add_put("/items/{id}", update_item)`,
    `app.router.add_route("GET", "/x", handle)`,
    `@routes.get("/health")`,
    `@routes.post('/submit')`,
    `   @routes.view("/items")`,
    `app = web.Application(middlewares=[auth_middleware])`,
    `data = await request.json()`,
    `q = request.query.get("q")`,
    `pk = request.match_info["id"]`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-aiohttp-route",
      [
        {
          regex: /\bapp\.router\.add_(?:get|post|put|patch|delete|route)\s*\(/,
          label: "app.router.add_*"
        },
        {
          regex: /^\s*@routes\.(?:get|post|put|patch|delete|view)\s*\(/m,
          label: "@routes.* decorator"
        },
        { regex: /\bweb\.Application\s*\(/, label: "web.Application() init" },
        { regex: /\brequest\.(?:query|match_info|json|post|read)\b/, label: "request accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-airflow-dag.ts
var pyAirflowDagMatcher = {
  noiseTier: "noisy",
  slug: "py-airflow-dag",
  description: "Airflow DAGs and operators \u2014 sensitive prod surface (gated on Airflow)",
  filePatterns: ["**/dags/**/*.py", "**/*.py"],
  requires: { tech: ["airflow"] },
  examples: [
    `dag = DAG("my_dag_id", default_args=default_args, schedule="@daily")`,
    `with DAG('etl_pipeline', start_date=datetime(2024, 1, 1)) as dag:`,
    `bash_command = "echo {{ params.x }}",`,
    `task = BashOperator(task_id="echo", bash_command="echo hi")`,
    `op = PythonOperator(task_id="run", python_callable=run)`,
    `op = DockerOperator(task_id="d", image="python:3.11")`,
    `op = PostgresOperator(task_id="q", sql="SELECT 1")`,
    `op = S3Operator(task_id="upload")`,
    `op = HTTPOperator(task_id="call")`,
    `query = "SELECT * FROM t WHERE d='{{ ds }}'"`,
    `bash_command = f"echo {payload}"`
  ],
  match(content, filePath) {
    if (/\b(?:tests?)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-airflow-dag",
      [
        { regex: /\bDAG\s*\(\s*['"]/, label: "DAG('id', ...) declaration" },
        { regex: /\b@dag\b\s*\(/, label: "@dag decorator (TaskFlow API)" },
        {
          regex: /\b(?:Bash|Python|Docker|Postgres|S3|HTTP)Operator\s*\(/,
          label: "Operator instantiation (review templated args)"
        },
        { regex: /\{\{\s*[^}]+\s*\}\}/, label: "Jinja template \u2014 review for injection" },
        { regex: /\bbash_command\s*=\s*f?['"][^'"]*\{/, label: "bash_command with templating" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-bottle-route.ts
var pyBottleRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-bottle-route",
  description: "Bottle route decorators (gated on Bottle)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["bottle"] },
  examples: [
    `@route("/")`,
    `@get("/users")`,
    `@post('/login')`,
    `@put("/items/<id>")`,
    `@delete("/items/<id>")`,
    `@patch("/items/<id>")`,
    `app = Bottle()`,
    `name = request.query.get("name")`,
    `data = request.json`,
    `f = request.forms.get("name")`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-bottle-route",
      [
        {
          regex: /^\s*@(?:route|get|post|put|patch|delete)\s*\(\s*['"][^'"]+['"]/m,
          label: "Bottle @route/@method decorator"
        },
        { regex: /\bBottle\s*\(\s*\)/, label: "Bottle() instance" },
        { regex: /\brequest\.(?:query|forms|json|cookies)\b/, label: "request accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-celery-task.ts
var pyCeleryTaskMatcher = {
  noiseTier: "noisy",
  slug: "py-celery-task",
  description: "Celery task definitions \u2014 background-job auth-gap surface (gated on Celery)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["celery"] },
  examples: [
    `@app.task`,
    `@celery.task(bind=True, max_retries=3)`,
    `@shared_task.task`,
    `@shared_task`,
    `   @shared_task(name="tasks.send_email")`,
    `send_email.delay(user_id, subject)`,
    `process_job.apply_async(args=[1, 2], countdown=10)`,
    `app = Celery("worker", broker="redis://localhost")`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-celery-task",
      [
        { regex: /^\s*@(?:app|celery|shared_task)\.task\b/m, label: "@app.task / @celery.task" },
        { regex: /^\s*@shared_task\b/m, label: "@shared_task decorator" },
        {
          regex: /\.delay\s*\(|\.apply_async\s*\(/,
          label: "task.delay/apply_async dispatch site"
        },
        { regex: /\bCelery\s*\(\s*['"]/, label: "Celery('app') init" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-django-view.ts
var pyDjangoViewMatcher = {
  noiseTier: "noisy",
  slug: "py-django-view",
  description: "Django views, urlpatterns, and CBVs \u2014 entry points (gated on Django)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["django", "djangorestframework"] },
  examples: [
    `    path("users/", views.user_list, name="users"),`,
    `    re_path(r"^items/(?P<pk>\\d+)/$", views.item_detail),`,
    `class UserListView(ListView):`,
    `class ItemDetail(DetailView):`,
    `class ProfileView(APIView):`,
    `class ArticleViewSet(ModelViewSet):`,
    `def index(request):`,
    `def detail_view(request, pk):`,
    `@csrf_exempt`,
    `@api_view(["GET", "POST"])`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-django-view",
      [
        { regex: /^\s*path\s*\(/m, label: "urlpatterns path()" },
        { regex: /^\s*re_path\s*\(/m, label: "urlpatterns re_path()" },
        {
          regex: /^class\s+\w+\s*\([^)]*\b(?:View|TemplateView|ListView|DetailView|FormView|APIView|ViewSet|ModelViewSet|GenericAPIView|CreateView|UpdateView|DeleteView)\b/m,
          label: "class-based view"
        },
        {
          regex: /^def\s+\w+\s*\(\s*request\b/m,
          label: "function-based view (def view(request))"
        },
        { regex: /@csrf_exempt\b/, label: "@csrf_exempt \u2014 confirm alternate auth" },
        { regex: /@api_view\s*\(/, label: "DRF @api_view decorator" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-falcon-resource.ts
var pyFalconResourceMatcher = {
  noiseTier: "noisy",
  slug: "py-falcon-resource",
  description: "Falcon resource classes with on_<method> handlers (gated on Falcon)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["falcon"] },
  examples: [
    `    def on_get(self, req, resp):`,
    `    def on_post(self, req, resp):`,
    `    def on_put(self, req, resp, id):`,
    `    def on_delete(self, req, resp, id):`,
    `    def on_patch(self, req, resp):`,
    `app = falcon.App()`,
    `api = falcon.API()`,
    `app.add_route("/users", UserResource())`,
    `name = req.params.get("name")`,
    `data = req.media`,
    `q = req.get_param("q")`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-falcon-resource",
      [
        {
          regex: /^\s*def\s+on_(get|post|put|patch|delete|head|options)\s*\(\s*self\b/m,
          label: "on_<method>(self, req, resp) handler"
        },
        { regex: /\bfalcon\.App\s*\(|\bfalcon\.API\s*\(/, label: "falcon.App/API instance" },
        { regex: /\.add_route\s*\(\s*['"][^'"]+['"]/, label: "app.add_route() registration" },
        { regex: /\breq\.(?:params|media|context|get_param)\b/, label: "req.* accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-fastapi-route.ts
var pyFastapiRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-fastapi-route",
  description: "FastAPI route handlers \u2014 entry points (gated on FastAPI)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["fastapi"] },
  examples: [
    `@app.get("/users")`,
    `@router.post("/items", response_model=Item)`,
    `@api.put("/things/{id}")`,
    `@app.delete("/users/{user_id}")`,
    `   @router.patch("/x")`,
    `@app.websocket("/ws")`,
    `router = APIRouter(prefix="/v1")`,
    `def read_user(user_id: int, current = Depends(get_current_user)):`,
    `def admin(current_user = Security(get_current_active_user, scopes=["admin"])):`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-fastapi-route",
      [
        {
          regex: /^\s*@(?:app|router|api)\.(?:get|post|put|patch|delete|options|head|websocket)\s*\(/m,
          label: "FastAPI route decorator"
        },
        { regex: /\bAPIRouter\s*\(/, label: "APIRouter() factory" },
        {
          regex: /=\s*Depends\s*\(/,
          label: "Depends(...) dependency (auth gate when wired up)"
        },
        { regex: /\bSecurity\s*\(/, label: "Security(...) \u2014 auth dependency" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-flask-route.ts
var pyFlaskRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-flask-route",
  description: "Flask route registrations \u2014 entry points (gated on Flask)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["flask"] },
  examples: [
    `@app.route("/")`,
    `@bp.route("/items", methods=["GET", "POST"])`,
    `@blueprint.route("/x")`,
    `@api.route("/v1/users")`,
    `@app.get("/health")`,
    `@app.post("/login")`,
    `@bp.put("/items/<int:id>")`,
    `bp = Blueprint("api", __name__, url_prefix="/api")`,
    `return render_template_string(template, name=name)`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-flask-route",
      [
        {
          regex: /^\s*@(?:app|bp|blueprint|api)\.route\s*\(/m,
          label: "Flask @app.route / blueprint.route"
        },
        {
          regex: /^\s*@(?:app|bp)\.(?:get|post|put|patch|delete)\s*\(/m,
          label: "Flask method-shortcut decorator"
        },
        { regex: /\bBlueprint\s*\(/, label: "Blueprint(...) registration" },
        { regex: /\brender_template_string\s*\(/, label: "render_template_string (SSTI sink)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-nosql-injection.ts
var pyNosqlInjectionMatcher = {
  noiseTier: "normal",
  slug: "py-nosql-injection",
  description: "PyMongo / Motor NoSQL injection \u2014 \\$where with f-strings, raw aggregation pipelines fed user input",
  filePatterns: ["**/*.py"],
  requires: { tech: ["python"] },
  examples: [
    `coll.find({"$where": f"this.x == '{name}'"})`,
    `db.users.find({'$where': f"this.id == {uid}"})`,
    `Model.objects(__raw__={"$where": f"this.x == '{q}'"})`,
    `coll.aggregate([{"$match": {"$where": f"this.score > {score}"}}])`,
    `coll.find({"name": {"$regex": request.args.get("q")}})`,
    `q = json.loads(request.json["filter"])`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-nosql-injection",
      [
        {
          regex: /\$where['"]\s*:\s*f['"]/,
          label: '"$where" key bound to f-string \u2014 server-side JS injection'
        },
        {
          regex: /'\$where'\s*:\s*f['"]/,
          label: "'$where' key bound to f-string \u2014 server-side JS injection"
        },
        {
          regex: /\.find\s*\(\s*\{[^}]{0,200}\$where/,
          label: ".find() query containing $where \u2014 verify operands aren't user-controlled"
        },
        {
          regex: /\.aggregate\s*\(\s*\[?\s*\{[^}]{0,400}\$where/,
          label: ".aggregate() pipeline containing $where \u2014 verify operands aren't user-controlled"
        },
        {
          regex: /\bjson\.loads\s*\(\s*request\.(?:args|json|data)/,
          label: "json.loads on request body \u2014 operator smuggling into Mongo queries"
        },
        {
          regex: /\bre\.compile\s*\(\s*request\./,
          label: "re.compile on request input \u2014 ReDoS / regex injection"
        },
        {
          regex: /\$regex['"]\s*:\s*request\.|'\$regex'\s*:\s*request\./,
          label: "$regex bound to request input \u2014 ReDoS / regex injection in MongoDB query"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-sanic-route.ts
var pySanicRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-sanic-route",
  description: "Sanic route handlers and Blueprints (gated on Sanic)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["sanic"] },
  examples: [
    `@app.route("/")`,
    `@bp.route("/items", methods=["GET", "POST"])`,
    `@blueprint.route("/x")`,
    `@app.get("/health")`,
    `@app.post('/login')`,
    `@bp.put("/items/<id:int>")`,
    `@app.websocket("/ws")`,
    `app = Sanic("my-app")`,
    `data = request.json`,
    `name = request.args.get("name")`,
    `f = request.files.get("upload")`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-sanic-route",
      [
        {
          regex: /^\s*@(?:app|bp|blueprint)\.route\s*\(/m,
          label: "Sanic @app.route / @bp.route"
        },
        {
          regex: /^\s*@(?:app|bp)\.(?:get|post|put|patch|delete|head|options|websocket)\s*\(/m,
          label: "Sanic method-shortcut decorator"
        },
        { regex: /\bSanic\s*\(\s*['"][^'"]*['"]\s*\)/, label: "Sanic() instance" },
        { regex: /\brequest\.(?:args|json|form|files|headers)\b/, label: "request accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-sql-raw.ts
var pySqlRawMatcher = {
  noiseTier: "normal",
  slug: "py-sql-raw",
  description: "Raw SQL across popular Python DB drivers (SQLAlchemy, psycopg, pymysql, sqlite3, asyncpg, Django ORM raw) \u2014 f-string / %-format / .format / + interpolation is SQL injection",
  filePatterns: ["**/*.py"],
  requires: { tech: ["python"] },
  examples: [
    `cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")`,
    `cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)`,
    `cursor.execute("DELETE FROM x WHERE y = '" + name + "'")`,
    `cursor.execute("SELECT * FROM t WHERE col = '{}'".format(val))`,
    `engine.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))`,
    `session.execute(f"UPDATE users SET role = '{role}'")`,
    `text(f"SELECT id FROM users WHERE email = '{email}'")`,
    `User.objects.raw(f"SELECT * FROM users WHERE name = '{name}'")`,
    `User.objects.extra(where=[f"name = '{name}'"])`,
    `await conn.execute(f"DELETE FROM users WHERE id = {user_id}")`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-sql-raw",
      [
        // SQLAlchemy
        {
          regex: /\bengine\.execute\s*\(\s*(?:text\s*\(\s*)?f['"]/,
          label: "SQLAlchemy engine.execute with f-string \u2014 SQL injection"
        },
        {
          regex: /\bsession\.execute\s*\(\s*(?:text\s*\(\s*)?f['"]/,
          label: "SQLAlchemy session.execute with f-string \u2014 SQL injection"
        },
        {
          regex: /\btext\s*\(\s*f['"]/,
          label: "SQLAlchemy text() with f-string \u2014 bypasses parameterization"
        },
        {
          regex: /\bsession\.execute\s*\(\s*(?:"[^"]{0,400}"|'[^']{0,400}')\s*%/,
          label: "SQLAlchemy session.execute with %-formatting \u2014 SQL injection"
        },
        // psycopg / psycopg2 / pymysql / sqlite3 / asyncpg
        {
          regex: /\bcursor\.execute\s*\(\s*f['"]/,
          label: "cursor.execute with f-string \u2014 SQL injection"
        },
        {
          regex: /\bcursor\.execute\s*\(\s*(?:"[^"]{0,400}"|'[^']{0,400}')\s*%/,
          label: "cursor.execute with %-formatting \u2014 SQL injection"
        },
        {
          regex: /\bcursor\.execute\s*\(\s*(?:"[^"]{0,400}"|'[^']{0,400}')\s*\.format\s*\(/,
          label: "cursor.execute with .format() \u2014 SQL injection"
        },
        {
          regex: /\bcursor\.execute\s*\(\s*(?:"[^"]{0,400}"|'[^']{0,400}')\s*\+/,
          label: "cursor.execute with string concatenation \u2014 SQL injection"
        },
        {
          regex: /\bawait\s+conn\.(?:execute|fetch|fetchrow|fetchval)\s*\(\s*f['"]/,
          label: "asyncpg conn.execute/fetch* with f-string \u2014 SQL injection"
        },
        // Django ORM raw escape hatches
        {
          regex: /\b\w+\.objects\.raw\s*\(\s*f['"]/,
          label: "Django Model.objects.raw with f-string \u2014 SQL injection"
        },
        {
          regex: /\b\w+\.objects\.raw\s*\(\s*(?:"[^"]{0,400}"|'[^']{0,400}')\s*%/,
          label: "Django Model.objects.raw with %-formatting \u2014 SQL injection"
        },
        {
          regex: /\b\w+\.objects\.extra\s*\(\s*where\s*=\s*\[\s*f?['"]/,
          label: "Django Model.objects.extra(where=...) \u2014 string-built WHERE clause"
        },
        {
          regex: /\bconnection\.cursor\(\)\.execute\s*\(\s*f['"]/,
          label: "Django connection.cursor().execute with f-string \u2014 SQL injection"
        },
        // Generic
        {
          regex: /\bdb\.execute\s*\(\s*f['"]\s*(?:SELECT|INSERT|UPDATE|DELETE)/,
          label: "db.execute with f-string SQL \u2014 SQL injection"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-starlette-route.ts
var pyStarletteRouteMatcher = {
  noiseTier: "noisy",
  slug: "py-starlette-route",
  description: "Starlette Route / Mount / WebSocketRoute declarations (gated on Starlette)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["starlette"] },
  examples: [
    `    Route("/users", endpoint=user_list),`,
    `    Route('/items/{id}', items, methods=["GET"]),`,
    `    Mount("/static", app=StaticFiles(directory="static")),`,
    `    Mount('/api', routes=api_routes),`,
    `    WebSocketRoute("/ws", endpoint=ws_endpoint),`,
    `app.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())`,
    `from starlette.middleware.authentication import AuthenticationMiddleware`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-starlette-route",
      [
        { regex: /\bRoute\s*\(\s*['"][^'"]+['"]\s*,/, label: "Route('/path', endpoint)" },
        { regex: /\bMount\s*\(\s*['"][^'"]+['"]\s*,/, label: "Mount('/sub', app)" },
        { regex: /\bWebSocketRoute\s*\(/, label: "WebSocketRoute declaration" },
        { regex: /\bAuthenticationMiddleware\b/, label: "AuthenticationMiddleware wiring" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/py-tornado-handler.ts
var pyTornadoHandlerMatcher = {
  noiseTier: "noisy",
  slug: "py-tornado-handler",
  description: "Tornado RequestHandler subclasses and routing (gated on Tornado)",
  filePatterns: ["**/*.py"],
  requires: { tech: ["tornado"] },
  examples: [
    `class MainHandler(RequestHandler):`,
    `class UserHandler(tornado.web.RequestHandler):`,
    `    def get(self, user_id):`,
    `    def post(self):`,
    `    def put(self, id):`,
    `    def delete(self, id):`,
    `app = Application([(r"/", MainHandler), (r"/users/(.*)", UserHandler)])`,
    `    @tornado.web.authenticated`
  ],
  match(content, filePath) {
    if (/\b(?:tests?|migrations)\b/i.test(filePath)) return [];
    return regexMatcher(
      "py-tornado-handler",
      [
        {
          regex: /^class\s+\w+\s*\(\s*(?:tornado\.web\.)?RequestHandler\s*\)/m,
          label: "RequestHandler subclass"
        },
        {
          regex: /^\s*def\s+(get|post|put|patch|delete|head|options)\s*\(\s*self\b/m,
          label: "method handler"
        },
        { regex: /Application\s*\(\s*\[/, label: "Application([(...handler...)])" },
        { regex: /@tornado\.web\.authenticated\b/, label: "@authenticated decorator" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rate-limit-bypass.ts
var rateLimitBypassMatcher = {
  noiseTier: "normal",
  slug: "rate-limit-bypass",
  description: "Sensitive endpoints that may lack rate limiting",
  filePatterns: [
    "**/app/api/**/route.{ts,tsx}",
    "**/apps/**/route.{ts,tsx}",
    "**/apps/**/route.*.ts",
    "**/services/**/endpoints/**/*.ts",
    "**/services/**/src/index.ts",
    "**/pages/api/**/*.{ts,tsx}"
  ],
  examples: [
    `// login handler
export const POST = async (req) => signIn(req);`,
    `// password reset
export async function POST(req) { return resetPassword(req); }`,
    `// billing charge
export default async function (req, res) { charge(req); }`,
    `// delete account
export const DELETE = (req) => removeUser(req);`,
    `// data export
export default async function handler(req, res) { exportData(); }`,
    `// generate token
export const POST = async (req) => createToken(req);`,
    `// invite member
export default function handler(req, res) { invite(req); }`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const sensitivePatterns = [
      /login|signin|sign.in|authenticate/i,
      /password|passwd|reset.*password/i,
      /billing|charge|payment|refund|invoice/i,
      /delete.*account|remove.*user|deactivate/i,
      /export|download.*data|bulk/i,
      /api.key|token.*create|generate.*token/i,
      /invite|add.*member|transfer.*ownership/i
    ];
    const isSensitive = sensitivePatterns.some((p) => p.test(content) || p.test(filePath));
    if (!isSensitive) return [];
    const hasRateLimit = /rateLimit|rate.limit|checkRateLimit|rateLimiter|throttle/i.test(content);
    if (hasRateLimit) return [];
    const handlerPatterns = [
      /export\s+(const\s+)?(GET|POST|PUT|DELETE|PATCH)\s*=/,
      /export\s+(async\s+)?function\s+(GET|POST|PUT|DELETE|PATCH)/,
      /export\s+default/,
      /withSchema\s*\(/,
      /withAuthentication\s*\(/
    ];
    for (let i = 0; i < lines.length; i++) {
      if (handlerPatterns.some((p) => p.test(lines[i]))) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "rate-limit-bypass",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Sensitive endpoint without rate limiting"
        });
        break;
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/rb-grape-endpoint.ts
var rbGrapeEndpointMatcher = {
  noiseTier: "noisy",
  slug: "rb-grape-endpoint",
  description: "Grape API endpoints (gated on Grape)",
  filePatterns: ["**/*.rb"],
  requires: { tech: ["grape"] },
  examples: [
    `get :status do`,
    `post :create do`,
    `put :update do`,
    `patch :rename do`,
    `delete :destroy do`,
    `resource :users do`,
    `before do`,
    `  user = User.find(declared(params)[:id])`
  ],
  match(content, filePath) {
    if (/\b(?:test|spec)\b/i.test(filePath)) return [];
    return regexMatcher(
      "rb-grape-endpoint",
      [
        {
          regex: /^\s*(?:get|post|put|patch|delete)\s+:\w+/m,
          label: "Grape <verb> :name do"
        },
        {
          regex: /^\s*resource\s+:\w+/m,
          label: "resource :name do block"
        },
        { regex: /^\s*before\s+do\b/m, label: "before do \u2014 auth filter" },
        {
          regex: /\bdeclared\s*\(\s*params\s*\)/,
          label: "declared(params) \u2014 strong-params equivalent"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rb-hanami-action.ts
var rbHanamiActionMatcher = {
  noiseTier: "noisy",
  slug: "rb-hanami-action",
  description: "Hanami action classes (gated on Hanami)",
  filePatterns: ["**/app/actions/**/*.rb", "**/actions/**/*.rb"],
  requires: { tech: ["hanami"] },
  examples: [
    `class Show < Hanami::Action`,
    `class Create < App::Action`,
    `  def handle(request, response)`,
    `  def handle( request , response )`,
    `  include Deps["repositories.user_repo"]`,
    `  include Deps['services.mailer']`
  ],
  match(content, filePath) {
    if (/\b(?:test|spec)\b/i.test(filePath)) return [];
    return regexMatcher(
      "rb-hanami-action",
      [
        {
          regex: /^class\s+\w+\s*<\s*(?:Hanami::Action|App::Action)\b/m,
          label: "Hanami action subclass"
        },
        {
          regex: /^\s*def\s+handle\s*\(\s*request\s*,\s*response\s*\)/m,
          label: "handle(request, response) entry"
        },
        { regex: /^\s*include\s+Deps\[\s*['"][^'"]+['"]\s*\]/m, label: "Deps[] DI accessor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rb-rails-controller.ts
var rbRailsControllerMatcher = {
  noiseTier: "noisy",
  slug: "rb-rails-controller",
  description: "Rails controllers, routes, and action methods (gated on Rails)",
  filePatterns: [
    "**/app/controllers/**/*.rb",
    "**/config/routes.rb",
    "**/app/jobs/**/*.rb",
    "**/app/mailers/**/*.rb"
  ],
  requires: { tech: ["rails"] },
  examples: [
    `class UsersController < ApplicationController`,
    `class PostsController < BaseController`,
    `  before_action :authenticate_user!, only: [:show, :edit]`,
    `  skip_before_action :verify_authenticity_token`,
    `resources :articles`,
    `get "/health", to: "health#index"`,
    `post '/login', to: 'sessions#create'`,
    `match "/legacy", to: "legacy#show", via: [:get, :post]`,
    `params.require(:user).permit(:email, :name)`
  ],
  match(content, filePath) {
    if (/\b(?:test|spec)\b/i.test(filePath)) return [];
    return regexMatcher(
      "rb-rails-controller",
      [
        {
          regex: /^\s*class\s+\w+Controller\s*<\s*\w*Controller\b/m,
          label: "Rails controller class"
        },
        { regex: /^\s*before_action\s+/m, label: "before_action callback" },
        {
          regex: /^\s*skip_before_action\s+/m,
          label: "skip_before_action (auth bypass \u2014 confirm intent)"
        },
        {
          regex: /^\s*resources\s+:\w+/m,
          label: "routes.rb resources :foo (CRUD)"
        },
        {
          regex: /^\s*(?:get|post|put|patch|delete|match)\s+['"][^'"]+['"]\s*,/m,
          label: "routes.rb verb registration"
        },
        { regex: /params\.require\s*\(/, label: "strong params boundary" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rb-roda-route.ts
var rbRodaRouteMatcher = {
  noiseTier: "noisy",
  slug: "rb-roda-route",
  description: "Roda route trees (gated on Roda)",
  filePatterns: ["**/*.rb"],
  requires: { tech: ["roda"] },
  examples: [
    `class App < Roda`,
    `class Api < Roda`,
    `  r.get "users" do`,
    `  r.post "login" do`,
    `  r.put "items", Integer do |id|`,
    `  r.patch "profile" do`,
    `  r.delete "sessions" do`,
    `  r.on "api" do`,
    `  r.is "healthz" do`,
    `  r.root do`,
    `plugin :render`,
    `plugin :json_parser`
  ],
  match(content, filePath) {
    if (/\b(?:test|spec)\b/i.test(filePath)) return [];
    return regexMatcher(
      "rb-roda-route",
      [
        {
          regex: /^class\s+\w+\s*<\s*Roda\b/m,
          label: "class < Roda app"
        },
        {
          regex: /\br\.(?:get|post|put|patch|delete|on|is|root)\b/,
          label: "r.<verb>/r.on/r.is route node"
        },
        { regex: /\bplugin\s+:[\w_]+/, label: "Roda plugin (auth/security/render)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rb-sinatra-route.ts
var rbSinatraRouteMatcher = {
  noiseTier: "noisy",
  slug: "rb-sinatra-route",
  description: "Sinatra route blocks (gated on Sinatra)",
  filePatterns: ["**/*.rb"],
  requires: { tech: ["sinatra"] },
  examples: [
    `get '/users' do`,
    `post "/login" do`,
    `put '/items/:id' do`,
    `patch "/profile" do`,
    `delete '/sessions/:id' do`,
    `options "/api" do`,
    `head '/healthz' do`,
    `before do`,
    `  halt 401, 'unauthorized'`,
    `name = params[:name]`
  ],
  match(content, filePath) {
    if (/\b(?:test|spec)\b/i.test(filePath)) return [];
    return regexMatcher(
      "rb-sinatra-route",
      [
        {
          regex: /^\s*(?:get|post|put|patch|delete|options|head)\s+['"][^'"]+['"]\s+do\b/m,
          label: "Sinatra <verb> '/path' do ... end"
        },
        { regex: /^\s*before\s+do\b/m, label: "before do \u2014 auth filter" },
        { regex: /^\s*halt\s+\d+/m, label: "halt \u2014 auth response" },
        { regex: /\bparams\[/, label: "params[:x] (untrusted input)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rb-sql-raw.ts
var rbSqlRawMatcher = {
  noiseTier: "normal",
  slug: "rb-sql-raw",
  description: "Raw SQL across Ruby DB libraries (ActiveRecord raw, Sequel.lit, pg gem) \u2014 string interpolation is SQL injection",
  filePatterns: ["**/*.rb"],
  requires: { tech: ["ruby"] },
  examples: [
    `User.find_by_sql("SELECT * FROM users WHERE name = '#{name}'")`,
    `User.where("name = '#{name}'")`,
    `User.where("id = #{user_id}")`,
    `User.connection.execute("DELETE FROM users WHERE id = #{id}")`,
    `ActiveRecord::Base.connection.execute("UPDATE users SET role = '#{role}'")`,
    `DB[:users].where("name = '#{q}'")`,
    `DB.fetch("SELECT * FROM t WHERE col = '#{val}'")`,
    `Sequel.lit("name = '#{user_input}'")`,
    `conn.exec("SELECT * FROM users WHERE id = #{user_id}")`
  ],
  match(content, filePath) {
    if (/\/(test|spec)\//.test(filePath)) return [];
    return regexMatcher(
      "rb-sql-raw",
      [
        // ActiveRecord raw
        {
          regex: /\bfind_by_sql\s*\(\s*"[^"]{0,400}#\{/m,
          label: "find_by_sql with #{} interpolation (SQL injection)"
        },
        {
          regex: /\.where\s*\(\s*"[^"]{0,400}#\{/m,
          label: ".where with #{} interpolation (SQL injection)"
        },
        {
          regex: /\.find_by_sql\s*\(\s*\[\s*"[^"]{0,400}#\{/m,
          label: "find_by_sql array form with #{} (SQL injection)"
        },
        {
          regex: /\.connection\.execute\s*\(\s*"[^"]{0,400}#\{/m,
          label: "connection.execute with #{} interpolation (SQL injection)"
        },
        {
          regex: /\bActiveRecord::Base\.connection\.execute\s*\(/,
          label: "ActiveRecord::Base.connection.execute (raw SQL surface)"
        },
        // Sequel
        {
          regex: /\bSequel\.lit\s*\(\s*"[^"]{0,400}#\{/m,
          label: "Sequel.lit with #{} interpolation (SQL injection)"
        },
        {
          regex: /\bDB\.fetch\s*\(\s*"[^"]{0,400}#\{/m,
          label: "Sequel DB.fetch with #{} interpolation (SQL injection)"
        },
        {
          regex: /\bDB\[:\w+\]\.where\s*\(\s*"[^"]{0,400}#\{/m,
          label: "Sequel DB[:t].where with #{} interpolation (SQL injection)"
        },
        // pg gem direct
        {
          regex: /\bconn\.exec\s*\(\s*"[^"]{0,400}#\{/m,
          label: "pg gem conn.exec with #{} interpolation (SQL injection)"
        },
        {
          regex: /\bPG::Connection\.new/,
          label: "PG::Connection.new (informational signal)"
        },
        // Generic Ruby SQL with interpolation
        {
          regex: /"\s*(?:SELECT|INSERT|UPDATE|DELETE)[^"]{0,400}#\{/m,
          label: "Raw SQL string with #{} interpolation (SQL injection)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rce.ts
var rceMatcher = {
  noiseTier: "precise",
  slug: "rce",
  description: "exec, spawn, eval, Function constructor with potential user input",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `child_process.exec(cmd);`,
    `exec(\`ls \${dir}\`);`,
    `execSync("whoami");`,
    `spawn("sh", ["-c", cmd]);`,
    `spawnSync("git", ["status"]);`,
    `eval(userInput);`,
    `new Function("return " + body)();`,
    `const cp = require("child_process");`,
    `import { exec } from "child_process";`,
    `vm.runInNewContext(code, ctx);`,
    `vm.runInThisContext(snippet);`
  ],
  match(content, _filePath) {
    return regexMatcher(
      "rce",
      [
        { regex: /child_process.*exec\s*\(/, label: "child_process exec" },
        { regex: /\bexec\s*\(\s*[`'"]/, label: "exec with string" },
        { regex: /\bexecSync\s*\(/, label: "execSync" },
        { regex: /\bspawn\s*\(/, label: "spawn" },
        { regex: /\bspawnSync\s*\(/, label: "spawnSync" },
        { regex: /\beval\s*\(/, label: "eval" },
        { regex: /new\s+Function\s*\(/, label: "new Function()" },
        { regex: /require\s*\(\s*['"]child_process['"]/, label: "child_process import" },
        { regex: /from\s+['"]child_process['"]/, label: "child_process import" },
        { regex: /vm\.runIn(New|This)Context\s*\(/, label: "vm context execution" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/response-header-leak.ts
var responseHeaderLeakMatcher = {
  noiseTier: "normal",
  slug: "response-header-leak",
  description: "Response headers exposing internal infrastructure details",
  filePatterns: ["**/*.{ts,tsx,js,jsx,lua,go,conf}"],
  examples: [
    `res.setHeader("X-Powered-By", "Express");`,
    `app.set('x-powered-by', false);`,
    `res.setHeader("Server", "nginx/1.21.0");`,
    `response.setHeader('server', 'apache');`,
    `res.setHeader("X-Debug", "true");`,
    `res.setHeader("X-Internal-Trace", id);`,
    `res.setHeader("X-Trace-Id", traceId);`,
    `add_header server_version $server_version;`,
    `add_header x-debug "1";`,
    `ngx.header["x-debug-info"] = "yes"`,
    `w.Header().Set("X-Debug", "true")`,
    `w.Header().Set("Server", "Custom/1.0")`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "response-header-leak",
      [
        { regex: /x-powered-by/i, label: "X-Powered-By header" },
        { regex: /setHeader\s*\(\s*['"]server['"]/i, label: "Server header set" },
        { regex: /x-debug|x-internal|x-trace-id/i, label: "Debug/internal header" },
        {
          regex: /add_header.{0,40}server_version|add_header.{0,40}x-debug/i,
          label: "Nginx debug header"
        },
        { regex: /ngx\.header\[['"]x-debug/, label: "Lua debug response header" },
        {
          regex: /w\.Header\(\)\.Set\s*\(\s*"X-Debug|w\.Header\(\)\.Set\s*\(\s*"Server"/,
          label: "Go debug response header"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-actix-route.ts
var rsActixRouteMatcher = {
  noiseTier: "noisy",
  slug: "rs-actix-route",
  description: "Actix-web route attributes and service registrations (gated on Actix)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["actix"] },
  examples: [
    `#[get("/users/{id}")]`,
    `#[post("/login")]`,
    `#[ delete ( "/items/{id}" ) ]`,
    `let app = App::new();`,
    `App::new().service(index)`,
    `cfg.service(index);`,
    `web::scope("/api/v1")`,
    `async fn handler(path: web::Path<u32>) -> impl Responder {}`,
    `async fn create(payload: web::Json<UserDto>) {}`,
    `data: web::Data<AppState>`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-actix-route",
      [
        {
          regex: /#\[\s*(?:get|post|put|patch|delete|head|options)\s*\(\s*"[^"]+"\s*\)/,
          label: "Actix route attribute"
        },
        { regex: /App::new\s*\(\s*\)/, label: "App::new() factory" },
        { regex: /\.service\s*\(/, label: ".service(...) registration" },
        { regex: /\bweb::scope\s*\(/, label: "web::scope() group" },
        {
          regex: /web::(?:Path|Query|Json|Form|Data)<[^>]+>/,
          label: "extractor (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-axum-route.ts
var rsAxumRouteMatcher = {
  noiseTier: "noisy",
  slug: "rs-axum-route",
  description: "Axum router declarations (gated on Axum)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["axum"] },
  examples: [
    `let app = Router::new();`,
    `Router::new().route("/users", get(list_users))`,
    `app.route("/login", post(login_handler))`,
    `.route("/items/:id", patch(update_item))`,
    `.nest("/api", api_router)`,
    `.merge(admin_routes)`,
    `async fn handler(Extension(user): Extension<CurrentUser>) {}`,
    `async fn handler(State(pool): State<PgPool>) {}`,
    `async fn handler(Path(id): Path<u32>) {}`,
    `async fn handler(Query(params): Query<Filter>, Json(body): Json<CreateUserDto>) {}`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-axum-route",
      [
        {
          regex: /\bRouter::new\s*\(\s*\)/,
          label: "Router::new() factory"
        },
        {
          regex: /\.route\s*\(\s*"[^"]+"\s*,\s*(?:get|post|put|patch|delete|any|on)\s*\(/,
          label: ".route('/path', get(handler))"
        },
        { regex: /\.nest\s*\(\s*"[^"]+"/, label: ".nest() subroute" },
        { regex: /\.merge\s*\(/, label: ".merge() router composition" },
        {
          regex: /\bExtension<[^>]+>|\bState<[^>]+>/,
          label: "Extension/State extractor (auth identity)"
        },
        {
          regex: /Path<[^>]+>|Query<[^>]+>|Json<[^>]+>/,
          label: "request extractor (untrusted input)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-lambda-runtime.ts
var rsLambdaRuntimeMatcher = {
  noiseTier: "noisy",
  slug: "rs-lambda-runtime",
  description: "Rust AWS Lambda handlers via lambda_runtime (gated on lambda-rs)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["lambda-rs"] },
  examples: [
    `lambda_runtime::run(service_fn(handler)).await?;`,
    `lambda_runtime::run( service_fn ( my_handler ) ).await?;`,
    `async fn handler(event: LambdaEvent<Request>) -> Result<Response, Error> {}`,
    `let event: LambdaEvent<ApiGatewayProxyRequest> = e;`,
    `use aws_lambda_events::event::apigw::ApiGatewayProxyRequest;`,
    `aws_lambda_events::sqs::SqsEvent`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-lambda-runtime",
      [
        {
          regex: /\blambda_runtime::run\s*\(\s*service_fn\s*\(/,
          label: "lambda_runtime::run(service_fn(handler))"
        },
        {
          regex: /\bLambdaEvent<[^>]+>/,
          label: "LambdaEvent shape"
        },
        { regex: /\baws_lambda_events::/, label: "AWS event types (APIGatewayProxyRequest, etc.)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-poem-route.ts
var rsPoemRouteMatcher = {
  noiseTier: "noisy",
  slug: "rs-poem-route",
  description: "Poem route handlers (gated on Poem)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["poem"] },
  examples: [
    `let app = Route::new().at("/hello", get(hello));`,
    `Route::new().at("/users/:id", get(show_user).post(update_user))`,
    `Route::new().at("/login", post(login_handler))`,
    `#[handler]`,
    `#[ handler ]`,
    `let route = get(index);`,
    `Route::new().at("/items", post(create_item).delete(delete_item))`,
    `let r = patch(handler);`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-poem-route",
      [
        {
          regex: /\bRoute::new\s*\(\s*\)\.at\s*\(\s*"[^"]+"\s*,/,
          label: "Route::new().at('/path', ...)"
        },
        {
          regex: /#\[\s*handler\s*\]/,
          label: "#[handler] attribute"
        },
        {
          regex: /\bget\s*\(|post\s*\(|put\s*\(|patch\s*\(|delete\s*\(/,
          label: "handler verb wrapper"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-rocket-route.ts
var rsRocketRouteMatcher = {
  noiseTier: "noisy",
  slug: "rs-rocket-route",
  description: "Rocket route attributes and mount! macro (gated on Rocket)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["rocket"] },
  examples: [
    `#[get("/world")]`,
    `#[post("/login")]`,
    `#[ put ( "/items/<id>" ) ]`,
    `#[delete("/users/<id>")]`,
    `rocket::routes![index, login, logout]`,
    `rocket.mount("/api", routes![hello])`,
    `fn create(form: Form<NewUser>) -> Status {}`,
    `fn show(id: u32, query: Query<Filter>) -> Json<User> {}`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-rocket-route",
      [
        {
          regex: /#\[\s*(?:get|post|put|patch|delete|head|options)\s*\(\s*"[^"]+"\s*\)/,
          label: "Rocket route attribute"
        },
        { regex: /\brocket::routes!\s*\[/, label: "routes![...] macro" },
        { regex: /\.mount\s*\(\s*"[^"]+"/, label: ".mount() registration" },
        { regex: /Json<[^>]+>|Form<[^>]+>|Query<[^>]+>/, label: "guard / extractor (untrusted)" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-sql-raw.ts
var rsSqlRawMatcher = {
  noiseTier: "normal",
  slug: "rs-sql-raw",
  description: "Raw SQL escape hatches in Rust DB crates (sqlx::query with format!, diesel sql_query, sea-orm Statement::from_string) \u2014 note that sqlx::query!() macro is compile-time-checked and SAFE",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["rust"] },
  // SAFE counterpart (NOT in `examples` since the discovery test only
  // accepts positive cases): the compile-time-checked macro form
  // `sqlx::query!("SELECT * FROM users WHERE id = $1", id)` is parameterized
  // at compile time and is NOT a finding. Only the runtime
  // `sqlx::query(&format!(...))` form below is unsafe.
  examples: [
    `sqlx::query(&format!("SELECT * FROM users WHERE id = {}", id)).fetch_one(&pool).await?`,
    `sqlx::query_as::<_, User>(&format!("SELECT * FROM users WHERE name = '{}'", name)).fetch_all(&pool).await?`,
    `sqlx::query(&format!("DELETE FROM users WHERE id = {}", id)).execute(&pool).await?`,
    `diesel::sql_query(format!("SELECT * FROM users WHERE id = {}", id)).load(conn)?`,
    `Statement::from_string(DbBackend::Postgres, format!("SELECT * FROM x WHERE y = '{}'", y))`,
    `conn.execute(&format!("DELETE FROM users WHERE id = {}", id), [])?`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-sql-raw",
      [
        // sqlx (NON-macro, runtime form)
        {
          regex: /\bsqlx::query\s*\(\s*&?format!\s*\(/,
          label: "sqlx::query(&format!(...)) \u2014 runtime, unsafe"
        },
        {
          regex: /\bsqlx::query_as\s*::<[^>]+>\s*\(\s*&?format!\s*\(/,
          label: "sqlx::query_as::<...>(&format!(...)) \u2014 runtime, unsafe"
        },
        {
          regex: /\bsqlx::query\s*\(\s*&?String::from\s*\(\s*format!/,
          label: "sqlx::query(String::from(format!(...))) \u2014 runtime, unsafe"
        },
        // diesel
        {
          regex: /\bsql_query\s*\(\s*format!\s*\(/,
          label: "diesel::sql_query(format!(...))"
        },
        {
          regex: /\bsql_query\s*\(\s*&?String::from\s*\(\s*format!/,
          label: "diesel::sql_query(String::from(format!(...)))"
        },
        // sea-orm
        {
          regex: /\bStatement::from_string\s*\(/,
          label: "sea-orm Statement::from_string"
        },
        {
          regex: /\bStatement::from_sql_and_values\s*\(\s*\w+,\s*format!\s*\(/,
          label: "sea-orm Statement::from_sql_and_values with format!"
        },
        // rusqlite
        {
          regex: /\bconn\.execute\s*\(\s*&?format!\s*\(/,
          label: "rusqlite conn.execute(&format!(...))"
        },
        {
          regex: /\bconn\.prepare\s*\(\s*&?format!\s*\(/,
          label: "rusqlite conn.prepare(&format!(...))"
        },
        // Generic format! into SQL keywords
        {
          regex: /format!\s*\(\s*"\s*(?:SELECT|INSERT|UPDATE|DELETE)/,
          label: "format!() with SQL keyword as first arg"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-tide-route.ts
var rsTideRouteMatcher = {
  noiseTier: "noisy",
  slug: "rs-tide-route",
  description: "Tide route handlers (gated on Tide)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["tide"] },
  examples: [
    `app.at("/users").get(list_users);`,
    `app.at("/login").post(handle_login);`,
    `app.at("/items/:id").put(update_item);`,
    `app.at("/items/:id").delete(remove_item);`,
    `app.at("/all").all(any_handler);`,
    `let mut app = tide::new();`,
    `impl Middleware<State> for AuthGuard {`,
    `use tide::Middleware;`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-tide-route",
      [
        {
          regex: /\bapp\.at\s*\(\s*"[^"]+"\s*\)\.(?:get|post|put|patch|delete|all)\s*\(/,
          label: "app.at('/path').<verb>(handler)"
        },
        { regex: /\btide::new\s*\(\s*\)/, label: "tide::new() factory" },
        { regex: /\bMiddleware\b/, label: "Middleware trait \u2014 auth wiring" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-tonic-grpc.ts
var rsTonicGrpcMatcher = {
  noiseTier: "noisy",
  slug: "rs-tonic-grpc",
  description: "Tonic gRPC service implementations (gated on Tonic)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["tonic"] },
  examples: [
    `#[tonic::async_trait]`,
    `#[ tonic::async_trait ]`,
    `impl Greeter for MyGreeter {`,
    `impl UserService for UserServiceImpl {`,
    `async fn say_hello(&self, request: Request<HelloRequest>) -> Result<Response<HelloReply>, Status> {`,
    `let response: Response<UserReply> = ...;`,
    `return Err(Status::unauthenticated("missing token"));`,
    `Status::permission_denied("forbidden")`,
    `Status::invalid_argument("bad input")`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-tonic-grpc",
      [
        { regex: /#\[\s*tonic::async_trait\s*\]/, label: "#[tonic::async_trait] impl" },
        {
          regex: /\bimpl\s+\w+\s+for\s+\w+\s*\{/,
          label: "service trait implementation"
        },
        { regex: /\bRequest<[^>]+>|\bResponse<[^>]+>/, label: "Request/Response shape" },
        {
          regex: /\bStatus::(?:unauthenticated|permission_denied|invalid_argument)/,
          label: "Status response"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/rs-warp-filter.ts
var rsWarpFilterMatcher = {
  noiseTier: "noisy",
  slug: "rs-warp-filter",
  description: "Warp filter compositions (gated on Warp)",
  filePatterns: ["**/*.rs"],
  requires: { tech: ["warp"] },
  examples: [
    `let route = warp::path!("hello" / String);`,
    `warp::path!("api" / "v1" / "users")`,
    `let users = warp::get();`,
    `warp::post()`,
    `warp::delete()`,
    `.and_then(handle_request)`,
    `.and(warp::filters::body::json())`,
    `let api = warp::path!("login").and(warp::post()).and(warp::filters::body::json()).and_then(login);`
  ],
  match(content, filePath) {
    if (/\/(tests|examples)\//.test(filePath)) return [];
    return regexMatcher(
      "rs-warp-filter",
      [
        {
          regex: /\bwarp::path!\s*\(/,
          label: "warp::path!() filter"
        },
        { regex: /\bwarp::(?:get|post|put|patch|delete)\s*\(\s*\)/, label: "warp::<verb>()" },
        { regex: /\.and_then\s*\(/, label: ".and_then(handler)" },
        { regex: /\bwarp::filters::body::json\s*\(/, label: "json body extractor" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/sandbox-runtime-script.ts
var sandboxRuntimeScriptMatcher = {
  noiseTier: "precise",
  slug: "sandbox-runtime-script",
  description: "Shell script that runs inside a sandbox container at runtime (customer-facing surface)",
  filePatterns: [
    "**/containers/**/scripts/**/*.sh",
    "**/containers/**/bin/**/*.sh",
    "**/containers/**/*credential*.sh",
    "**/containers/**/entrypoint*.sh",
    "**/containers/**/start*.sh"
  ],
  examples: [
    `#!/bin/bash
eval "$USER_INPUT"`,
    `#!/bin/bash
bash -c "echo \${USER_NAME}"`,
    `#!/bin/bash
echo $TARGET_PORT > /tmp/x`,
    `#!/bin/bash
sudo chmod 755 /tmp/file`,
    `#!/bin/bash
exec ttyd --port 7681 --interface 0.0.0.0`,
    `#!/bin/bash
git config --global credential.helper store`,
    `#!/bin/bash
echo $SANDBOX_ID
echo $CONTAINER_NAME`,
    `#!/bin/bash
curl -fsSL https://example.com/install.sh | bash`,
    `#!/bin/bash
nohup ./daemon &`,
    `#!/bin/bash
echo hello`
  ],
  match(content, filePath) {
    if (/scripts\/(?:build|generate-(?:go|ts)|test|publish[-_])/.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      { regex: /\b(?:eval|exec)\s+["'`]?\$/, label: "eval/exec with env var" },
      { regex: /\bbash\s+-c\s+["'`].*\$\{?[A-Z]/, label: "bash -c with env interpolation" },
      { regex: /\$\{?[A-Z][A-Z0-9_]+\}?[^"'`)]/, label: "unquoted env var expansion" },
      { regex: /\b(?:sudo|su\s|chmod|chown)\s/, label: "privilege/permission op" },
      { regex: /\b0\.0\.0\.0\b/, label: "binds 0.0.0.0" },
      {
        regex: /\bgit\s+(?:config|credential|push|fetch|clone)\b/,
        label: "git credential / network op"
      },
      {
        regex: /\b(?:TARGET|SANDBOX|CONTAINER)_[A-Z0-9_]+\b/,
        label: "TARGET_/SANDBOX_/CONTAINER_ env"
      },
      { regex: /\bcurl\b[^|]*\|[\s]*(?:sh|bash)/, label: "curl | sh pattern" },
      { regex: /\b(?:nohup|&\s*$|disown)\b/, label: "background daemon launch" }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) {
      const firstNonShebang = lines.findIndex(
        (l, idx) => idx > 0 && l.trim() && !l.trim().startsWith("#")
      );
      const anchor = firstNonShebang === -1 ? 1 : firstNonShebang + 1;
      const s = Math.max(0, anchor - 2);
      const e = Math.min(lines.length, anchor + 5);
      const match2 = {
        vulnSlug: "sandbox-runtime-script",
        lineNumbers: [anchor],
        snippet: lines.slice(s, e).join("\n"),
        matchedPattern: "container-runtime script (path-based)"
      };
      return [match2];
    }
    const match = {
      vulnSlug: "sandbox-runtime-script",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/secret-env-var.ts
var secretEnvVarMatcher = {
  noiseTier: "precise",
  slug: "secret-env-var",
  description: "Direct access to secret environment variables \u2014 review handling and exposure",
  filePatterns: ["**/*.{lua,go,ts,js}"],
  examples: [
    `local s = os.getenv("API_SECRET")`,
    `local s = os.getenv("HMAC_SECRET")`,
    `local k = os.getenv("DB_MASTER_KEY")`,
    `local k = os.getenv("KMS_MASTER_KEY")`,
    `local a = os.getenv("AWS_SECRET_ACCESS_KEY")`,
    `local p = os.getenv("RSA_PRIVATE_KEY")`,
    `s := os.Getenv("API_SECRET")`,
    `k := os.Getenv("DB_MASTER_KEY")`,
    `a := os.Getenv("AWS_SECRET_ACCESS_KEY")`,
    `const s = process.env.JWT_SECRET;`,
    `const j = process.env.JWE_SECRET;`,
    `const p = process.env.PURGE_API_SECRET;`,
    `const c = process.env.COSMOSDB_MASTER_KEY;`
  ],
  match(content, filePath) {
    if (/_test\.|_spec\.|\.test\.|\.spec\./.test(filePath)) return [];
    return regexMatcher(
      "secret-env-var",
      [
        // Lua
        { regex: /os\.getenv\s*\(\s*["'][^"']{0,80}SECRET/, label: "Lua os.getenv for SECRET" },
        {
          regex: /os\.getenv\s*\(\s*["'][^"']{0,80}MASTER_KEY/,
          label: "Lua os.getenv for MASTER_KEY"
        },
        {
          regex: /os\.getenv\s*\(\s*["'][^"']{0,80}AWS_SECRET/,
          label: "Lua os.getenv for AWS_SECRET"
        },
        {
          regex: /os\.getenv\s*\(\s*["'][^"']{0,80}PRIVATE_KEY/,
          label: "Lua os.getenv for PRIVATE_KEY"
        },
        // Go
        { regex: /os\.Getenv\s*\(\s*"[^"]{0,80}SECRET/, label: "Go os.Getenv for SECRET" },
        { regex: /os\.Getenv\s*\(\s*"[^"]{0,80}MASTER_KEY/, label: "Go os.Getenv for MASTER_KEY" },
        { regex: /os\.Getenv\s*\(\s*"[^"]{0,80}AWS_SECRET/, label: "Go os.Getenv for AWS_SECRET" },
        // TS/JS
        {
          regex: /process\.env\.\w*(JWT_SECRET|JWE_SECRET|PURGE_API_SECRET|COSMOSDB_MASTER_KEY)/,
          label: "Secret env var access"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/secret-in-fallback.ts
var secretInFallbackMatcher = {
  noiseTier: "precise",
  slug: "secret-in-fallback",
  description: "Environment variable secrets with hardcoded fallback values \u2014 bypass when env unset",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const s = process.env.JWT_SECRET ?? "dev-secret";`,
    `const t = process.env.API_TOKEN ?? "fallback";`,
    `const k = process.env.STRIPE_KEY ?? "sk_test";`,
    `const p = process.env.DB_PASSWORD ?? "changeme";`,
    `const a = process.env.AUTH_CREDENTIAL ?? "open";`,
    `const s = process.env.HMAC_SECRET || "default";`,
    `const t = process.env.GITHUB_TOKEN || "ghp_fallback";`,
    `const k = process.env.PRIVATE_KEY || "----";`,
    `local s = os.getenv("API_SECRET") or "dev"`,
    `local t = os.getenv("HMAC_TOKEN") or "fallback"`,
    `local k = os.getenv("OAUTH_KEY") or "stub"`,
    `local p = os.getenv("DB_PASSWORD") or "changeme"`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "secret-in-fallback",
      [
        {
          regex: /process\.env\.\w*(SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL|AUTH)\w*\s*\?\?\s*['"][^'"]*['"]/,
          label: "Secret env var with ?? fallback"
        },
        {
          regex: /process\.env\.\w*(SECRET|TOKEN|KEY|PASSWORD|CREDENTIAL|AUTH)\w*\s*\|\|\s*['"][^'"]*['"]/,
          label: "Secret env var with || fallback"
        },
        {
          regex: /os\.getenv\s*\(\s*["']\w*(SECRET|TOKEN|KEY|PASSWORD).*\)\s*or\s+["']/,
          label: "Lua env var with 'or' fallback"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/secret-in-log.ts
var secretInLogMatcher = {
  noiseTier: "precise",
  slug: "secret-in-log",
  description: "Credentials or tokens appearing in log statements or error messages returned to callers",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `console.log("token", token);`,
    `console.error("failed:", apiKey);`,
    `console.warn("auth", refreshToken);`,
    `console.info("got", accessToken);`,
    `logger.info({ secret });`,
    `logger.error({ password });`,
    `migrationsLogger.warn({ apiKey });`,
    `log.debug({ credential });`,
    `({ token, foo })`,
    `({ secret: v })`,
    `JSON.stringify({ token: t });`,
    `throw new Error("token=" + token);`,
    `res.json({ token });`,
    `res.send({ secret });`,
    `return { error: "missing token" };`,
    `return { message: "credential rejected" };`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const secretNames = /\b(token|accessToken|refreshToken|secret|apiKey|api_key|password|credential|privateKey|bearerToken)\b/;
    const logPatterns = [
      /console\.(log|error|warn|info)\s*\(/,
      /logger\.\w+\s*\(/,
      /migrationsLogger\.\w+\s*\(/,
      /log\.\w+\s*\(/,
      /\{\s*(token|secret|apiKey|password|credential|accessToken|refreshToken)\s*[,}:]/,
      // structured logging
      /JSON\.stringify\s*\(.*\b(token|secret|key|password)\b/
    ];
    const errorReturnPatterns = [
      /throw\s+new\s+\w*Error\s*\(/,
      /res\.(json|send|status)\s*\(/,
      /return.*\{.*error/,
      /return.*message.*:/
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!secretNames.test(line)) continue;
      const isLog = logPatterns.some((p) => p.test(line));
      const isErrorReturn = errorReturnPatterns.some((p) => p.test(line));
      if (isLog || isErrorReturn) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 2);
        matches.push({
          vulnSlug: "secret-in-log",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: isLog ? "Secret variable in log statement" : "Secret variable in error response"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/secrets-exposure.ts
var secretsExposureMatcher = {
  noiseTier: "precise",
  slug: "secrets-exposure",
  description: "Hardcoded API keys, tokens, passwords, and secrets",
  filePatterns: ["**/*.{ts,tsx,js,jsx,json,yaml,yml,env,conf,cfg}"],
  // Examples write the secret prefix and body as TWO concatenated string
  // literals so neither literal alone matches GitHub's secret-scanning
  // push-protection patterns (which look for the full contiguous shape).
  // The matcher catches both the contiguous form (real bugs) AND the
  // split form (also a real bug — string-split is a common attempt at
  // hiding hardcoded secrets). See the matcher regex list below.
  examples: [
    `const stripe = "sk_live_" + "REDACTEDxxxxxxxxxxxxxxxx";`,
    `const k = "AIza" + "REDACTEDxxxxxxxxxxxxxxxxxxxxxxxxxxx";`,
    `const tok = "ghp_" + "REDACTEDxxxxxxxxxxxxxxxxxxxxxxxxxxxx";`,
    `const id = "AKIA" + "REDACTED1234567";`,
    `const password = "supersecret" + "Password123!";`,
    `api_key = "REDACTED" + "REDACTEDredacted"`,
    `const h = "deadbeefdeadbeefdeadbeefdeadbeef" + "deadbeefdeadbeefdeadbeefdeadbeef";`,
    `headers: { Authorization: "Bearer " + "REDACTEDxxxxxxxxxxxxxxxxxxxxx" }`
  ],
  match(content, filePath) {
    if (/\.(test|spec|fixture|mock)\./i.test(filePath)) return [];
    if (/__(tests|mocks|fixtures)__/i.test(filePath)) return [];
    return regexMatcher(
      "secrets-exposure",
      [
        // Contiguous-literal forms — what real bugs almost always look
        // like. These match the canonical issuer-format shapes.
        { regex: /['"]sk[-_]live[-_][a-zA-Z0-9]{20,}['"]/, label: "Stripe secret key" },
        { regex: /['"]AIza[a-zA-Z0-9_-]{35}['"]/, label: "Google API key" },
        { regex: /['"]ghp_[a-zA-Z0-9]{36}['"]/, label: "GitHub personal access token" },
        { regex: /['"]AKIA[A-Z0-9]{16}['"]/, label: "AWS access key ID" },
        { regex: /['"][a-f0-9]{64}['"]/, label: "potential 256-bit hex secret" },
        { regex: /Bearer\s+[a-zA-Z0-9._-]{20,}/, label: "hardcoded Bearer token" },
        // Split-literal forms — `"prefix" + "rest"` is a common attempt
        // at hiding a hardcoded secret. Match both halves quoted with
        // the issuer prefix in the first literal and an alphanum body
        // in the second. Each half alone is short enough that GitHub's
        // push-protection scanner (which keys on the contiguous shape)
        // doesn't flag it, but our matcher correctly catches the bug.
        {
          regex: /['"]sk[-_]live[-_]['"]\s*\+\s*['"][A-Za-z0-9_]{16,}['"]/,
          label: "Stripe secret key (string-split \u2014 likely hardcoded)"
        },
        {
          regex: /['"]AIza['"]\s*\+\s*['"][A-Za-z0-9_-]{20,}['"]/,
          label: "Google API key (string-split \u2014 likely hardcoded)"
        },
        {
          regex: /['"]ghp_['"]\s*\+\s*['"][A-Za-z0-9]{20,}['"]/,
          label: "GitHub personal access token (string-split \u2014 likely hardcoded)"
        },
        {
          regex: /['"]AKIA['"]\s*\+\s*['"][A-Za-z0-9_]{10,}['"]/,
          label: "AWS access key ID (string-split \u2014 likely hardcoded)"
        },
        {
          regex: /['"]Bearer\s*['"]\s*\+\s*['"][A-Za-z0-9._-]{16,}['"]/,
          label: "hardcoded Bearer token (string-split \u2014 likely hardcoded)"
        },
        {
          regex: /['"][a-f0-9]{32,}['"]\s*\+\s*['"][a-f0-9]{16,}['"]/,
          label: "long hex secret (string-split \u2014 likely hardcoded)"
        },
        // Generic concatenated credential — `"<prefix>" + "<body>"`
        // where <prefix> is a high-signal credential token.
        {
          regex: /['"](?:supersecret|secret|password|passwd|api[_-]?key|api[_-]?secret|token|REDACTED)['"]\s*\+\s*['"][^'"]{6,}['"]/i,
          label: "credential prefix concatenated with body \u2014 likely hardcoded"
        },
        // Existing generic shape — `password = "..."`, etc.
        {
          regex: /(password|passwd|secret|api_key|apikey|api[-_]secret)\s*[:=]\s*['"][^'"]{8,}['"](?!\s*[;,]\s*\/\/)/,
          label: "hardcoded credential"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/secrets-plaintext-exposure.ts
var secretsPlaintextExposureMatcher = {
  noiseTier: "precise",
  slug: "secrets-plaintext-exposure",
  description: "Decrypted plaintext flowing into logs, HTTP responses, errors, or traces",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs", "**/*.go"],
  examples: [
    `console.log(plaintext);`,
    `console.info(decryptedValue);`,
    `console.warn(decryptedSecret);`,
    `console.error(decryptedEnv);`,
    `console.debug(decryptResponse.plaintext);`,
    `logger.info({ plaintext });`,
    `logger.error("got", decryptedSecret);`,
    `log.Info("plaintext=", plaintext)`,
    `log.Printf("got %s", plaintext)`,
    `ngx.log(ngx.ERR, plaintext)`,
    `zap.String("v", plaintext)`,
    `fmt.Errorf("err: %s", plaintext)`,
    `fmt.Println(decryptedValue)`,
    `span.setAttribute("v", plaintext);`,
    `span.recordException(decryptedSecret);`,
    `res.json({ value: decryptResponse.plaintext });`,
    `response.send(plaintext);`,
    `reply.send(decryptedValue);`,
    `ctx.body(plaintext);`,
    `throw new Error(\`failed: \${plaintext}\`);`,
    `new Error(plaintext);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/_test\.go$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/(?:^|\/)__(?:tests|mocks)__\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const snippets = [];
    const PLAINTEXT = /\b(?:plaintext|decryptedValue|decryptedSecret|decryptedEnv|decryptResponse\.plaintext|nowDecryptResponse\.plaintext|decrypted\w*)\b/;
    const SINK = /\b(?:console\.(?:log|info|warn|error|debug)|logger\.(?:info|warn|error|debug|fatal|trace)|log\.(?:Info|Warn|Error|Debug|Printf|Println)|ngx\.log|zap\.(?:String|Any|Error)|fmt\.(?:Errorf|Printf|Println)|span\.(?:setAttribute|setAttributes|addEvent|recordException)|res\.(?:send|json|write|end)|response\.(?:send|json|write|end)|reply\.(?:send|code)|ctx\.(?:body|reply)|throw\s+new\s+\w*Error|new\s+Error)\s*\(/;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!SINK.test(line)) continue;
      const span = lines.slice(i, i + 4).join("\n");
      if (!PLAINTEXT.test(span)) continue;
      if (/plaintext\s*\.\s*length\b/.test(span) && !/plaintext\s*[,)]/.test(span)) continue;
      hitLines.push(i + 1);
      const s = Math.max(0, i - 1);
      const e = Math.min(lines.length, i + 4);
      snippets.push(lines.slice(s, e).join("\n"));
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "secrets-plaintext-exposure",
      lineNumbers: hitLines,
      snippet: snippets[0],
      matchedPattern: "plaintext reference inside logger/response/error/span call"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/security-behind-flag.ts
var securityBehindFlagMatcher = {
  noiseTier: "precise",
  slug: "security-behind-flag",
  description: "Security-critical code gated by feature flags \u2014 fails open when flag is off",
  filePatterns: ["**/*.{ts,tsx,js,jsx,lua,go}"],
  examples: [
    `if (featureFlag("strict-auth")) {
  await verifyToken(req);
}`,
    `if (feature_flag.is_enabled("waf")) {
  await firewallCheck(req);
}`,
    `if (LaunchDarkly.variation("rate-limit", false)) {
  throttle(req);
}`,
    `const variant = client.variation("csrf-check");
if (variant) {
  validateCsrf(req);
}`,
    `if (statsig.checkGate("strip-headers")) {
  sanitize(req.headers);
}`,
    `if (flag_enabled("encryption")) {
  encrypt(payload);
}`,
    `if (isEnabled("auth-required")) {
  await verifyToken(req);
}`,
    `if (isFeatureEnabled("rate-limit")) {
  throttle(req);
}`,
    `const flag = experiment("hmac-check");
if (flag) {
  hmac(secret, body);
}`,
    `if (getFlag("strict-cors")) {
  applyCors(req);
}`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const flagPatterns = [
      /feature_?flag|featureFlag|LaunchDarkly|variation\s*\(|statsig|flag_enabled/i,
      /isEnabled\s*\(|isFeatureEnabled/,
      /experiment\s*\(|getFlag\s*\(/
    ];
    const securityPatterns = [
      /sanitize|strip.*header|clear_header|remove.*header/i,
      /auth|verify|validate.*token|check.*permission/i,
      /waf|firewall|block|deny|reject/i,
      /rate.?limit|throttle/i,
      /csrf|cors|xss|injection/i,
      /encrypt|decrypt|sign|hmac/i
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const hasFlag = flagPatterns.some((p) => p.test(line));
      if (!hasFlag) continue;
      const context = lines.slice(Math.max(0, i - 3), Math.min(lines.length, i + 4)).join("\n");
      const hasSecurity = securityPatterns.some((p) => p.test(context));
      if (hasSecurity) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "security-behind-flag",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "Security operation gated by feature flag \u2014 verify fail-safe when flag is off"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/sensitive-data-in-traces.ts
var sensitiveDataInTracesMatcher = {
  noiseTier: "normal",
  slug: "sensitive-data-in-traces",
  description: "Sensitive data sent to tracing/observability \u2014 check for PII, secrets, tokens",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `// handles password reset
const password = req.body.password;
addTagsToCurrentSpan({ user: req.body });`,
    `// payment processing
const card = req.body.creditCard;
tracer.trace("charge", () => stripe.charge(card));`,
    `// holds secret token from env
const token = req.body.token;
span.setTag("payload", req.body);`,
    `// stores apiKey in trace
const apiKey = req.headers["x-api-key"];
Sentry.captureException(new Error("oops"));`,
    `// invoice handler
const invoice = req.body;
Sentry.setContext("billing", invoice);`,
    `// log credential issues
const credential = req.body.credential;
Sentry.setExtra("credential", credential);`,
    `// store secret
const secret = process.env.MY_SECRET;
span.setAttribute("secret", secret);`,
    `// payment handler tracing
const payment = req.body.payment;
span.addEvent("payment.received", payment);`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const tracePatterns = [
      // Datadog
      { regex: /addTagsToCurrentSpan\s*\(/, label: "Datadog span tags" },
      { regex: /tracer\.trace\s*\(/, label: "Datadog tracer" },
      { regex: /span\.setTag\s*\(/, label: "Datadog span tag" },
      // Sentry
      { regex: /Sentry\.captureException\s*\(/, label: "Sentry exception capture" },
      { regex: /Sentry\.setContext\s*\(/, label: "Sentry context" },
      { regex: /Sentry\.setExtra\s*\(/, label: "Sentry extra data" },
      // OpenTelemetry
      { regex: /span\.setAttribute\s*\(/, label: "OTel span attribute" },
      { regex: /span\.addEvent\s*\(/, label: "OTel span event" }
    ];
    const hasSensitiveContext = /password|secret|token|apiKey|api_key|credential|private.?key|client.?secret|access.?token/i.test(
      content
    ) || /payment|billing|invoice|stripe|credit.?card/i.test(content) || /req\.body|request\.body|rawReqData|requestPayload/i.test(content);
    if (!hasSensitiveContext) return [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const { regex, label } of tracePatterns) {
        if (regex.test(line)) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "sensitive-data-in-traces",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: `${label} in file with sensitive data \u2014 check what's being traced`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/service-entry-point.ts
var serviceEntryPointMatcher = {
  noiseTier: "noisy",
  slug: "service-entry-point",
  description: "Lambda handlers, event consumers, cron jobs, and API endpoints in services (weak candidate)",
  filePatterns: [
    "**/services/**/src/index.ts",
    "**/services/**/src/event-consumer.ts",
    "**/services/**/src/endpoint.ts",
    "**/services/**/src/endpoints/**/*.ts",
    "**/services/**/src/handler.ts",
    "**/services/**/src/handlers/**/*.ts"
  ],
  examples: [
    `export default (event) => process(event);`,
    `export default async (event) => handle(event);`,
    `export default async function handler(event) { return ok(); }`,
    `const c = new EventConsumer();`,
    `import { eventConsumer } from "./bus";`,
    `const ep = createEndpoint(spec);`,
    `registerEndpoint(api, def);`,
    `const router = createRouter();`,
    `await handleRequest(req);`,
    `const r = routeHandler(req);`,
    `export const POST = withSchema(schema, handler);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const entryPatterns = [
      // Lambda-style handlers
      {
        regex: /export\s+default\s+(async\s+)?(function\s*)?\(/,
        label: "Lambda default export handler (weak candidate)"
      },
      {
        regex: /export\s+default\s+async\s+function\b/,
        label: "Lambda default export handler (weak candidate)"
      },
      // Event consumers
      {
        regex: /eventConsumer|event-consumer|EventConsumer/,
        label: "Event consumer entry point (weak candidate)"
      },
      // Endpoint definitions
      {
        regex: /createEndpoint|registerEndpoint/,
        label: "Service endpoint registration (weak candidate)"
      },
      // Express-style route registration
      {
        regex: /handleRequest|routeHandler|createRouter/,
        label: "Request handler (weak candidate)"
      },
      // withSchema in apps
      {
        regex: /withSchema\s*\(/,
        label: "withSchema route handler (weak candidate)"
      }
    ];
    for (const { regex, label } of entryPatterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "service-entry-point",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/session-cookie-config.ts
var sessionCookieConfigMatcher = {
  noiseTier: "normal",
  slug: "session-cookie-config",
  description: "Session/auth cookie configuration \u2014 verify httpOnly + sameSite + secure",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `import { cookies } from "next/headers";
cookies().set("session", token, { httpOnly: true });`,
    `import { cookies } from "next/headers";
cookies().set({ name: "auth", value: token });`,
    `import session from "iron-session";
res.cookie("auth", token, { secure: true });`,
    `import { betterAuth } from "better-auth";
response.cookie("session", token);`,
    `import NextAuth from "next-auth";
const auth = new NextAuth({ providers: [] });`,
    `import { Lucia } from "lucia";
const lucia = new Lucia(adapter, {
  sessionCookie: { attributes: { secure: true } },
});`,
    `import { betterAuth } from "better-auth";
export const auth = betterAuth({
  cookieOptions: { secure: true, httpOnly: true },
});`,
    `import session from "iron-session";
const ironOptions = { cookieName: "session", password: "x" };`,
    `import { ironSession } from "iron-session/express";
ironSession({ cookieName: "session", password: "x" });`,
    `import { cookies } from "next/headers";
res.setHeader("Set-Cookie", \`session=\${token}; HttpOnly\`);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_AUTH_LIB = /\bfrom\s+["'](?:better-auth|next-auth|@auth\/core|iron-session|lucia|@lucia-auth|@clerk\/(?:nextjs|backend))[^"']*["']|\bcookies\(\)\s*\.\s*set\s*\(|\bres\.\s*setHeader\s*\(\s*["']Set-Cookie/i;
    if (!HAS_AUTH_LIB.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const PATTERNS2 = [
      {
        regex: /\bcookies\(\)\s*\.\s*set\s*\(/,
        label: "next/headers cookies().set() \u2014 verify cookie options"
      },
      {
        regex: /\bres\.\s*cookie\s*\(|\bresponse\.\s*cookie\s*\(/,
        label: "res.cookie() \u2014 verify httpOnly+secure+sameSite"
      },
      {
        regex: /\bnew\s+(?:NextAuth|BetterAuth|Lucia)\s*\(/,
        label: "Auth library construction \u2014 review cookie config"
      },
      {
        regex: /\bsessionCookie\s*:\s*\{|\bcookieOptions\s*:\s*\{|\bcookies\s*:\s*\{/,
        label: "Cookie options block"
      },
      { regex: /\bironOptions\s*=\s*\{|\bironSession\s*\(/, label: "iron-session config" },
      {
        regex: /\bsetHeader\s*\(\s*["']Set-Cookie["']/,
        label: "Raw Set-Cookie header \u2014 verify flags"
      }
    ];
    const seen = /* @__PURE__ */ new Set();
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          if (seen.has(i)) continue;
          seen.add(i);
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 8);
          matches.push({
            vulnSlug: "session-cookie-config",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/slack-signing-verification.ts
var slackSigningVerificationMatcher = {
  noiseTier: "precise",
  slug: "slack-signing-verification",
  description: "Slack request handlers \u2014 verify HMAC signing + replay protection",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `import { App } from "@slack/bolt";
export async function POST(req: Request) {
  return new Response("ok");
}`,
    `import { App } from "@slack/bolt";
const app = new App({ signingSecret: process.env.SLACK_SIGNING_SECRET });`,
    `import { App } from "@slack/bolt";
app.command("/hello", async ({ ack }) => { await ack(); });`,
    `import { App } from "@slack/bolt";
app.action("button_click", async ({ ack }) => { await ack(); });`,
    `import { App } from "@slack/bolt";
app.event("message", async ({ event }) => {});`,
    `import { App } from "@slack/bolt";
app.view("modal_submit", async ({ ack }) => { await ack(); });`,
    `import { App } from "@slack/bolt";
app.shortcut("global_shortcut", async ({ ack }) => { await ack(); });`,
    `import { AwsLambdaReceiver } from "@slack/bolt";
const receiver = new AwsLambdaReceiver({ signingSecret: "x" });`,
    `import { verifySlackRequest } from "@slack/web-api";
verifySlackRequest({ body, signingSecret });`,
    `import { createHmac } from "crypto";
const SLACK_SIGNING_SECRET = process.env.SLACK_SIGNING_SECRET;
const hmac = crypto.createHmac("sha256", slackSecret);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_SLACK = /\bfrom\s+["'](?:@slack\/(?:bolt|web-api|events-api|interactive-messages|oauth)|slack-bolt)["']|\bSlackRequestVerifier\b|\bverifySlackRequest\b|\bslack_signing_secret\b|\bSLACK_SIGNING_SECRET\b/;
    const PATH_HINT = /(?:^|\/)(?:slack|bolt)(?:[-_./]|$)|\/slack-events|\/slack-actions|\/slack-commands|\/slack-interactivity/i;
    if (!HAS_SLACK.test(content) && !PATH_HINT.test(filePath)) return [];
    const lines = content.split("\n");
    const matches = [];
    const HANDLER_PATTERNS = [
      {
        regex: /\bexport\s+(?:async\s+)?function\s+(?:POST|GET|handle)\b/,
        label: "Slack-context HTTP handler"
      },
      {
        regex: /\bnew\s+App\s*\(\s*\{[^}]*signingSecret\s*:/m,
        label: "Slack Bolt App construction"
      },
      { regex: /\bapp\.\s*command\s*\(/, label: "Slack Bolt slash-command handler" },
      { regex: /\bapp\.\s*action\s*\(/, label: "Slack Bolt action handler" },
      { regex: /\bapp\.\s*event\s*\(/, label: "Slack Bolt event handler" },
      { regex: /\bapp\.\s*view\s*\(/, label: "Slack Bolt view (modal) handler" },
      { regex: /\bapp\.\s*shortcut\s*\(/, label: "Slack Bolt shortcut handler" },
      {
        regex: /\bawsLambdaReceiver\b|\bExpressReceiver\b|\bAwsLambdaReceiver\b/,
        label: "Slack Bolt receiver wiring"
      },
      { regex: /\bverifySlackRequest\s*\(/, label: "Manual Slack signature verification" },
      {
        regex: /\bcrypto\.\s*createHmac\s*\(\s*["']sha256["'].*?(?:slack|signing)/i,
        label: "Slack HMAC-SHA256 verification"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of HANDLER_PATTERNS) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 1);
          const end = Math.min(lines.length, i + 6);
          matches.push({
            vulnSlug: "slack-signing-verification",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/snowflake-bigquery-sql.ts
var snowflakeBigquerySqlMatcher = {
  noiseTier: "precise",
  slug: "snowflake-bigquery-sql",
  description: "Snowflake / BigQuery / ClickHouse SQL via template/string interpolation",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `import snowflake from "snowflake-sdk";
connection.execute({ sqlText: \`SELECT * FROM users WHERE id = \${id}\` });`,
    `import snowflake from "snowflake-sdk";
connection.execute({ sqlText: "SELECT * FROM users WHERE id = " + id });`,
    `import { BigQuery } from "@google-cloud/bigquery";
await bigquery.query(\`SELECT * FROM users WHERE id = \${id}\`);`,
    `import { BigQuery } from "@google-cloud/bigquery";
await bigquery.createQueryJob({ query: \`SELECT * FROM \${tableName}\` });`,
    `import { createClient } from "@clickhouse/client";
await clickhouse.query(\`SELECT * FROM users WHERE id = \${id}\`);`,
    `import { createClient } from "@clickhouse/client";
await client.query({ query: \`SELECT * FROM \${table}\` });`,
    `import duckdb from "duckdb";
await connection.execute(\`SELECT * FROM \${table}\`);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_ANALYTICS = /\bfrom\s+["'](?:snowflake-sdk|@google-cloud\/bigquery|@clickhouse\/client|@clickhouse\/client-web|@databricks\/sql|duckdb|@duckdb\/[^"']*)["']/;
    if (!HAS_ANALYTICS.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const SQLTEXT_TPL = /\bsqlText\s*:\s*`[^`]*\$\{/;
    const SQLTEXT_CONCAT = /\bsqlText\s*:\s*["'][^"']*["']\s*\+/;
    const QUERY_TPL = /\b(?:bigquery|bq|clickhouse|client|connection)\.\s*query\s*\(\s*\{?\s*(?:query\s*:\s*)?`[^`]*\$\{/;
    const CREATE_JOB_TPL = /\bcreateQueryJob\s*\(\s*\{[^}]*query\s*:\s*`[^`]*\$\{/;
    const EXEC_TPL = /\b(?:connection|conn|client|db)\.\s*execute\s*\(\s*`[^`]*\$\{/;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let label;
      if (SQLTEXT_TPL.test(line)) label = "Snowflake sqlText with template interpolation";
      else if (SQLTEXT_CONCAT.test(line)) label = "Snowflake sqlText with string concatenation";
      else if (CREATE_JOB_TPL.test(line))
        label = "BigQuery createQueryJob with template interpolation";
      else if (QUERY_TPL.test(line)) label = "Analytics .query() with template interpolation";
      else if (EXEC_TPL.test(line))
        label = ".execute() with template interpolation in analytics context";
      if (!label) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 3);
      matches.push({
        vulnSlug: "snowflake-bigquery-sql",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: label
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/soql-injection.ts
var soqlInjectionMatcher = {
  noiseTier: "precise",
  slug: "soql-injection",
  description: "Salesforce SOQL built with template/string interpolation",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  requires: { tech: ["apex", "salesforce"] },
  examples: [
    `import jsforce from "jsforce";
await conn.query(\`SELECT Id FROM Account WHERE Name = '\${name}'\`);`,
    `import jsforce from "jsforce";
await conn.queryAll(\`SELECT Id FROM Lead WHERE Email = '\${email}'\`);`,
    `import jsforce from "jsforce";
await conn.query("SELECT Id FROM Account WHERE Id = " + id);`,
    `import { Connection } from "@jsforce/jsforce-node";
await sf.query(\`SELECT Id FROM Account WHERE Id = '\${id}'\`);`,
    `import jsforce from "jsforce";
await tooling.query(\`SELECT Id FROM ApexClass WHERE Name = '\${name}'\`);`,
    `import { something } from "@salesforce/api";
const soql = \`SELECT Id FROM Account WHERE Name = '\${name}'\`;`,
    `import jsforce from "jsforce";
await sfConn.queryMore(\`SELECT Id FROM Lead WHERE Status = '\${status}'\`);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_SF = /\bfrom\s+["'](?:jsforce[^"']*|@jsforce\/[^"']*|@salesforce\/[^"']*)["']|\b(?:sf|salesforce|conn|sfConn)\.\s*query(?:All)?\s*\(/;
    if (!HAS_SF.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const TPL = /\b(?:sf|salesforce|conn|sfConn|tooling)\.\s*query(?:All|More)?\s*\(\s*`[^`]*\$\{/;
    const CONCAT = /\b(?:sf|salesforce|conn|sfConn|tooling)\.\s*query(?:All|More)?\s*\(\s*["'][^"']*["']\s*\+/;
    const SOQL_TPL = /`(?:[^`]*?\bSELECT\s+[^`]*?\bFROM\s+[A-Za-z_][A-Za-z0-9_]*[^`]*?)\$\{/i;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let label;
      if (TPL.test(line)) label = "SOQL via template literal \u2014 possible SOQL injection";
      else if (CONCAT.test(line)) label = "SOQL via string concat \u2014 possible SOQL injection";
      else if (SOQL_TPL.test(line)) label = "SOQL-shaped template literal with interpolation";
      if (!label) continue;
      const start = Math.max(0, i - 1);
      const end = Math.min(lines.length, i + 3);
      matches.push({
        vulnSlug: "soql-injection",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, end).join("\n"),
        matchedPattern: label
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/spread-operator-injection.ts
var spreadOperatorInjectionMatcher = {
  noiseTier: "precise",
  slug: "spread-operator-injection",
  description: "Object spread of user input into payloads \u2014 prototype pollution or key injection risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const payload = { ...req.body, createdAt: new Date() };`,
    `await db.user.create({ data: { ...request.body } });`,
    `const merged = { ...parsed.body };`,
    `return { ...parsed.query, page: 1 };`,
    `const next = { ...searchParams };`,
    `function build(params) { return { ...params, role: "user" }; }`,
    `const out = { ...query };`,
    `Object.assign({}, req, { id: 1 })`,
    `Object.assign({ }, body, { extra: true })`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "spread-operator-injection",
      [
        { regex: /\.\.\.(req\.body|request\.body)/, label: "Spread of req.body" },
        { regex: /\.\.\.(parsed\.body|parsed\.query)/, label: "Spread of parsed input" },
        { regex: /\.\.\.searchParams/, label: "Spread of searchParams" },
        { regex: /\.\.\.(params|query)\b/, label: "Spread of params/query" },
        {
          regex: /Object\.assign\s*\(\s*\{?\s*\}\s*,\s*(req|body|params|query)/,
          label: "Object.assign from user input"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/sql-injection.ts
var sqlInjectionMatcher = {
  noiseTier: "precise",
  slug: "sql-injection",
  description: "Raw SQL string concatenation or interpolation",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    "const q = `SELECT * FROM users WHERE id = ${id}`;",
    "const q = `INSERT INTO logs (msg) VALUES (${msg})`;",
    "const q = `UPDATE users SET name = ${name} WHERE id = 1`;",
    "const q = `DELETE FROM items WHERE id = ${id}`;",
    `const q = "SELECT * FROM t WHERE id =" + id;`,
    `const q = "INSERT INTO t VALUES (" + v + ")";`,
    `const q = "UPDATE t SET x = " + v;`,
    `const q = "DELETE FROM t WHERE id =" + id;`,
    "db.query(`SELECT ${col} FROM t`);",
    "knex.raw(`SELECT ${col} FROM t`);",
    "const c = `SELECT * FROM t WHERE name LIKE ${pat}`;",
    "const c = `SELECT * FROM t WHERE name LIKE '%${pat}%'`;",
    "const c = `SELECT * FROM t WHERE name RLIKE ${pat}`;",
    "executeQuery(`SELECT * FROM t WHERE id = ${id}`);",
    `sql.raw(rawString)`,
    "const r = sql`SELECT * FROM t WHERE id = ${id}`;"
  ],
  match(content, _filePath) {
    return regexMatcher(
      "sql-injection",
      [
        {
          regex: /`\s*SELECT\s+[^`]{0,400}\$\{/,
          label: "template literal SELECT with interpolation"
        },
        {
          regex: /`\s*INSERT\s+[^`]{0,400}\$\{/,
          label: "template literal INSERT with interpolation"
        },
        {
          regex: /`\s*UPDATE\s+[^`]{0,400}\$\{/,
          label: "template literal UPDATE with interpolation"
        },
        {
          regex: /`\s*DELETE\s+[^`]{0,400}\$\{/,
          label: "template literal DELETE with interpolation"
        },
        { regex: /['"]SELECT\s+[^'"]{0,400}['"]\s*\+/, label: "string concat SELECT" },
        { regex: /['"]INSERT\s+[^'"]{0,400}['"]\s*\+/, label: "string concat INSERT" },
        { regex: /['"]UPDATE\s+[^'"]{0,400}['"]\s*\+/, label: "string concat UPDATE" },
        { regex: /['"]DELETE\s+[^'"]{0,400}['"]\s*\+/, label: "string concat DELETE" },
        { regex: /query\s*\(\s*`[^`]*\$\{/, label: "query() with interpolation" },
        { regex: /\.raw\s*\(\s*`[^`]*\$\{/, label: ".raw() with interpolation" },
        { regex: /LIKE\s+['"]?%?\$\{/, label: "LIKE with interpolation" },
        { regex: /LIKE\s+['"]%\$\{/, label: "LIKE '%${...}%' pattern" },
        { regex: /RLIKE\s+['"]?\$\{/, label: "RLIKE with interpolation" },
        {
          regex: /executeQuery\w*\s*\(\s*`[^`]*\$\{/,
          label: "executeQuery with template interpolation"
        },
        { regex: /sql\.raw\s*\(/, label: "sql.raw() \u2014 raw SQL (verify parameterized)" },
        {
          regex: /sql`[^`]{0,400}\$\{[^}]{0,200}\}/,
          label: "sql tagged template with interpolation"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/ssrf.ts
var USER_INPUT_TOKEN = String.raw`(?:req\.|request\.|params\.|query\.|body\.|parsed\.|input\.|ctx\.|payload\.|searchParams|nextUrl|formData|headers\(\)|cookies\(\))`;
var ssrfMatcher = {
  noiseTier: "normal",
  slug: "ssrf",
  description: "HTTP requests with dynamic/user-controlled URLs",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `fetch(req.body.url);`,
    `fetch(query.target);`,
    `fetch(searchParams.get('u'));`,
    `fetch(input.url);`,
    `axios.get(req.body.endpoint);`,
    `axios.post(params.url, data);`,
    `axios(query.target);`,
    `got(body.url);`,
    `ky(payload.url);`,
    `superagent(ctx.url);`,
    `https.get(req.query.target);`,
    "https.request(`https://api/${req.body.host}`);",
    `page.goto(req.body.url);`,
    `browser.goto(params.target);`,
    `page.setContent(req.body.html);`,
    `fetch(headers().get('x-target'));`,
    `fetch(cookies().get('redirect')?.value);`,
    `axios.post(formData.get('url'));`,
    `new URL(req.query.target);`,
    `new URL(nextUrl.searchParams.get('href'));`,
    "fetch(`${userBase}/items`);",
    "const target = `https://${req.body.host}`;",
    `const url = "http://" + req.query.host;`,
    `const targetUrl = req.query.url;`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = regexMatcher(
      "ssrf",
      [
        {
          regex: new RegExp(String.raw`fetch\s*\(\s*${USER_INPUT_TOKEN}`),
          label: "fetch with request-derived URL"
        },
        {
          regex: new RegExp(
            String.raw`axios\.(get|post|put|delete|patch|request)\s*\(\s*${USER_INPUT_TOKEN}`
          ),
          label: "axios with request-derived URL"
        },
        {
          regex: new RegExp(String.raw`\b(axios|got|ky|superagent)\s*\(\s*${USER_INPUT_TOKEN}`),
          label: "HTTP client call with request-derived URL"
        },
        {
          regex: new RegExp(String.raw`https?\.(get|request)\s*\(\s*${USER_INPUT_TOKEN}`),
          label: "http(s).get/request with request-derived URL"
        },
        {
          regex: new RegExp(
            String.raw`\b(page|browser)\.(goto|setContent)\s*\(\s*${USER_INPUT_TOKEN}`
          ),
          label: "browser navigation with request-derived URL"
        },
        { regex: /https?\.request\s*\(\s*`[^`]*\$\{/, label: "http.request with interpolated URL" },
        {
          regex: new RegExp(String.raw`new\s+URL\s*\(\s*${USER_INPUT_TOKEN}`),
          label: "new URL from request data"
        },
        {
          regex: /(?:const|let|var)\s+\w*[uU]rl\w*\s*=\s*[^;\n]*\b(?:req|request|params|query|body|searchParams|nextUrl|input)\b/,
          label: "URL-named variable assigned from request data"
        }
      ],
      content
    );
    const lines = content.split("\n");
    const constantBaseUrls = /VERCEL_API_URL|API_BASE|API_URL|INTERNAL_URL|process\.env\.\w+_URL/;
    const stringBuiltUrlRules = [
      {
        regex: /fetch\s*\(\s*`[^`]*\$\{/,
        label: "fetch with interpolated URL (non-constant base)"
      },
      { regex: /https?:\/\/[^`]*\$\{/, label: "string-built URL via template interpolation" },
      { regex: /["']https?:\/\/["']\s*\+/, label: "string-built URL via concatenation" }
    ];
    for (let i = 0; i < lines.length; i++) {
      if (constantBaseUrls.test(lines[i])) continue;
      for (const { regex, label } of stringBuiltUrlRules) {
        if (!regex.test(lines[i])) continue;
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "ssrf",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: label
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/streaming-endpoint.ts
var streamingEndpointMatcher = {
  noiseTier: "normal",
  slug: "streaming-endpoint",
  description: "AI streaming endpoints \u2014 auth bypass, prompt injection, state leakage risk",
  filePatterns: [
    "**/route.{ts,tsx,js,jsx}",
    "**/api/**/*.{ts,tsx,js,jsx}",
    "**/app/**/*.{ts,tsx,js,jsx}"
  ],
  examples: [
    `const result = streamText({ model, messages });`,
    `const stream = streamObject({ model, schema, prompt });`,
    `const out = await generateText({ model, prompt });`,
    `return new StreamingTextResponse(stream);`,
    `const stream = new ReadableStream({ start(c) { c.enqueue("hi"); } });`,
    `const tx = new TransformStream();`,
    `const res = await openai.chat.completions.create({ model: "gpt-4", stream: true });`,
    `const r = await client.chat.completions.create({ model, messages, stream: true });`,
    `fetch("/api/chat", { method: "POST" });`,
    `app.post("/api/completion", handler);`,
    `await fetch("/api/generate", { method: "POST" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const patterns = [
      // AI SDK streaming
      { regex: /streamText\s*\(/, label: "AI SDK streamText \u2014 streaming LLM endpoint" },
      { regex: /streamObject\s*\(/, label: "AI SDK streamObject \u2014 streaming structured output" },
      { regex: /generateText\s*\(/, label: "AI SDK generateText \u2014 LLM generation endpoint" },
      { regex: /StreamingTextResponse/, label: "StreamingTextResponse \u2014 legacy streaming pattern" },
      // Raw streaming responses
      { regex: /new\s+ReadableStream/, label: "ReadableStream \u2014 raw streaming response" },
      { regex: /TransformStream/, label: "TransformStream \u2014 streaming pipeline" },
      // OpenAI/Anthropic direct
      {
        regex: /openai.{0,80}stream.{0,40}true|stream:\s*true/i,
        label: "LLM API call with streaming enabled"
      },
      {
        regex: /\.chat\.completions\.create[^)]{0,200}stream/i,
        label: "OpenAI chat completion stream"
      },
      // Chat/completion endpoints
      {
        regex: /\/api\/chat|\/api\/completion|\/api\/generate/i,
        label: "AI chat/completion API route"
      }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "streaming-endpoint",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: label
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/swift-vapor-route.ts
var swiftVaporRouteMatcher = {
  noiseTier: "noisy",
  slug: "swift-vapor-route",
  description: "Swift Vapor route registrations (gated on Vapor)",
  filePatterns: ["**/*.swift"],
  requires: { tech: ["vapor"] },
  examples: [
    `app.get("hello") { req in return "hi" }`,
    `app.post("users") { req async throws -> User in }`,
    `app.put("users", ":id") { req in }`,
    `app.patch("users", ":id") { req in }`,
    `app.delete("users", ":id") { req in }`,
    `app.on(.POST, "upload", body: .stream) { req in }`,
    `let protected = app.grouped(User.guardMiddleware())`,
    `let secured = routes.grouped(Token.authenticator())`,
    `let id = req.parameters.get("id")`,
    `let q = try req.query.decode(Search.self)`,
    `let body = try req.content.decode(User.self)`,
    `let user = try req.auth.require(User.self)`,
    `let auth = req.headers.bearerAuthorization`,
    `final class UserController: RouteCollection {}`,
    `class AdminController : RouteCollection {`
  ],
  match(content, filePath) {
    if (/\/(Tests|tests)\//.test(filePath)) return [];
    return regexMatcher(
      "swift-vapor-route",
      [
        {
          regex: /\bapp\.(?:get|post|put|patch|delete|on)\s*\(/,
          label: "app.<verb>('/path') registration"
        },
        {
          regex: /\bgrouped\s*\(\s*\w+\.[A-Za-z]+\(\)\s*\)/,
          label: ".grouped(Middleware()) auth scope"
        },
        { regex: /\breq\.(?:parameters|query|content|auth|headers)\b/, label: "req.* accessor" },
        {
          regex: /\bclass\s+\w+Controller\s*:\s*RouteCollection\b/,
          label: "RouteCollection conformance"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/test-header-bypass.ts
var testHeaderBypassMatcher = {
  noiseTier: "precise",
  slug: "test-header-bypass",
  description: "Test/debug headers that bypass security checks in production",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `if (req.headers["x-automated-test"]) skip();`,
    `if (req.headers["x-test-bypass"]) return next();`,
    `if (headers.get("x-debug")) bypass();`,
    `if (req.headers["x-internal"]) skipAuth();`,
    `if (req.headers["x-bypass"]) disable();`,
    `if (req.headers["x-skip-auth"]) return next();`,
    `if (req.headers["x-no-rate-limit"]) skip();`,
    `if (req.headers["x-admin"]) bypass();`,
    `if ("test" === headers["x-mode"]) return true;`,
    `if (headers["x-something"] === "test") skip();`
  ],
  match(content, filePath) {
    if (/\.(test|spec|mock|stub)\./i.test(filePath)) return [];
    if (/node_modules|\.next|dist\//.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const headerPatterns = [
      { regex: /x-automated-test/i, label: "x-automated-test header" },
      { regex: /x-test-/i, label: "x-test-* header" },
      { regex: /x-debug/i, label: "x-debug header" },
      { regex: /x-internal/i, label: "x-internal header" },
      { regex: /x-bypass/i, label: "x-bypass header" },
      { regex: /x-skip-auth/i, label: "x-skip-auth header" },
      { regex: /x-no-rate-limit/i, label: "x-no-rate-limit header" },
      { regex: /x-admin/i, label: "x-admin header" },
      { regex: /['"]test['"].{0,40}===.{0,40}headers/i, label: "test value in header check" },
      { regex: /headers.{0,80}['"]test['"]/i, label: "header compared to test" }
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      for (const { regex, label } of headerPatterns) {
        if (regex.test(line)) {
          const context = lines.slice(Math.max(0, i - 3), Math.min(lines.length, i + 3)).join("\n");
          if (/if\s*\(|skip|bypass|disable|return\s+(true|next)|continue/.test(context)) {
            const start = Math.max(0, i - 2);
            const end = Math.min(lines.length, i + 3);
            matches.push({
              vulnSlug: "test-header-bypass",
              lineNumbers: [i + 1],
              snippet: lines.slice(start, end).join("\n"),
              matchedPattern: `${label} \u2014 may bypass security in production`
            });
            break;
          }
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/tf-encryption-missing.ts
var tfEncryptionMissingMatcher = {
  noiseTier: "normal",
  slug: "tf-encryption-missing",
  description: "Terraform storage resource (S3/RDS/EBS/DynamoDB/SNS/SQS) without encryption-at-rest config",
  filePatterns: ["**/*.tf", "**/*.tf.json"],
  requires: { tech: ["terraform"] },
  examples: [
    `resource "aws_s3_bucket" "logs" {
  bucket = "my-logs"
}`,
    `resource "aws_db_instance" "db" {
  engine = "postgres"
}`,
    `resource "aws_rds_cluster" "main" {
  engine = "aurora-postgresql"
}`,
    `resource "aws_ebs_volume" "data" {
  size = 100
}`,
    `resource "aws_dynamodb_table" "users" {
  name = "users"
  hash_key = "id"
}`,
    `resource "aws_sns_topic" "alerts" {
  name = "alerts"
}`,
    `resource "aws_sqs_queue" "jobs" {
  name = "jobs"
}`,
    `resource "aws_elasticache_replication_group" "cache" {
  replication_group_id = "cache"
}`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const RESOURCES = [
      // S3 bucket: needs aws_s3_bucket_server_side_encryption_configuration in file or sse block
      {
        regex: /^\s*resource\s+"aws_s3_bucket"\s+/i,
        encAttr: /aws_s3_bucket_server_side_encryption_configuration|server_side_encryption_configuration\s*\{/i,
        label: "S3 bucket"
      },
      // RDS / Aurora
      {
        regex: /^\s*resource\s+"aws_(?:rds_cluster|db_instance|db_cluster)"\s+/i,
        encAttr: /\bstorage_encrypted\s*=\s*true\b/i,
        label: "RDS/Aurora"
      },
      // EBS volume
      {
        regex: /^\s*resource\s+"aws_ebs_volume"\s+/i,
        encAttr: /\bencrypted\s*=\s*true\b/i,
        label: "EBS volume"
      },
      // EBS in launch template / launch configuration block_device_mappings
      // (skip — too noisy at file level)
      // DynamoDB
      {
        regex: /^\s*resource\s+"aws_dynamodb_table"\s+/i,
        encAttr: /\bserver_side_encryption\s*\{[^}]*enabled\s*=\s*true/is,
        label: "DynamoDB"
      },
      // SNS
      {
        regex: /^\s*resource\s+"aws_sns_topic"\s+/i,
        encAttr: /\bkms_master_key_id\s*=/i,
        label: "SNS topic"
      },
      // SQS
      {
        regex: /^\s*resource\s+"aws_sqs_queue"\s+/i,
        encAttr: /\bkms_master_key_id\s*=|\bsqs_managed_sse_enabled\s*=\s*true/i,
        label: "SQS queue"
      },
      // ElastiCache redis
      {
        regex: /^\s*resource\s+"aws_elasticache_replication_group"\s+/i,
        encAttr: /\bat_rest_encryption_enabled\s*=\s*true/i,
        label: "ElastiCache"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, encAttr, label } of RESOURCES) {
        if (!regex.test(lines[i])) continue;
        if (encAttr.test(content)) continue;
        hitLines.push(i + 1);
        labels.add(`${label} without encryption`);
        if (firstContext === void 0) {
          const s = Math.max(0, i - 1);
          const e = Math.min(lines.length, i + 6);
          firstContext = lines.slice(s, e).join("\n");
        }
        break;
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-encryption-missing",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/tf-iac-surface.ts
var tfIacSurfaceMatcher = {
  noiseTier: "normal",
  slug: "tf-iac-surface",
  description: "Terraform/HCL/Sentinel file declaring security-critical infrastructure resources",
  filePatterns: ["**/*.tf", "**/*.tf.json", "**/*.hcl", "**/*.sentinel"],
  requires: { tech: ["terraform"] },
  examples: [
    `resource "aws_iam_role" "service" {`,
    `resource "aws_iam_policy_attachment" "admin" {`,
    `resource "aws_kms_key" "main" {`,
    `resource "aws_eks_cluster" "main" {`,
    `resource "aws_security_group" "web" {`,
    `resource "aws_network_acl" "main" {`,
    `resource "aws_vpc_endpoint" "s3" {`,
    `resource "aws_s3_bucket_policy" "logs" {`,
    `resource "aws_route53_record" "www" {`,
    `resource "aws_secretsmanager_secret" "db" {`,
    `resource "aws_lb_listener" "https" {`,
    `resource "kubernetes_cluster_role" "admin" {`,
    `resource "helm_release" "prom" {`,
    `data "aws_iam_policy_document" "doc" {`,
    `import "tfplan"`
  ],
  match(content, filePath) {
    if (/\.terraform\//.test(filePath)) return [];
    const PATTERNS2 = [
      {
        regex: /^\s*resource\s+"aws_iam_(?:role|policy|user|group|policy_attachment|access_key|service_linked_role|openid_connect_provider|saml_provider|role_policy|role_policy_attachment|user_policy|group_policy)"\s+/m,
        label: "aws_iam_*"
      },
      { regex: /^\s*resource\s+"aws_kms_(?:key|alias|grant|key_policy)"\s+/m, label: "aws_kms_*" },
      {
        regex: /^\s*resource\s+"aws_eks_(?:cluster|node_group|fargate_profile|access_entry|access_policy_association|identity_provider_config|addon|pod_identity_association)"\s+/m,
        label: "aws_eks_*"
      },
      { regex: /^\s*resource\s+"aws_security_group(?:_rule)?"\s+/m, label: "aws_security_group" },
      {
        regex: /^\s*resource\s+"aws_network_acl(?:_rule|_association)?"\s+/m,
        label: "aws_network_acl_*"
      },
      {
        regex: /^\s*resource\s+"aws_vpc(?:_peering_connection|_endpoint|_endpoint_policy)?"\s+/m,
        label: "aws_vpc_*"
      },
      {
        regex: /^\s*resource\s+"aws_s3_bucket(?:_policy|_public_access_block|_versioning|_server_side_encryption_configuration|_acl|_lifecycle_configuration|_logging|_object_lock_configuration|_replication_configuration)?"\s+/m,
        label: "aws_s3_bucket_*"
      },
      {
        regex: /^\s*resource\s+"aws_route53_(?:record|zone|zone_association|delegation_set|health_check)"\s+/m,
        label: "aws_route53_*"
      },
      {
        regex: /^\s*resource\s+"aws_secretsmanager_(?:secret|secret_version|secret_policy|secret_rotation)"\s+/m,
        label: "aws_secretsmanager_*"
      },
      {
        regex: /^\s*resource\s+"aws_lb_listener(?:_rule|_certificate)?"\s+/m,
        label: "aws_lb_listener_*"
      },
      {
        regex: /^\s*resource\s+"kubernetes_(?:secret|cluster_role|cluster_role_binding|role|role_binding|service_account|network_policy|pod_security_policy|namespace|config_map)(?:_v1)?"\s+/m,
        label: "kubernetes_*"
      },
      { regex: /^\s*resource\s+"helm_release"\s+/m, label: "helm_release" },
      { regex: /^\s*data\s+"aws_iam_policy_document"\s+/m, label: "aws_iam_policy_document data" },
      // Sentinel policies
      { regex: /^\s*(?:rule|policy|main)\s*=\s*function\s*\(/m, label: "Sentinel rule/policy" },
      { regex: /^\s*import\s+"tfplan(?:-functions)?"/m, label: "Sentinel tfplan import" }
    ];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 1);
            const e = Math.min(lines.length, i + 4);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-iac-surface",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/tf-iam-wildcard.ts
var tfIamWildcardMatcher = {
  noiseTier: "precise",
  slug: "tf-iam-wildcard",
  description: "Terraform IAM/KMS/S3/SNS policy with wildcard Action/Resource/Principal",
  filePatterns: ["**/*.tf", "**/*.tf.json", "**/*.hcl"],
  requires: { tech: ["terraform"] },
  examples: [
    `    actions = ["*"]`,
    `"Action": "*",`,
    `    resources = ["*"]`,
    `"Resource": "*",`,
    `"Principal": "*",`,
    `"AWS": "*"`,
    `    identifiers = ["*"]`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      // actions = ["*"]   or  Action = "*"
      { regex: /^\s*actions\s*=\s*\[\s*['"]\*['"]\s*\]/i, label: 'actions = ["*"]' },
      { regex: /['"]Action['"]\s*:\s*['"]\*['"]/i, label: 'Action = "*" (JSON)' },
      // resources = ["*"]
      { regex: /^\s*resources\s*=\s*\[\s*['"]\*['"]\s*\]/i, label: 'resources = ["*"]' },
      { regex: /['"]Resource['"]\s*:\s*['"]\*['"]/i, label: 'Resource = "*" (JSON)' },
      // principal "*"
      { regex: /['"]Principal['"]\s*:\s*['"]\*['"]/i, label: 'Principal = "*" (JSON)' },
      { regex: /['"]AWS['"]\s*:\s*['"]\*['"]/i, label: '"AWS": "*" trust' },
      // principals block { type = "AWS"; identifiers = ["*"] }
      { regex: /\bidentifiers\s*=\s*\[\s*['"]\*['"]\s*\]/i, label: 'identifiers = ["*"]' },
      // assume_role_policy with star
      {
        regex: /\bassume_role_policy\s*=\s*[^"]*\bAWS['"]\s*:\s*['"]\*['"]/i,
        label: "assume_role with AWS:*"
      }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-iam-wildcard",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/tf-module-unpinned.ts
var tfModuleUnpinnedMatcher = {
  noiseTier: "precise",
  slug: "tf-module-unpinned",
  description: "Terraform module references a remote git/github source without a commit-SHA pin",
  filePatterns: ["**/*.tf"],
  requires: { tech: ["terraform"] },
  examples: [
    `module "vpc" {
  source = "github.com/terraform-aws-modules/terraform-aws-vpc"
}`,
    `module "k8s" {
  source = "git::https://github.com/some-org/k8s-module.git"
}`,
    `module "iam" {
  source = "git::ssh://git@github.com/org/iam.git?ref=main"
}`,
    `module "registry" {
  source = "terraform-aws-modules/eks/aws"
}`,
    `module "external" {
  source = "https://example.com/modules/foo.tar.gz"
}`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    let inModule = false;
    let moduleStart = -1;
    let moduleSource = "";
    let moduleHasVersion = false;
    let depth = 0;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!inModule && /^\s*module\s+"[^"]+"\s*\{/.test(line)) {
        inModule = true;
        moduleStart = i;
        moduleSource = "";
        moduleHasVersion = false;
        depth = 0;
      }
      if (!inModule) continue;
      for (const ch of line) {
        if (ch === "{") depth++;
        else if (ch === "}") depth--;
      }
      const sm = line.match(/\bsource\s*=\s*"([^"]+)"/);
      if (sm && !moduleSource) moduleSource = sm[1];
      if (/\bversion\s*=\s*"[^"]+"/.test(line)) moduleHasVersion = true;
      if (depth <= 0) {
        const src = moduleSource;
        const local = src.startsWith("./") || src.startsWith("../") || src.startsWith("/");
        const looksRemote = /^(?:git::|github\.com\/|bitbucket\.org\/|https?:\/\/)/i.test(src) || /^[\w.-]+@/.test(src);
        const looksRegistry = /^[a-z0-9-]+\/[a-z0-9-]+\/[a-z0-9-]+(?:\/\/[\w/-]+)?$/i.test(src) && !src.startsWith("git::");
        const isPinned = /\?ref=[0-9a-f]{7,40}\b/.test(src) || /(\?|&)tag=[\w.-]+/.test(src);
        const okPinned = local || looksRegistry && moduleHasVersion || looksRemote && isPinned;
        if (!okPinned && (looksRemote || looksRegistry && !moduleHasVersion)) {
          hitLines.push(moduleStart + 1);
          labels.add(local ? "local" : looksRegistry ? "registry no version" : "remote unpinned");
          if (firstContext === void 0) {
            const s = Math.max(0, moduleStart);
            const e = Math.min(lines.length, i + 2);
            firstContext = lines.slice(s, e).join("\n");
          }
        }
        inModule = false;
        moduleStart = -1;
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-module-unpinned",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/tf-public-ingress.ts
var tfPublicIngressMatcher = {
  noiseTier: "precise",
  slug: "tf-public-ingress",
  description: "Terraform security-group / NACL / EKS ingress allowing 0.0.0.0/0 on non-HTTPS ports",
  filePatterns: ["**/*.tf", "**/*.tf.json", "**/*.hcl"],
  requires: { tech: ["terraform"] },
  examples: [
    `ingress {
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}`,
    `ingress {
  from_port = 3306
  to_port = 3306
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}`,
    `resource "aws_security_group_rule" "open" {
  type = "ingress"
  from_port = 5432
  to_port = 5432
  cidr_blocks = ["0.0.0.0/0"]
}`,
    `vpc_config {
  endpoint_public_access = true
  subnet_ids = var.subnets
}`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const SENSITIVE_PORTS = /\b(?:from_port|to_port|port)\s*=\s*(?:22|3389|5432|3306|6379|27017|9200|9300|11211|5601|8086|9092|2049|445|1433|5984|9300|9000|8080|3000|5000|8000|9090|9443|6443|10250|2375|2376|2377|7000|7001|9999|11210|13316)\b/;
    const blocks = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      const isStart = /^\s*(?:ingress|egress)\s*\{|resource\s+"aws_(?:security_group_rule|network_acl_rule)"/.test(
        line
      );
      if (!isStart) {
        i++;
        continue;
      }
      const start = i;
      let depth = 0;
      let started = false;
      let text = "";
      outer: for (let j = i; j < lines.length && j < i + 40; j++) {
        text += (started ? "\n" : "") + lines[j];
        for (const ch of lines[j]) {
          if (ch === "{") {
            depth++;
            started = true;
          } else if (ch === "}") {
            depth--;
            if (started && depth === 0) {
              i = j;
              break outer;
            }
          }
        }
      }
      blocks.push({ start, text });
      i++;
    }
    for (const b of blocks) {
      const hasOpenCidr = /\b(?:cidr_blocks|cidr_block)\s*=\s*\[?\s*['"]0\.0\.0\.0\/0['"]|::\/0/.test(b.text);
      if (!hasOpenCidr) continue;
      const hasSensitivePort = SENSITIVE_PORTS.test(b.text);
      const hasOnlyWebPort = /\bfrom_port\s*=\s*(?:80|443)\b/.test(b.text) && /\bto_port\s*=\s*(?:80|443)\b/.test(b.text) && !hasSensitivePort;
      if (hasOnlyWebPort) continue;
      hitLines.push(b.start + 1);
      labels.add("0.0.0.0/0 ingress on non-web port");
      if (firstContext === void 0) {
        const s = Math.max(0, b.start - 1);
        const e = Math.min(lines.length, b.start + b.text.split("\n").length + 1);
        firstContext = lines.slice(s, e).join("\n");
      }
    }
    for (let j = 0; j < lines.length; j++) {
      if (/\bendpoint_public_access\s*=\s*true/.test(lines[j])) {
        const span = lines.slice(Math.max(0, j - 8), Math.min(lines.length, j + 9)).join("\n");
        if (!/\bendpoint_public_access_cidrs\b/.test(span)) {
          hitLines.push(j + 1);
          labels.add("EKS public endpoint without CIDR allow-list");
          if (firstContext === void 0) {
            const s = Math.max(0, j - 2);
            const e = Math.min(lines.length, j + 4);
            firstContext = lines.slice(s, e).join("\n");
          }
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-public-ingress",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 3).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/tf-secret-in-data.ts
var tfSecretInDataMatcher = {
  noiseTier: "precise",
  slug: "tf-secret-in-data",
  description: "kubernetes_secret resource with hardcoded plaintext value in data block",
  filePatterns: ["**/*.tf"],
  requires: { tech: ["terraform"] },
  examples: [
    `resource "kubernetes_secret" "db" {
  metadata { name = "db" }
  data = {
    password = "supersecret-plaintext-value"
  }
}`,
    `resource "kubernetes_secret_v1" "api" {
  metadata { name = "api" }
  data = {
    api_key = "AKIAIOSFODNN7EXAMPLE"
  }
}`,
    `resource "kubernetes_secret" "tokens" {
  metadata { name = "tokens" }
  data = {
    token = "REDACTED-plaintext-token-value-goes-here"
  }
}`
  ],
  match(content) {
    const lines = content.split("\n");
    const hitLines = [];
    const snippets = [];
    let inSecret = false;
    let inData = false;
    let braceDepth = 0;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/^\s*resource\s+"kubernetes_secret(?:_v1)?"\s+/.test(line)) {
        inSecret = true;
        braceDepth = 0;
      }
      if (!inSecret) continue;
      for (const ch of line) {
        if (ch === "{") braceDepth++;
        else if (ch === "}") {
          braceDepth--;
          if (braceDepth === 0) {
            inSecret = false;
            inData = false;
          }
        }
      }
      if (/^\s*data\s*=?\s*\{/.test(line)) inData = true;
      if (inData && braceDepth <= 1 && /^\s*\}/.test(line)) inData = false;
      if (!inData) continue;
      const m = line.match(/^\s*[\w-]+\s*=\s*"([^"]+)"/);
      if (!m) continue;
      const value = m[1];
      if (/\$\{[^}]+\}/.test(value)) continue;
      if (value.length < 8) continue;
      if (/^(default|true|false|enabled|disabled|none|public|private)$/i.test(value)) continue;
      hitLines.push(i + 1);
      const s = Math.max(0, i - 1);
      const e = Math.min(lines.length, i + 2);
      snippets.push(lines.slice(s, e).join("\n"));
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "tf-secret-in-data",
      lineNumbers: hitLines,
      snippet: snippets[0],
      matchedPattern: "kubernetes_secret.data with literal value"
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/trpc-public-procedure.ts
var trpcPublicProcedureMatcher = {
  noiseTier: "normal",
  slug: "trpc-public-procedure",
  description: "tRPC publicProcedure used in a router that looks authenticated \u2014 verify it should not be authedProcedure",
  filePatterns: ["**/*.ts", "**/*.tsx"],
  requires: { tech: ["trpc"] },
  examples: [
    `export const listUsers = publicProcedure.query(({ ctx }) => {
  return ctx.prisma.user.findMany({ where: { id: ctx.session.user.id } });
});`,
    `publicProcedure.input(z.object({})).mutation(({ ctx }) => {
  return ctx.user.id;
});`,
    `publicProcedure.input(schema).query(async ({ ctx, input }) => {
  const userId = ctx.userId;
  return userId;
});`,
    `publicProcedure.use(async ({ ctx, next }) => {
  if (!ctx.session) throw new Error();
  return next();
});`,
    `export const getMe = publicProcedure.query(({ ctx }) => {
  return ctx.currentUser;
});`,
    `publicProcedure.mutation(async ({ ctx }) => {
  return getSession(ctx);
});`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (!/\bpublicProcedure\b/.test(content)) return [];
    if (/\/procedures\/publicProcedure\.|\/publicViewer\//.test(filePath)) return [];
    const lines = content.split("\n");
    const matches = [];
    const sessionAccess = /\bctx\.(?:session|user|userId|currentUser|prisma)|getSession\s*\(\s*ctx/;
    const fileLooksAuthed = /\/(?:viewer|admin|organizations?|teams?|settings|billing|payments?|workflows?)\//.test(
      filePath
    );
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (!/\bpublicProcedure\s*\.\s*(?:input|query|mutation|use)\b/.test(line)) continue;
      const start = Math.max(0, i - 2);
      const end = Math.min(lines.length, i + 12);
      const window = lines.slice(start, end).join("\n");
      const reachesSession = sessionAccess.test(window);
      if (!fileLooksAuthed && !reachesSession) continue;
      let label = "publicProcedure used in router that looks authenticated";
      if (reachesSession) label += " (handler reads ctx.session/user) \u2014 verify intent";
      else label += " \u2014 verify intent";
      matches.push({
        vulnSlug: "trpc-public-procedure",
        lineNumbers: [i + 1],
        snippet: lines.slice(start, Math.min(lines.length, i + 4)).join("\n"),
        matchedPattern: label
      });
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/unix-socket-listener.ts
var unixSocketListenerMatcher = {
  noiseTier: "precise",
  slug: "unix-socket-listener",
  description: "Unix-socket / vsock listener setup (incl. umask + auto-recreate patterns)",
  filePatterns: ["**/*.go"],
  requires: { tech: ["go"] },
  examples: [
    `l, err := net.Listen("unix", "/var/run/app.sock")`,
    `l, err := net.Listen("unixpacket", path)`,
    `l, err := net.ListenUnix("unix", addr)`,
    `l, err := vsock.Listen(uint32(port), nil)`,
    `conn, err := vsock.Dial(cid, port, nil)`,
    `pc, err := net.ListenPacket("unix", path)`,
    `oldMask := syscall.Umask(0177)`,
    `os.Remove(socketPath)`,
    `watcher.Add("/var/run")`
  ],
  match(content, filePath) {
    if (/_test\.go$/.test(filePath)) return [];
    if (/(?:^|\/)gen\//.test(filePath)) return [];
    const lines = content.split("\n");
    const hitLines = [];
    const labels = /* @__PURE__ */ new Set();
    let firstContext;
    const PATTERNS2 = [
      { regex: /\bnet\.Listen\s*\(\s*"unix(?:packet|gram)?"/, label: "net.Listen unix socket" },
      { regex: /\bnet\.ListenUnix\s*\(/, label: "net.ListenUnix" },
      { regex: /\bvsock\.(?:Listen|Dial|ListenContextID)\s*\(/, label: "vsock listener/dial" },
      { regex: /\bnet\.ListenPacket\s*\(\s*"unix/, label: "net.ListenPacket unix" },
      { regex: /\bsyscall\.Umask\s*\(/, label: "syscall.Umask (socket perm)" },
      { regex: /\bos\.(?:Remove|RemoveAll)\s*\([^)]*[Ss]ocket/, label: "socket file removal" },
      { regex: /\bfsnotify\.\w+|inotify\.|watcher\.Add\s*\(/, label: "filesystem watcher" }
    ];
    for (let i = 0; i < lines.length; i++) {
      for (const { regex, label } of PATTERNS2) {
        if (regex.test(lines[i])) {
          hitLines.push(i + 1);
          labels.add(label);
          if (firstContext === void 0) {
            const s = Math.max(0, i - 2);
            const e = Math.min(lines.length, i + 3);
            firstContext = lines.slice(s, e).join("\n");
          }
          break;
        }
      }
    }
    if (hitLines.length === 0) return [];
    const match = {
      vulnSlug: "unix-socket-listener",
      lineNumbers: hitLines,
      snippet: firstContext ?? "",
      matchedPattern: Array.from(labels).slice(0, 4).join(", ")
    };
    return [match];
  }
};

// vendor/deepsec-scanner/matchers/unsafe-deserialization.ts
var unsafeDeserializationMatcher = {
  noiseTier: "normal",
  slug: "unsafe-deserialization",
  description: "JSON.parse on user input without schema validation, or unsafe eval of parsed data",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const data = JSON.parse(req.body);`,
    `const x = JSON.parse(request.body);`,
    `const cfg = JSON.parse(body.config);`,
    `const out = JSON.parse(params.payload);`,
    `const filter = JSON.parse(query.filter);`,
    `const payload = JSON.parse(await req.text());`,
    `const data = JSON.parse(await request.text());`,
    `eval(JSON.parse(input));`,
    `const fn = new Function(JSON.parse(spec));`,
    `const config = yaml.load(rawYaml);`,
    `const cfg = safeLoad(input);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    return regexMatcher(
      "unsafe-deserialization",
      [
        {
          regex: /JSON\.parse\s*\(\s*(req\.|request\.|body\.|params\.|query\.)/,
          label: "JSON.parse of request input (verify schema validation)"
        },
        {
          regex: /JSON\.parse\s*\(\s*await\s+(req|request)\.text\(\)/,
          label: "JSON.parse of raw request text"
        },
        { regex: /eval\s*\(\s*JSON\.parse/, label: "eval of parsed JSON" },
        { regex: /new\s+Function\s*\(\s*JSON\.parse/, label: "new Function from parsed JSON" },
        {
          regex: /yaml\.load\s*\(|safeLoad\s*\(/,
          label: "YAML deserialization (verify safe mode)"
        }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/unsafe-redirect.ts
var unsafeRedirectMatcher = {
  noiseTier: "normal",
  slug: "unsafe-redirect",
  description: "Redirects that may bypass validNextRedirect() \u2014 open redirect risk",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `redirect(req.body.next);`,
    `redirect(query.target);`,
    `redirect(searchParams.get("u"));`,
    `redirect(params.next);`,
    "redirect(`/${req.body.path}`);",
    `NextResponse.redirect(new URL(target, base));`,
    `// x-app-redirect-uri header
redirect(target);`,
    `// returnUrl from query
redirect(target);`,
    `// returnTo param
redirect(t);`,
    `// redirectUrl from body
redirect(t);`,
    `// redirect.uri from header
redirect(t);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const hasRedirect = /redirect\s*\(|NextResponse\.redirect|router\.push|router\.replace|window\.location/i.test(
      content
    );
    if (!hasRedirect) return [];
    const hasValidation = /validNextRedirect/.test(content);
    const patterns = [
      {
        regex: /redirect\s*\(\s*(req\.|request\.|params\.|query\.|searchParams|body\.)/,
        label: "redirect() with request-derived URL"
      },
      {
        regex: /redirect\s*\(\s*`[^`]*\$\{/,
        label: "redirect() with interpolated URL"
      },
      {
        regex: /NextResponse\.redirect\s*\(\s*new\s+URL\s*\(/,
        label: "NextResponse.redirect with dynamic URL"
      },
      {
        regex: /x-app-redirect-uri|redirect.uri|redirectUrl|returnUrl|returnTo/i,
        label: "Redirect URL from header/param"
      }
    ];
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "unsafe-redirect",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: hasValidation ? `${label} (validNextRedirect in scope \u2014 verify usage)` : `${label} (NO validNextRedirect \u2014 investigate)`
          });
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/untrusted-redirect-following.ts
var untrustedRedirectFollowingMatcher = {
  noiseTier: "normal",
  slug: "untrusted-redirect-following",
  description: "Server-side fetch follows redirects \u2014 SSRF bypass risk if URL is caller-influenced",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `await fetch(targetUrl, { redirect: "follow" });`,
    `await fetch(callbackUrl);`,
    `const res = await fetch(redirectUrl);`,
    `const r = await fetch(webhookUrl);`,
    `await axios.get(companyUrl);`,
    `await axios.post(websiteUrl, payload);`,
    `await got(domainUrl);`,
    `await got(imageUrl);
got.get(imageUrl);`,
    `await fetch(fetchUrl, { method: "GET" });`,
    `await fetch(returnTo, { method: "GET" });`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    if (/\.client\.(ts|tsx|js|mjs)$/.test(filePath)) return [];
    const HAS_OUTBOUND = /\bfetch\s*\(|\baxios\b|\bgot\s*\(|\bundici\b|\bnode-fetch\b|\bphin\b/;
    if (!HAS_OUTBOUND.test(content)) return [];
    const URL_VAR = /\b(?:url|targetUrl|callbackUrl|redirectUrl|webhookUrl|companyUrl|websiteUrl|domainUrl|imageUrl|fetchUrl|next|return_to|returnTo|destination|location)\b/;
    const lines = content.split("\n");
    const matches = [];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/\bredirect\s*:\s*["']follow["']/.test(line)) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "untrusted-redirect-following",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "explicit redirect: 'follow' \u2014 verify URL is allowlisted"
        });
        continue;
      }
      const m = line.match(
        /\b(?:fetch|axios\.\s*(?:get|post|put|delete|head)|got|got\.\s*(?:get|post))\s*\(\s*([^,)]+)/
      );
      if (m && URL_VAR.test(m[1])) {
        const window = lines.slice(i, Math.min(lines.length, i + 5)).join("\n");
        if (/\bredirect\s*:\s*["'](?:manual|error)["']/.test(window)) continue;
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "untrusted-redirect-following",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: `fetch(${m[1].slice(0, 40).trim()}) \u2014 default redirect: follow + caller-style URL`
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/unverified-lookup.ts
var unverifiedLookupMatcher = {
  noiseTier: "precise",
  slug: "unverified-lookup",
  description: "DB lookups by ID without a nearby ownership check \u2014 cross-tenant risk",
  filePatterns: [
    "**/services/**/endpoints/**/*.ts",
    "**/services/**/endpoint/**/*.ts",
    "**/services/**/src/index.ts",
    "**/apps/**/route.ts",
    "**/apps/**/route.*.ts",
    "**/app/api/**/*.ts",
    "**/src/**/*.ts"
  ],
  examples: [
    `const project = await getProjectById(projectId);
return Response.json(project);`,
    `const team = await getTeamById(teamId);
return Response.json(team);`,
    `const user = await getUserById(userId);
return Response.json(user);`,
    `const deployment = await getDeploymentById(id);
return Response.json(deployment);`,
    `const installation = await getInstallationById(id);
return Response.json(installation);`,
    `const data = await db.findUnique({ where: { id } });
return Response.json(data);`,
    `const data = await db.findFirst({ where: { id } });
return Response.json(data);`,
    `const r = await repo.findOneById(id);
return Response.json(r);`,
    `const r = await repo.findByUid(uid);
return Response.json(r);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const lookupPatterns = [
      /get\w+By(Id|Uid)\s*\(/,
      /find(One)?By(Id|Uid)\s*\(/,
      /getTeamById\s*\(/,
      /getUserById\s*\(/,
      /getProjectById\s*\(/,
      /getDeploymentById\s*\(/,
      /getInstallationById\s*\(/,
      /\.findUnique\s*\(/,
      /\.findFirst\s*\(/
    ];
    const ownershipChecks = [
      /===?\s*auth\.|auth\.\w+\s*===?/,
      /ownerId\s*===?|===?\s*ownerId/,
      /\.teamId\s*===?|===?\s*\.teamId/,
      /\.userId\s*===?|===?\s*\.userId/,
      /throw.*403|throw.*Forbidden|throw.*Unauthorized/,
      /auth\.can\s*\(/,
      /if\s*\(\s*!\s*(installation|project|team|deployment)\./
    ];
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isLookup = lookupPatterns.some((p) => p.test(line));
      if (!isLookup) continue;
      const window = lines.slice(i, Math.min(lines.length, i + 15)).join("\n");
      const hasOwnershipCheck = ownershipChecks.some((p) => p.test(window));
      if (!hasOwnershipCheck) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "unverified-lookup",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "DB lookup by ID without ownership check in next 15 lines"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/url-regex-validation.ts
var urlRegexValidationMatcher = {
  noiseTier: "precise",
  slug: "url-regex-validation",
  description: "Regex-based URL/hostname validation with .+ or .* patterns \u2014 bypassable",
  filePatterns: ["**/*.{ts,tsx,js,jsx}"],
  examples: [
    `const re = new RegExp("https?://.+\\\\.example\\\\.com");
if (re.test(url)) ok();`,
    `if (/^https?:\\/\\/.+\\.trusted\\.com/.test(url)) ok();`,
    `const ok = /https?:.+\\.example\\.com/.test(url);`,
    `const re = /https?:.*\\.foo\\.com/;
if (re.test(url)) good();`,
    `const u = new URL(req.query.target);`,
    `const u = new URL(params.url);`,
    `const u = new URL(body.callbackUrl);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const hasUrlRegex = /https?.*\.\+|https?.*\.\*/.test(line) && /RegExp|\/.*\/|\.test|\.match/.test(line) || /new RegExp\s*\(.*https?/.test(line) || // Regex literal with URL + .+
      /\/\^?https?:.*\.\+.*\//.test(line);
      const hasUncheckedUrl = /new\s+URL\s*\(/.test(line) && !/\.hostname\s*===|\.host\s*===/.test(
        lines.slice(i, Math.min(lines.length, i + 5)).join("\n")
      );
      if (hasUrlRegex) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "url-regex-validation",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "URL validation regex with greedy wildcard (.+ or .*) \u2014 may be bypassable"
        });
      } else if (hasUncheckedUrl && /req\.|params\.|query\.|body\.|parsed\./.test(line)) {
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 3);
        matches.push({
          vulnSlug: "url-regex-validation",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: "new URL() from request input without hostname validation"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/webhook-handler.ts
var webhookHandlerMatcher = {
  noiseTier: "precise",
  slug: "webhook-handler",
  description: "Webhook endpoints that receive external payloads \u2014 must verify signatures",
  filePatterns: [
    "**/*webhook*/**/*.{ts,tsx,js,jsx}",
    "**/*hook*/**/route.{ts,js}",
    "**/api/**/route.{ts,js}",
    "**/services/**/src/**/*.ts"
  ],
  examples: [
    `export async function POST(req) { /* webhook */ return ok(); }`,
    `export const handler = async (req) => { /* webhook */ };`,
    `// webhook route
export function POST(req) { return ok(); }`,
    `export async function webhookHandler(req) { return ok(); }`,
    `export const webhookRoute = (req) => process(req);`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\./i.test(filePath)) return [];
    const matches = [];
    const lines = content.split("\n");
    const isWebhook = /webhook/i.test(filePath) || /webhook/i.test(content) || /hook.*route/i.test(filePath);
    if (!isWebhook) return [];
    const patterns = [
      { regex: /webhook/i, label: "Webhook handler (verify signature validation)" }
    ];
    const hasVerification = /verifySignature|verify.*signature|hmac|createHmac|timingSafeEqual/i.test(content);
    for (const { regex, label } of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (regex.test(lines[i]) && /export|handler|POST|route/i.test(lines[i])) {
          const start = Math.max(0, i - 2);
          const end = Math.min(lines.length, i + 3);
          matches.push({
            vulnSlug: "webhook-handler",
            lineNumbers: [i + 1],
            snippet: lines.slice(start, end).join("\n"),
            matchedPattern: hasVerification ? `${label} \u2014 has signature verification` : `${label} \u2014 NO signature verification found`
          });
          break;
        }
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/xss.ts
var xssMatcher = {
  noiseTier: "normal",
  slug: "xss",
  description: "Unsafe innerHTML, dangerouslySetInnerHTML, template injection patterns",
  filePatterns: ["**/*.{ts,tsx,js,jsx,html,ejs,hbs}"],
  examples: [
    `<div dangerouslySetInnerHTML={{ __html: x }} />`,
    `el.innerHTML = userInput;`,
    `node.outerHTML = data;`,
    `document.write(payload);`,
    `const html = \`<p>\${value}</p>\`;`,
    `<div v-html="raw" />`,
    `<span [innerHTML]="bound"></span>`
  ],
  match(content, _filePath) {
    return regexMatcher(
      "xss",
      [
        { regex: /dangerouslySetInnerHTML/, label: "dangerouslySetInnerHTML" },
        { regex: /\.innerHTML\s*=/, label: "innerHTML assignment" },
        { regex: /\.outerHTML\s*=/, label: "outerHTML assignment" },
        { regex: /document\.write\s*\(/, label: "document.write" },
        // Bounded `.{0,120}` between `}` and the tag avoids the O(n²)
        // backtrack the unbounded version exhibited on long minified
        // lines — see commit log for the regression that motivated this.
        {
          regex: /\$\{[^}]{0,200}\}.{0,120}<\/?\w+>|<\w+[^>]{0,200}\$\{/,
          label: "template literal in HTML"
        },
        { regex: /v-html\s*=/, label: "Vue v-html directive" },
        { regex: /\[innerHTML\]\s*=/, label: "Angular innerHTML binding" }
      ],
      content
    );
  }
};

// vendor/deepsec-scanner/matchers/zod-passthrough-mass-assignment.ts
var zodPassthroughMassAssignmentMatcher = {
  noiseTier: "normal",
  slug: "zod-passthrough-mass-assignment",
  description: "Zod schema with .passthrough() \u2014 verify parsed output isn't passed to DB write unfiltered",
  filePatterns: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.mjs"],
  examples: [
    `import { z } from "zod";
const schema = z.object({ name: z.string() }).passthrough();`,
    `import { z } from "zod";
const input = z.object({ id: z.string() }).passthrough();
const parsed = input.parse(req.body);
await db.insert(users).values(parsed);`,
    `import { z } from "zod";
const schema = z.object({}).passthrough();
await db.update(users).set(parsed);`,
    `import { z } from "zod";
export const userInput = z.object({ name: z.string() }).strict().passthrough();`,
    `import { z } from "zod";
const s = z
  .object({ name: z.string() })
  .passthrough();`
  ],
  match(content, filePath) {
    if (/\.(test|spec)\.(ts|tsx|js|jsx|mjs|cjs)$/.test(filePath)) return [];
    if (/\.d\.ts$/.test(filePath)) return [];
    if (/node_modules/.test(filePath)) return [];
    const HAS_ZOD = /\bfrom\s+["']zod[^"']*["']|\bz\.\s*object\s*\(/;
    if (!HAS_ZOD.test(content)) return [];
    if (!/\.\s*passthrough\s*\(/.test(content)) return [];
    const lines = content.split("\n");
    const matches = [];
    const HAS_DB_WRITE = /\.\s*insert\s*\([^)]+\)\.\s*values\s*\(|\.\s*update\s*\([^)]+\)\.\s*set\s*\(/;
    const writeContext = HAS_DB_WRITE.test(content);
    for (let i = 0; i < lines.length; i++) {
      if (/\.\s*passthrough\s*\(/.test(lines[i])) {
        const start = Math.max(0, i - 2);
        const end = Math.min(lines.length, i + 4);
        matches.push({
          vulnSlug: "zod-passthrough-mass-assignment",
          lineNumbers: [i + 1],
          snippet: lines.slice(start, end).join("\n"),
          matchedPattern: writeContext ? ".passthrough() in file with DB insert/update \u2014 mass-assignment risk" : ".passthrough() \u2014 verify parsed output trust boundary"
        });
      }
    }
    return matches;
  }
};

// vendor/deepsec-scanner/matchers/index.ts
function createDefaultRegistry() {
  const registry = new MatcherRegistry();
  registry.register(authBypassMatcher);
  registry.register(missingAuthMatcher);
  registry.register(xssMatcher);
  registry.register(rceMatcher);
  registry.register(sqlInjectionMatcher);
  registry.register(ssrfMatcher);
  registry.register(pathTraversalMatcher);
  registry.register(secretsExposureMatcher);
  registry.register(insecureCryptoMatcher);
  registry.register(openRedirectMatcher);
  registry.register(publicEndpointMatcher);
  registry.register(serviceEntryPointMatcher);
  registry.register(webhookHandlerMatcher);
  registry.register(iamPermissionsMatcher);
  registry.register(serverActionMatcher);
  registry.register(unsafeRedirectMatcher);
  registry.register(dangerousHtmlMatcher);
  registry.register(jwtHandlingMatcher);
  registry.register(envExposureMatcher);
  registry.register(rateLimitBypassMatcher);
  registry.register(crossTenantIdMatcher);
  registry.register(secretInFallbackMatcher);
  registry.register(secretInLogMatcher);
  registry.register(urlRegexValidationMatcher);
  registry.register(gitProviderUrlInjectionMatcher);
  registry.register(cronSecretCheckMatcher);
  registry.register(useServerExportMatcher);
  registry.register(nextjsMiddlewareOnlyAuthMatcher);
  registry.register(luaStringConcatUrlMatcher);
  registry.register(luaNgxExecMatcher);
  registry.register(luaSharedDictPoisoningMatcher);
  registry.register(luaRegexBypassMatcher);
  registry.register(luaCryptoWeaknessMatcher);
  registry.register(goHttpHandlerMatcher);
  registry.register(goSsrfMatcher);
  registry.register(goCommandInjectionMatcher);
  registry.register(cacheKeyPoisoningMatcher);
  registry.register(secretEnvVarMatcher);
  registry.register(unverifiedLookupMatcher);
  registry.register(catchAllRouteAuthMatcher);
  registry.register(serverActionNoAuthMatcher);
  registry.register(oauthFlowMatcher);
  registry.register(securityBehindFlagMatcher);
  registry.register(pageDataFetchMatcher);
  registry.register(spreadOperatorInjectionMatcher);
  registry.register(nonAtomicOperationMatcher);
  registry.register(debugEndpointMatcher);
  registry.register(postmessageOriginMatcher);
  registry.register(algorithmConfusionMatcher);
  registry.register(objectInjectionMatcher);
  registry.register(envVarAsBoolMatcher);
  registry.register(responseHeaderLeakMatcher);
  registry.register(corsWildcardMatcher);
  registry.register(unsafeDeserializationMatcher);
  registry.register(pageWithoutAuthFetchMatcher);
  registry.register(unsafeJsonInHtmlMatcher);
  registry.register(allRouteHandlersMatcher);
  registry.register(allServerActionsMatcher);
  registry.register(nextjsMiddlewareMatcher);
  registry.register(catchallRouterMatcher);
  registry.register(agentToolDefinitionMatcher);
  registry.register(devAuthBypassMatcher);
  registry.register(streamingEndpointMatcher);
  registry.register(expensiveApiAbuseMatcher);
  registry.register(processEnvAccessMatcher);
  registry.register(missingAwaitMatcher);
  registry.register(sensitiveDataInTracesMatcher);
  registry.register(cacheKeyScopeMatcher);
  registry.register(nonAtomicReadDeleteMatcher);
  registry.register(testHeaderBypassMatcher);
  registry.register(eventHandlerMismatchMatcher);
  registry.register(errorMessageLeakMatcher);
  registry.register(dockerfileFromMutableTagMatcher);
  registry.register(dockerfileCurlPipeUnverifiedMatcher);
  registry.register(dockerfileRunAsRootMatcher);
  registry.register(cryptoUsageMatcher);
  registry.register(secretsPlaintextExposureMatcher);
  registry.register(k8sSecretReferenceMatcher);
  registry.register(k8sSecretsInitContainerMatcher);
  registry.register(protoRpcSurfaceMatcher);
  registry.register(connectrpcHandlerImplMatcher);
  registry.register(unixSocketListenerMatcher);
  registry.register(sandboxRuntimeScriptMatcher);
  registry.register(goEmbedAssetMatcher);
  registry.register(githubWorkflowSecurityMatcher);
  registry.register(tfIamWildcardMatcher);
  registry.register(tfPublicIngressMatcher);
  registry.register(tfEncryptionMissingMatcher);
  registry.register(tfSecretInDataMatcher);
  registry.register(tfModuleUnpinnedMatcher);
  registry.register(tfIacSurfaceMatcher);
  registry.register(frameworkUntrustedFetchMatcher);
  registry.register(frameworkInternalHeaderMatcher);
  registry.register(frameworkServerActionMatcher);
  registry.register(frameworkImageOptimizerMatcher);
  registry.register(frameworkEdgeSandboxMatcher);
  registry.register(agenticUntrustedPromptInputMatcher);
  registry.register(drizzleRawSqlMatcher);
  registry.register(soqlInjectionMatcher);
  registry.register(snowflakeBigquerySqlMatcher);
  registry.register(mcpToolHandlerMatcher);
  registry.register(slackSigningVerificationMatcher);
  registry.register(drizzleMassAssignmentMatcher);
  registry.register(sessionCookieConfigMatcher);
  registry.register(zodPassthroughMassAssignmentMatcher);
  registry.register(untrustedRedirectFollowingMatcher);
  registry.register(agentLoopNoCapMatcher);
  registry.register(promptLeaksSystemPromptMatcher);
  registry.register(fsWriteSymlinkBoundaryMatcher);
  registry.register(prismaRawSqlMatcher);
  registry.register(trpcPublicProcedureMatcher);
  registry.register(jsExpressRouteMatcher);
  registry.register(jsFastifyRouteMatcher);
  registry.register(jsNestjsControllerMatcher);
  registry.register(jsHonoRouteMatcher);
  registry.register(jsKoaRouteMatcher);
  registry.register(jsHapiRouteMatcher);
  registry.register(jsRemixRouteMatcher);
  registry.register(jsSveltekitRouteMatcher);
  registry.register(jsNuxtRouteMatcher);
  registry.register(jsAstroEndpointMatcher);
  registry.register(jsSolidstartActionMatcher);
  registry.register(jsGraphqlResolverMatcher);
  registry.register(jsSocketioHandlerMatcher);
  registry.register(jsBullmqProcessorMatcher);
  registry.register(jsBunServeMatcher);
  registry.register(jsDenoRouteMatcher);
  registry.register(jsWorkersFetchMatcher);
  registry.register(phpLaravelRouteMatcher);
  registry.register(phpSymfonyControllerMatcher);
  registry.register(phpSlimRouteMatcher);
  registry.register(phpYiiControllerMatcher);
  registry.register(phpCakephpControllerMatcher);
  registry.register(phpCodeigniterControllerMatcher);
  registry.register(phpWordpressRestMatcher);
  registry.register(phpDrupalControllerMatcher);
  registry.register(phpMagentoControllerMatcher);
  registry.register(pyDjangoViewMatcher);
  registry.register(pyFastapiRouteMatcher);
  registry.register(pyFlaskRouteMatcher);
  registry.register(pyStarletteRouteMatcher);
  registry.register(pyAiohttpRouteMatcher);
  registry.register(pyTornadoHandlerMatcher);
  registry.register(pySanicRouteMatcher);
  registry.register(pyBottleRouteMatcher);
  registry.register(pyFalconResourceMatcher);
  registry.register(pyCeleryTaskMatcher);
  registry.register(pyAirflowDagMatcher);
  registry.register(rbRailsControllerMatcher);
  registry.register(rbSinatraRouteMatcher);
  registry.register(rbGrapeEndpointMatcher);
  registry.register(rbHanamiActionMatcher);
  registry.register(rbRodaRouteMatcher);
  registry.register(goGinRouteMatcher);
  registry.register(goEchoRouteMatcher);
  registry.register(goFiberRouteMatcher);
  registry.register(goChiRouteMatcher);
  registry.register(goGorillaRouteMatcher);
  registry.register(goBuffaloRouteMatcher);
  registry.register(goCobraCommandMatcher);
  registry.register(rsActixRouteMatcher);
  registry.register(rsAxumRouteMatcher);
  registry.register(rsRocketRouteMatcher);
  registry.register(rsWarpFilterMatcher);
  registry.register(rsTideRouteMatcher);
  registry.register(rsPoemRouteMatcher);
  registry.register(rsTonicGrpcMatcher);
  registry.register(rsLambdaRuntimeMatcher);
  registry.register(jvmSpringControllerMatcher);
  registry.register(jvmKtorRouteMatcher);
  registry.register(jvmMicronautControllerMatcher);
  registry.register(jvmJaxrsResourceMatcher);
  registry.register(dotnetAspnetControllerMatcher);
  registry.register(dotnetMinimalApiMatcher);
  registry.register(dotnetRazorPagesMatcher);
  registry.register(dotnetAzureFunctionMatcher);
  registry.register(exPhoenixControllerMatcher);
  registry.register(crKemalRouteMatcher);
  registry.register(cljRingHandlerMatcher);
  registry.register(erlCowboyHandlerMatcher);
  registry.register(swiftVaporRouteMatcher);
  registry.register(dartShelfHandlerMatcher);
  registry.register(apexRestResourceMatcher);
  registry.register(lambdaAwsHandlerMatcher);
  registry.register(gcpCloudFunctionMatcher);
  registry.register(azureFunctionHandlerMatcher);
  registry.register(androidManifestExportMatcher);
  registry.register(iosUrlSchemeMatcher);
  registry.register(jsSqlRawMatcher);
  registry.register(jsNosqlInjectionMatcher);
  registry.register(pySqlRawMatcher);
  registry.register(pyNosqlInjectionMatcher);
  registry.register(jvmSqlRawMatcher);
  registry.register(phpSqlRawMatcher);
  registry.register(rbSqlRawMatcher);
  registry.register(goSqlRawMatcher);
  registry.register(rsSqlRawMatcher);
  registry.register(dotnetSqlRawMatcher);
  return registry;
}
export {
  createDefaultRegistry
};
