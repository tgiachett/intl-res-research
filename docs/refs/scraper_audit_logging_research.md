Great question. You’ve got three good levers here: (A) make the *only* path to the network go through your own tool that writes to SQLite, (B) plug that tool into Claude via MCP (and optionally Copilot via Extensions), and (C) add lightweight “observability” so you can see every call, success, failure, and artifact.

Here’s a concrete plan with options.

# 1) Route all scraping through *your* MCP server (Claude-friendly)

**Why this works:** Claude (Claude Code / Claude Desktop) natively speaks the Model Context Protocol (MCP). If the only “web” capability you expose to it is an MCP tool you control, then every fetch/search/scrape will go through your server—and you can log to SQLite automatically on each call. ([Model Context Protocol][1])

**How to do it**

* Build a tiny MCP server (Node or Python) that exposes tools like `search_web`, `fetch_url`, `playwright_scrape`. In each handler, insert a row into your SQLite tables before/after the action. The official docs show a minimal server with multiple tools and how to connect it to Claude Desktop/Claude Code. ([Model Context Protocol][2])
* Drop in an existing MCP server for search/scraping (e.g., Brave Search MCP, Playwright MCP) and **wrap** it—either by forking or by writing a proxy server—to add your logging middleware. Examples and registries: Brave Search API + community MCP servers, Playwright MCP examples. ([Brave][3])
* Install/enable your local MCP server in Claude Desktop/Code (settings → extensions; Claude provides official steps). Once installed, you can tell Claude “all web access must use the ‘webtools’ MCP.” But even if it *forgets*, it literally can’t do anything else if your MCP is the only available capability for web access. ([Claude Help Center][4])

**Schema sketch (SQLite)**

```sql
CREATE TABLE job_run (
  id INTEGER PRIMARY KEY,
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  user_task TEXT,           -- natural-language task
  agent_session_id TEXT
);

CREATE TABLE tool_call (
  id INTEGER PRIMARY KEY,
  job_run_id INTEGER REFERENCES job_run(id),
  tool_name TEXT,
  args_json TEXT,           -- what the LLM asked for
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  status TEXT CHECK(status IN ('ok','error')),
  error_msg TEXT
);

CREATE TABLE source (
  id INTEGER PRIMARY KEY,
  tool_call_id INTEGER REFERENCES tool_call(id),
  url TEXT,
  title TEXT,
  http_status INTEGER,
  mime_type TEXT,
  found_at TEXT DEFAULT CURRENT_TIMESTAMP,
  dedupe_hash TEXT          -- e.g., SHA256 of normalized URL/body
);

CREATE TABLE artifact (
  id INTEGER PRIMARY KEY,
  tool_call_id INTEGER REFERENCES tool_call(id),
  type TEXT,                -- 'html','pdf','screenshot','json','text'
  path TEXT,                -- local path if persisted
  bytes INTEGER,
  sha256 TEXT
);
```

**Tool middleware (Node/TypeScript MCP sketch)**

```ts
// inside your MCP server's tool handler
async function withLogging<TArgs, TResult>(
  toolName: string,
  args: TArgs,
  fn: () => Promise<TResult>
): Promise<TResult> {
  const callId = await db.insertToolCall(toolName, JSON.stringify(args));
  try {
    const result = await fn();
    await db.finishToolCall(callId, 'ok', null);
    return result;
  } catch (e:any) {
    await db.finishToolCall(callId, 'error', String(e?.message ?? e));
    throw e;
  }
}

// example tool
tools.register('fetch_url', async ({ url }) => withLogging('fetch_url', { url }, async () => {
  const res = await fetch(url, { headers: {/* … */} });
  const body = await res.text();
  const sourceId = await db.insertSource(callId, url, /*title*/null, res.status, res.headers.get('content-type')||null);
  // optional: persist body/artifacts, compute hashes
  return { status: res.status, body }; // return to client (Claude)
}));
```

**Why MCP here instead of “just prompts”?** You *can* remind the model in a system prompt (“All web access must use `fetch_url`”), but MCP enforces it at the capability boundary. Claude already advertises MCP as the standard way to connect tools, and there are ready-made servers you can adopt or fork (Brave, Playwright). ([Anthropic][5])

# 2) “Hooks” in GitHub Copilot: use **Copilot Extensions** (actions)

Copilot doesn’t speak MCP natively, but it supports **Copilot Extensions** whose “actions” Copilot Chat can execute. You can publish an extension that exposes `search_web`, `fetch_url`, etc. Those actions call your backend—which performs the scrape and writes to SQLite. In practice, this is your “hook.” ([GitHub Docs][6])

Notes:

* You *can* strongly instruct Copilot (“When asked to browse, always use the **Subrosa Web** extension.”). It still relies on the agent to select the action, but with a single installed path for web access plus a good description, it’s reliable.
* If you need multi-model or Claude-powered experiences inside GitHub, Copilot is increasingly multi-model; that doesn’t change the extension mechanism, but it’s useful context. ([The Verge][7])

# 3) Brave, Playwright, and “deep research” servers you can adopt

* **Brave Search API** is a clean search back-end you can front through MCP and log locally. Community MCP servers combine search with browser automation/content extraction (Puppeteer/Playwright). Fork and add your SQLite logging. ([Brave][3])
* **Playwright MCP** servers expose browser actions (navigate, click, extract) as tools. Again, wrap/extend with your logging middleware. ([Execute Automation][8])

# 4) Observability (optional but recommended)

SQLite audit tables are great for provenance. Add **OpenTelemetry** spans for each tool call and page fetch—so you get timelines, error rates, token/cost metrics (if you also instrument LLM calls), and dashboards in Grafana/Datadog/etc. Guides and kits exist; they’re drop-in. ([OpenTelemetry][9])

* If you want an off-the-shelf LLM observability layer (traces, evals, dashboards), see Langfuse, Braintrust, Traceloop/OpenLLMetry, Middleware. You can run these *in addition to* your SQLite ledger. ([Langfuse][10])

# 5) If you *really* want “just instructions”

You can embed a short, strict system policy in Claude/Copilot that says:

> “All web search, fetching, or scraping **must** use the `webtools` interface. Do **not** browse via any other means. After each call, record `source` and `artifact` rows. If a tool fails, record an `error` and retry up to N times.”

This helps—but enforcement comes from only exposing the tools you want (MCP/Extensions), not from the text itself.

# 6) Minimal end-to-end: what to build this week

1. **Spin up an MCP server** with `search_web`, `fetch_url`, `scrape_playwright` tools; add the SQLite middleware + schema above; install it in Claude Desktop/Code. ([Model Context Protocol][2])
2. **(Optional) Fork a Brave/Playwright MCP** and add your logger wrapper instead of writing scraping from scratch. ([GitHub][11])
3. **Author a Copilot Extension** that exposes identical actions to your MCP tools, pointing to the same backend. Now both Claude and Copilot go through your logger. ([GitHub Docs][6])
4. **Add OpenTelemetry spans** per tool call and export to your preferred backend. Keep SQLite as your ground-truth ledger. ([OpenTelemetry][9])

---

## TL;DR on “hooks”

* **Claude (Code/Desktop):** Yes—use **MCP servers**. That *is* the hook, and it’s first-class. Build or fork a server that logs to SQLite and expose only that path for web access. ([Model Context Protocol][1])
* **GitHub Copilot:** Use **Copilot Extensions** to expose actions; your action handler does the scrape and the SQLite writes. This is the supported way to add behaviors. ([GitHub Docs][6])
* **“Just prompts”:** Helpful, but not sufficient by themselves. Combine with capability control (MCP/Extensions) to *guarantee* your SQLite gets updated.

If you want, I can sketch a working MCP server (Node or Python) that wraps Brave search + Playwright and writes every result and artifact into your `sources`, `tool_call`, and `artifact` tables—ready to drop into Claude Code.

[1]: https://modelcontextprotocol.io/?utm_source=chatgpt.com "What is the Model Context Protocol (MCP)? - Model Context ..."
[2]: https://modelcontextprotocol.io/docs/develop/build-server?utm_source=chatgpt.com "Build an MCP server"
[3]: https://brave.com/search/api/?utm_source=chatgpt.com "Brave Search API"
[4]: https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop?utm_source=chatgpt.com "Getting Started with Local MCP Servers on Claude Desktop"
[5]: https://www.anthropic.com/news/model-context-protocol?utm_source=chatgpt.com "Introducing the Model Context Protocol"
[6]: https://docs.github.com/copilot/building-copilot-extensions/about-building-copilot-extensions?utm_source=chatgpt.com "About building GitHub Copilot Extensions"
[7]: https://www.theverge.com/2024/10/29/24282544/github-copilot-multi-model-anthropic-google-open-ai-github-spark-announcement?utm_source=chatgpt.com "GitHub Copilot will support models from Anthropic, Google, and OpenAI"
[8]: https://executeautomation.github.io/mcp-playwright/docs/playwright-web/Examples?utm_source=chatgpt.com "Examples of browser automation | Playwright MCP Server"
[9]: https://opentelemetry.io/docs/concepts/signals/traces/?utm_source=chatgpt.com "Traces"
[10]: https://langfuse.com/blog/2024-10-opentelemetry-for-llm-observability?utm_source=chatgpt.com "OpenTelemetry (OTel) for LLM Observability"
[11]: https://github.com/modelcontextprotocol/servers?utm_source=chatgpt.com "modelcontextprotocol/servers: Model Context Protocol ..."
