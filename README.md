# CopilotKit Vue + Claude Agent SDK (Python) Test Suite

A navigable, working test harness for CopilotKit's **Vue** frontend against a **Claude Agent SDK (Python)** agent. Each Vue doc page is a route that runs that page's own code.

| | |
|---|---|
| **Doc sync date** | Machine-maintained: `doc-snapshot/manifest.json` → `syncedAt` (baseline taken 2026-11-13, 22 pages; the nine Generative UI › Components pages added 2026-11-17, 31 in all). |
| **CopilotKit packages** | `@copilotkit/vue` 1.87.0 · `@copilotkit/core` 1.87.0 · `@copilotkit/runtime` 1.87.0 · `@ag-ui/client` 1.0.2 (`HttpAgent`, the same copy the runtime uses) |
| **Claude** | `claude-agent-sdk` 0.2.170 (bundles the Claude Code CLI it drives) · `ag-ui-claude-sdk` 0.2.4 · `ag-ui-protocol` 1.0.0 · `anthropic` 2.8.0 · `fastapi` 0.162.5 · `uvicorn` 0.54.0 · `python-dotenv` 1.2.4 · Python 3.14 (uv default; the Quickstart pins none) |
| **Frontend** | Vite 8.3 · Vue 3.5 · vue-router 5.5 · TypeScript 6.0 · Tailwind 4.3 (harness chrome only) · zod 3.25.76 · chart.js 4.6.1 · maplibre-gl 5.24.1 (Components pages) |
| **Build status** | No CI. `vite build` ✅. `vue-tsc` reports 9 errors, all in published doc code (§9.10). All 86 URLs (every route and every demo sample, Components pages included) mounted in headless Chrome with **zero console or page errors** (2026-11-17). The chain (runtime → `HttpAgent` → Claude agent → Anthropic) was driven with a **fake** key: the run reached Anthropic and failed only with `Invalid API key`. A captured model request showed a run's frontend tool, its context and its state reaching the model. Tool Rendering was driven end to end in the browser against a local stand-in Anthropic API (2026-11-17): all three renderers drew the page's `get_weather` call (§9.2). **No route has been driven against a live model yet.** |

---

## 2. Overview

The Claude Agent SDK runs Claude as an agent (it drives the Claude Code CLI as a subprocess). CopilotKit reaches it over AG-UI: the `ag-ui-claude-sdk` adapter (`ClaudeAgentAdapter`) turns AG-UI run input into SDK calls and streams AG-UI events back from a FastAPI endpoint, the Copilot Runtime registers an AG-UI `HttpAgent` pointed at it, and `@copilotkit/vue` renders the conversation, tools and state.

This repo turns the Quickstart and the Basics, Generative UI, Interactivity and Agent capabilities sections of the Vue Claude Agent SDK (Python) sidebar (22 pages) into one navigable Vite app. It adds the nine **Generative UI › Components** pages, which aren't under `/vue` and print each sample for React, Angular, React Native and Vue; only their Vue tab is used. Every route mounts the page's code verbatim, bugs included, and shows the exact files that run. Anything the harness added is marked **[harness]** in the file, in a pink **Harness** callout on the notes page, and, for stand-in components, with a **HARNESS STAND-IN** badge on screen.

Tracks: **<https://docs.copilotkit.ai/vue/claude-sdk-python>** and **<https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components>**

---

## 3. Architecture

```
Browser — Vite dev server · localhost:5173
  │  @copilotkit/vue/v2; each /<route>/demo-chat mounts that page's own App.vue
  │  runtime-url="/api/copilotkit…" ──► Vite proxy /api → :8200
  ▼
Node · backend/server.ts · localhost:8200
  │  Vue Quickstart's host: createServer + createCopilotNodeListener({ cors: true })
  │  Claude landing page's runtime: my_agent = new HttpAgent({ url: AGENT_URL })
  │  /api/copilotkit           every doc agent id → my_agent
  │  /api/copilotkit-threads   Intelligence quickstart's runtime (if key set)  [harness: own path]
  │  /api/copilotkit-mcp-apps  MCP Apps' runtime (mcpApps.servers)            [harness: own path]
  │  /api/copilotkit-tool-rendering  Tool Rendering's runtime: default → AGENT_URL/tool-rendering  [harness: own path]
  ▼  AGENT_URL (AG-UI over HTTP)
Python · agent/harness_app.py · localhost:8000   (uv + uvicorn)   [harness: imports main.app unchanged]
  │  /                Claude Agent SDK Quickstart (main.py): ClaudeAgentAdapter(model=ANTHROPIC_MODEL, tools=[], permission_mode="dontAsk")
  │  /tool-rendering  [harness, flagged] same options + mcp_servers {weather: get_weather from weather_tool.snippet.py}
  ▼
Anthropic                                 MCP Apps example server on :3101 (MCP Apps route only)
```

**Three processes.** The agent is **Python** (Claude Agent SDK + FastAPI). The Copilot Runtime is **TypeScript on Node** (`tsx`). The frontend is Vite.

**Where each piece comes from.**
- **The Vue Claude Agent SDK Quickstart redirects to a landing page.** Its `.md` is the Vue (built-in agent) Quickstart, which says to keep its Vue frontend steps and take "the runtime wiring" from your framework's quickstart. So `App.vue`, `main.ts` and the Node host come from the Vue Quickstart.
- **The landing page's only code block is the runtime**, published as a Next.js route: `agents: { my_agent: new HttpAgent({ url: process.env.AGENT_URL! }) }`. It's used verbatim, hosted in the Vue Quickstart's Node listener.
- **The agent** is the Claude Agent SDK Quickstart's (`/claude-sdk-python/quickstart`, linked as the landing page's guide): "Use an existing agent". That's `agent/main.py` verbatim, in a uv project with the Quickstart's `uv add` line.

### Agent ids

The landing page registers only `my_agent`. The Vue samples use `default` (no agent-id), `my-agent`, `sales`, `support`, `researcher`, `workspace` and `writer`. Every id is `my_agent` (`backend/agents.ts`): no page publishes a complete Claude agent of its own (§9.2, §9.3). The Components samples keep `runtime-url="/api/copilotkit"` as published, so they run on `default` too (the ms-agent-py choice; §9.15).

### What the adapter does for you (verified by capturing the model request)

- **Frontend tools:** `ag-ui-claude-sdk` builds an in-process MCP server from the run's `tools` and grants them (`mcp__ag_ui__<name>`), so `useFrontendTool`, `useComponent` and `useHumanInTheLoop` tools reach the Quickstart agent with no change to `main.py`.
- **Context and state:** it appends the run's `context` and current `state` to the system prompt.
- **State writes:** whenever a run carries state, it adds a generic `ag_ui_update_state` tool. The agent *can* write shared state through it if the model chooses to, as one snapshot when the call completes (not streamed). No page's code asks it to (§9.4).
- **Generative UI › Components:** the runtime adds `render_ui` to the run's tools and its guide to the run's context. The model sees the tool as `mcp__ag_ui__render_ui`, and the adapter reports the call back as `render_ui`. The guide lands in the system prompt (captured, §9.15).
- **Not provided:** backend tools and interrupts. The Quickstart agent has none, and no page publishes a usable one.

---

## 4. Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Node.js | **24.12+** (or 22.18+) | `create-vue`'s scaffold requires it. Developed on 24.16. |
| npm | 10+ | Developed on npm 12. |
| uv | 0.11+ | Runs the agent. Developed on 0.11.20. |
| Python | 3.10+ | uv picks one; developed on 3.14. |
| Anthropic API key | — | Required, in `agent/.env`. The agent uses `claude-opus-4-8` as published (`ANTHROPIC_MODEL`). |
| CopilotKit Intelligence key | — | Optional, only for the two Threads routes. |

---

## 5. Setup

```bash
git clone <this-repo> claude-sdk-py && cd claude-sdk-py
cd agent && uv sync && cd ..
cd backend && npm install && cd ..
cd frontend && npm install && cd ..
cp .env.example agent/.env              # set ANTHROPIC_API_KEY
cp .env.example backend/.env            # AGENT_URL is pre-filled
```

| File | Variable | What it does |
|---|---|---|
| `agent/.env` | `ANTHROPIC_API_KEY` | **Required.** Loaded by `main.py` (`load_dotenv()`) for the Claude Agent SDK. |
| `agent/.env` | `ANTHROPIC_MODEL` | The Quickstart's model, `claude-opus-4-8` (also `main.py`'s fallback). |
| `backend/.env` | `AGENT_URL` | **Required.** The landing page's `HttpAgent` URL: `http://localhost:8000/`. |
| `backend/.env` | `CPK_INTELLIGENCE_API_KEY` | Optional. Intelligence for the Threads runtime: `cd backend && npx copilotkit@latest login && npx copilotkit@latest project select`. |
| `backend/.env` | `APP_USER_ID` · `MCP_APPS_URL` · `PORT` · `COPILOTKIT_TELEMETRY_DISABLED` | Optional: fixed local Threads identity (default `local-user`), MCP server URL (default `http://localhost:3101/mcp`), runtime port (default 8200), telemetry opt-out. |

**Ports:** agent **8000** (the Quickstart's `uvicorn` command), runtime **8200**, frontend **5173** (`strictPort`), MCP Apps example **3101**.

---

## 6. Running the project

```bash
# 1 — Claude agent: the Quickstart's app plus /tool-rendering (main.py loads agent/.env itself)
cd agent && uv run uvicorn harness_app:app --reload --host 0.0.0.0 --port 8000
```
Success: `Uvicorn running on http://0.0.0.0:8000`, and `curl http://localhost:8000/health` returns `{"status":"ok"}`. (`uvicorn main:app`, the Quickstart's own command, also works but serves no `/tool-rendering`, so Tool Rendering fails with `HTTP 404`.) **If port 8000 is taken:** use another `--port` and set `AGENT_URL` in `backend/.env` to match.

```bash
# 2 — Copilot Runtime
cd backend && npm run dev
```
Success:
```
Copilot Runtime listening at http://localhost:8200/api/copilotkit
  Agent: http://localhost:8000/
  + /api/copilotkit-threads  (sse)
  + /api/copilotkit-mcp-apps
  + /api/copilotkit-tool-rendering
```

```bash
# 3 — Vue app
cd frontend && npm run dev               # → http://localhost:5173/
```

Open **<http://localhost:5173>**. The landing page's **Connection** panel probes the runtime paths. **MCP Apps route only:** `cd backend && npm run mcp:apps`.

---

## 7. What to expect: walkthrough per section

Each route has a notes page (`/<route>`: notes, Try-it prompts with pass/fail, the exact source, unmounted samples as published, Harness and gap callouts) and a demo (`/<route>/demo-chat`; a **Sample** picker where a page has several samples).

### Getting Started
**`/quickstart`**: **Try:** `Hello! What can you do?` **Pass:** a streamed reply. **Fail:** connection refused or `RUN_ERROR` means the agent isn't running or `AGENT_URL` is wrong. `Invalid API key` means `ANTHROPIC_API_KEY` is missing or wrong in `agent/.env`.

### Basics
**`/prebuilt-components`**, **`/custom-look-and-feel/headless-ui`**, **`/programmatic-control`**: chat against `my_agent`: a streamed reply. Headless UI streams into bare rows. Programmatic Control's default sample adds a chat (harness, on request). **`/custom-look-and-feel/slots`**: nine samples; the **Disclaimer** sample shows no disclaimer (doc bug, §9.11).
**`/prebuilt-components/copilot-threads-drawer`**, **`/headless-threads`**: need `CPK_INTELLIGENCE_API_KEY`. `/api/copilotkit-threads/info` should report `mode: "intelligence"`.
**`/frontend-tools`**: **Try:** `Only show sev1 incidents`. **Pass:** "Current filter" changes to `sev1` and the agent confirms.

### Generative UI
**`/generative-ui/tool-based`**: **Try:** `Show me the weather in Paris`. **Pass:** an inline WeatherCard.
**`/generative-ui/tool-rendering`**: runs on its own runtime path, whose `default` is the page's `get_weather` (§9.2). **Try:** `What's the weather in Paris?` **Pass:** per-tool shows `WeatherToolCard` with `{"city": "Paris", "temperature": 68, …}` (its heading stays empty: the card reads `parameters.city`, but the tool's argument is `location`, a doc bug); zero-config shows a `get_weather` card ending "Done"; catch-all shows the BrandedToolCard stand-in with the result. **Fail:** a prose answer with no tool call means the agent is `main:app`, not `harness_app:app`.
**`/generative-ui/state-rendering`**: **Expected now:** "Idle". Progress appears only if the model chooses the generic state tool (§9.3, §9.4).
**`/generative-ui/mcp-apps`**: needs `npm run mcp:apps`. **Try:** `What time is it on the server?` **Pass:** a tool call, then an inline iframe app.

### Generative UI › Components (Vue tab of the `/claude-sdk-python/generative-ui/components` pages)
All run on `default`, the Quickstart agent, which receives both the `render_ui` tool and its guide (§9.15). Whether the model renders well is not yet checked against a live model.
**`/generative-ui/components`**: the overview's `App.vue` with the standard catalog. It calls `:8200` directly, as published. **Try:** `Compare the Starter, Team, and Enterprise plans in a table`. **Pass:** a table component in the chat.
**`/generative-ui/components/catalogs`**: your own catalog (`ProductGrid`, `ProductCard`). **Try:** `Show me two products`. **Pass:** a grid of product cards.
**`/generative-ui/components/surfaces`**: a page target (`featured`) above the chat; its default content is a **stand-in** `ProductRow`. **Pass:** the agent replaces it with a ProductGrid.
**`/generative-ui/components/standard-catalog`**: the standard catalog, and a sample that replaces `Card` with `MyCard`.
**`/generative-ui/components/state-and-actions`**: `ProductCard` with "Add to cart" (an `onAddToCart` event bound to an `addToCart` function). The handler sample needs `./cart-store`, which isn't published, so clicking takes the card's error path.
**`/generative-ui/components/theming`**: standard components in the amber accent and 10px radius.
**`/generative-ui/components/transports`**: tool, markdown and `agentIds: ['shop']` samples.
**`/generative-ui/components/markdown-mode`**: the guide travels in context, which the adapter appends to the system prompt, so the agent can answer with `a2ui` blocks. The `sendContext: false` sample puts the guide only in forwarded props, which no published Claude Agent SDK code reads; the captured request carried no guide.
**`/generative-ui/components/from-a2ui`**: the "After" provider; `Airport` and `Arrow` are **stand-ins**.

### Interactivity
**`/shared-state`**: **Try:** **Prefer concise answers**, then `Remember that I like tea`. **Pass:** `preferences.tone` appears in the agent state (Inspector › State). Notes fill only if the model uses `ag_ui_update_state` (§9.4).
**`/shared-state/rendering-in-app`**: **Try:** `Rename the project to "Spring release"`. **Pass (if the model uses the generic state tool):** the heading changes. Otherwise it stays "Project launch" (§9.4).
**`/shared-state/streaming`**: **Expected now:** "Waiting for a draft…". At most a whole document appears at once; nothing streams (§9.3).
**`/shared-state/agent-readonly`**: **Try:** `Which workspace am I in?` **Pass:** "northstar".
**`/human-in-the-loop`**: **Try:** `Schedule a meeting about Q3 planning with Dana`. **Pass:** a time-picker card (flagged stand-in); picking a slot resumes the run.
**`/human-in-the-loop/governed-actions`**: **Try:** `Refund $40 to customer 1182. Call approve_governed_action first with id a-1, tool send_refund, reference POL-7, verdict require_approval.` **Pass:** an approval card.
**`/human-in-the-loop/useInterrupt`**, **`/human-in-the-loop/headless`**: **Expected now:** no interrupt (§9.5).
**`/webmcp`**: stand-in sample only (your choice). In Chrome 149+ with WebMCP, **Run tool** `searchOrders` `{"status":"open"}` returns ORD-1001 and ORD-1004.

### Agent capabilities
**`/multi-agent/subagents`**: notes only (§9.3).

---

## 8. Testing checklist / current status

| Doc page | Route | Status | Notes |
|---|---|---|---|
| `/vue/claude-sdk-python` | `/` | 📖 Reference | Landing page. |
| `/vue/claude-sdk-python` (Quickstart) | `/quickstart` | ✅ Working | Chain verified with a fake key (Anthropic `Invalid API key`). |
| `prebuilt-components` | same | ✅ Working | Only `CopilotChat` has code. |
| `custom-look-and-feel/slots` | same | ⚠️ Partial | Imports added to fragments; 2 stand-ins; `labels` type error; disclaimer never renders (§9.10, §9.11). |
| `custom-look-and-feel/headless-ui` | same | ✅ Working | |
| `programmatic-control` | same | ✅ Working | Default sample adds a harness chat (on request). |
| `prebuilt-components/copilot-threads-drawer` | same | ⚠️ Partial | Intelligence quickstart runtime, fixed local identity; needs a key (§9.7). |
| `headless-threads` | same | ⚠️ Partial | Same runtime (§9.7). |
| `frontend-tools` | same | ✅ Working | Adapter exposes the tool (captured). Not yet run against a live model. |
| `generative-ui/tool-based` | same | ✅ Working | Same. |
| `generative-ui/tool-rendering` | same | ✅ Working | Published `get_weather` served on `/tool-rendering`, own runtime path; tool-call name mapped back to `get_weather` (harness), so all three renderers match; `WeatherToolCard` heading empty (doc bug); fake-key run (§9.2). |
| `generative-ui/state-rendering` | same | ⚠️ Partial | No backend writes these keys; only the generic state tool could (§9.3, §9.4). |
| `generative-ui/mcp-apps` | same | ⚠️ Partial | Needs `npm run mcp:apps`; placeholder URL replaced (§9.8). |
| `/claude-sdk-python/generative-ui/components` | same | ⚠️ Partial | `App.vue` verbatim + chart/map plugins; tool + guide reach the model (captured); not driven live (§9.15). |
| `…/components/surfaces` | same | ⚠️ Partial | `ProductRow` stand-in; not driven live. |
| `…/components/catalogs` | same | ⚠️ Partial | Provider line wrapped with a chat; fake-key run captured `render_ui` + guide; not driven live. |
| `…/components/standard-catalog` | same | ⚠️ Partial | Not driven live. |
| `…/components/state-and-actions` | same | ⚠️ Partial | `./cart-store` never published; not driven live. |
| `…/components/theming` | same | ⚠️ Partial | Not driven live. |
| `…/components/transports` | same | ⚠️ Partial | Tool and markdown: tool/guide reach the model; not driven live. |
| `…/components/markdown-mode` | same | ⚠️ Partial | Guide reaches the model via the system prompt; the `sendContext: false` sample sends none (§9.15). |
| `…/components/from-a2ui` | same | ⚠️ Partial | `Airport`/`Arrow` stand-ins; not driven live. |
| `shared-state` | same | ⚠️ Partial | Read + tone write-back; notes only via the generic state tool (§9.4). |
| `shared-state/rendering-in-app` | same | ⚠️ Partial | Canvas renders; agent writes only via the generic state tool (§9.4). |
| `shared-state/streaming` | same | ⚠️ Partial | Streaming backend is a snippet with no agent; no token streaming (§9.3). |
| `shared-state/agent-readonly` | same | ✅ Working | Adapter puts context in the system prompt (captured). |
| `human-in-the-loop` | same | ⚠️ Partial | Adapter exposes the tool; `TimePickerCard` stand-in; page also prints React code (§9.9). |
| `human-in-the-loop/useInterrupt` | same | ❌ Broken | No interrupting agent published; `MeetingChat.vue` stand-in (§9.5). |
| `human-in-the-loop/headless` | same | ❌ Broken | Same; `HeadlessInterruptPanel.vue` stand-in (§9.5). |
| `human-in-the-loop/governed-actions` | same | ⚠️ Partial | Tool half exposed; interrupt half §9.5; `executeSideEffect` undefined. |
| `webmcp` | same | ⚠️ Partial | Stand-in sample only; as published every call errors (§9.6). |
| `multi-agent/subagents` | same | ❌ Broken | Raw-Anthropic fragments, no supervisor loop; no Vue code (§9.3). |

**Legend:** ✅ Working · ⚠️ Partial · 📖 Reference · 🚧 Not started · ❌ Broken. "Working" means wired and verified from code, mounts, and the fake-key run; **not yet driven against a live model.**

---

## 9. Known issues / doc-vs-implementation discrepancies

All against `@copilotkit/vue` / `@copilotkit/runtime` 1.87.0, `ag-ui-claude-sdk` 0.2.4, `claude-agent-sdk` 0.2.170, and the docs as of the 2026-11-13 baseline.

**1. The Quickstart is split across three pages.** `/vue/claude-sdk-python/quickstart` redirects (307) to the landing page. The root `.md` is the built-in Vue Quickstart (`BuiltInAgent`), rendered on `/vue`. The landing page renders a single code block, the runtime route, which appears in no `.md`. The agent is on the non-Vue `/claude-sdk-python/quickstart` "Use an existing agent" tab, which renders client-side (verified through `data-raw-code`). That page also has a "Backend tools and state" section printing part of `claude_agent_sdk_adapter.py` (see §9.2).

**2. Tool Rendering: a complete tool, no published way to attach it (served and working since 2026-11-17, at your request).** [Tool Rendering](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/tool-rendering) prints `weather_tool.snippet.py`: an Anthropic tool schema (`GET_WEATHER_TOOL`) and its handler, both complete. The only published way to give it to an agent is `claude_agent_sdk_adapter.py` (`run_with_claude_agent_sdk`, `_make_sdk_tool`), which calls `_build_sdk_tools`, `_set_state`, `_normalize_claude_agent_sdk_model` and `_with_initial_state` and uses `ExecuteTool`, `COPILOTKIT_MCP_SERVER_NAME` and `COPILOTKIT_TOOL_PREFIX`; no page defines any of them. Attaching the tool takes harness-written glue. It was first recorded as a gap, and on 2026-11-17 you asked for the tool to be added as given:
- **Published file:** `weather_tool.snippet.py` is written verbatim to `agent/src/app/demos/tool-rendering/` by the doc generator.
- **Agent:** the new `agent/harness_app.py` (flagged) serves `main.app` unchanged, plus `/tool-rendering`. That route is a second `ClaudeAgentAdapter` with the Quickstart's options, plus an in-process MCP server (`weather`) holding the published tool, granted in `allowed_tools`, the same shape as the page's adapter excerpt.
- **Glue:** one `@tool` wrapper passes the published schema through and returns the handler's result as text, as the excerpt's `_make_sdk_tool` does. The handler is complete, so there's no stand-in.
- **Runtime:** `default` is shared by every route, so the Tool Rendering samples use their own runtime path on the same Node server, `/api/copilotkit-tool-rendering` (`backend/runtimes/tool-rendering.ts`). Their three `App.vue` `runtime-url`s are changed and labelled, as for MCP Apps.
- **Tool name (finding, fixed in the harness):** the model calls the tool `mcp__weather__get_weather`. `ag-ui-claude-sdk` 0.2.4 strips only its own `mcp__ag_ui__` prefix (`strip_mcp_prefix`), so AG-UI events would carry the full name, and the page's per-tool `useRenderTool({ name: "get_weather" })` would never match. Naming the server `ag_ui` doesn't help: the adapter replaces that key with its own frontend-tool server on every run that has tools or state. The page's adapter derives names from `COPILOTKIT_TOOL_PREFIX`, which no page defines. **At your request**, `harness_app.py`'s `/tool-rendering` endpoint (written like `main.py`'s) renames this server's tool calls back to the published schema's name, `get_weather`, in `TOOL_CALL_START` and `MESSAGES_SNAPSHOT` events. Nothing else in the stream changes.
- **Verified** with a fake key and a local stand-in model: the tool ran, the result went back to the model, and the final `MESSAGES_SNAPSHOT` carried the call (as `get_weather`) and its result. Per-tool drew `WeatherToolCard`, zero-config drew a `get_weather` card ending "Done", and catch-all drew the stand-in with the result. A follow-up message in the same chat ran cleanly in all three. `WeatherToolCard`'s heading stays empty because it reads `parameters.city` while the tool's argument is `location` (doc bug, left as published). Not yet driven against a live model.


**3. The other page backends target the raw Anthropic API and are incomplete.**
- [State Rendering](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/state-rendering) and [State Streaming](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state/streaming) print a 16-line excerpt of a streaming loop and `state_streaming_backend.snippet.py`, a complete helper that turns a raw Anthropic message stream into `document` snapshots. No agent or endpoint uses it.
- [Shared State](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state) prints `shared_state_read_write_agent.py` in three fragments around undefined names (`client`, `normalize_claude_model`, `DEFAULT_ANTHROPIC_MODEL`, …). It also prints an `agent_server.py` endpoint that calls `run_shared_state_read_write_agent`, which no page defines.
- [Sub-agents](https://docs.copilotkit.ai/vue/claude-sdk-python/multi-agent/subagents) prints `subagents_agent.py` (prompts, tool schemas, `_invoke_sub_agent`) with no imports, undefined `normalize_claude_model` / `DEFAULT_ANTHROPIC_MODEL`, and no supervisor loop. "Rendering a live delegation log" publishes no Vue code.

By your rules these are gaps: shown on their routes, not served. Even wired, the streaming helper writes `document`, while State Rendering's `ResearchProgress.vue` reads `status`, `completed`, `total` and `draft`.

**4. Shared state through the adapter, not the docs.** No page publishes a backend that writes state for these routes, so `researcher`, `workspace`, `writer` and `default` are the Quickstart agent. Its adapter, `ag-ui-claude-sdk`, adds the run's state to the system prompt and a generic `ag_ui_update_state` tool whenever a run carries state (verified by capturing the model request). The Canvas, the notes list, `ResearchProgress` and `StreamingDocument` can therefore change if the model chooses that tool, as one snapshot at the end of the call. Nothing streams, and no page's code prompts for it, so these routes are ⚠️ Partial rather than working.

**5. Interrupts.** [Pausing the Agent for Input](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop/useInterrupt) publishes `ApprovalPanel.vue` and an `App.vue` that imports a `MeetingChat.vue` it never publishes. [Headless Interrupts](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop/headless) publishes only an `App.vue` that imports a never-published `HeadlessInterruptPanel.vue`. Both are flagged stand-ins (the files can't compile without them). No Claude agent that interrupts is published, so no interrupt can fire.

**6. Undefined functions left undefined.** `searchOrders` (WebMCP: as published every call throws; the demo shows only a flagged stand-in sample, your choice), `executeSideEffect` (Governed Actions), the backend helpers in §9.2 and §9.3, and on the Components pages `useCartStore` (`./cart-store`) and `vueBasicCatalog`.

**7. Threads: Intelligence quickstart runtime.** Wired per the [Vue Claude Agent SDK (Python) Intelligence quickstart](https://docs.copilotkit.ai/vue/claude-sdk-python/intelligence/quickstart) (identical to the other frameworks' apart from the slug). Its `authenticateApplicationUser` is never defined; per that page's "a fixed identity is suitable only for a local, single-user demo", it returns `local-user` / "Local user" (flagged, **not authentication**). Without `CPK_INTELLIGENCE_API_KEY` the path is plain SSE, and the runtime logs that `GET /threads` returns 403. Restart the backend after `project select`. The Threads `App.vue` files use `/api/copilotkit-threads` (published value kept as a comment).

**8. MCP Apps.** The published server URL is a placeholder, replaced by the page's own `http://localhost:3101/mcp` example served by `npm run mcp:apps`. It runs on its own runtime path because `mcpApps` applies to every agent on a runtime; both `App.vue` `runtime-url`s are changed (labelled).

**9. HITL Overview prints React code.** Its first block, titled `page.tsx - useHumanInTheLoop`, is a React snippet (`agentId: "hitl-in-chat"`, a `book_call` tool, a JSX `TimePickerCard` render). It can't run in a Vue app and is shown only. The Vue `MeetingApproval.vue` on the same page is mounted.

**10. Type errors in published doc code** (`npm run type-check`, 9 errors): the `labels` prop is typed as literal default strings; `useRenderTool`, `useDefaultRenderTool` and `useHumanInTheLoop` reject render components that declare only the props they use; `searchOrders` ×2; Surfaces' `FeaturedProducts.vue` imports `../product`, a type module no page publishes. `npm run build` is `vite build`.

**11. Slots › Disclaimer never renders.** `CopilotChat`'s `#input` slot props don't include `showDisclaimer`, so the sample's `CopilotChatInput` never shows its `#disclaimer` slot. Left as published.

**12. Fragments, stand-ins and wrappers.** Slots' fragments get imports only, and "Three levels" is nested in "Two levels". Headless UI's `RenderedMessages.vue` is mounted with the minimal `HeadlessChat.vue` as its composer. Shared State's two `SharedWorkspace.vue` fragments are merged. Stand-ins: `TimePickerCard.vue`, `MeetingChat.vue`, `HeadlessInterruptPanel.vue`, `CustomMessageView`, `CustomToolbarAction`, `BrandedToolCard`, `searchOrders` (on request). `HarnessApp.vue` mounts HITL's `MeetingApproval` beside a chat. **Shown only:** `agent.subscribe`, the watch-sources line, Headless Threads' pagination, `toggleItem`, useInterrupt's multi-interrupt template, and Governed Actions' type and `handleApproval`.

**13. The Claude Agent SDK runs a CLI subprocess.** `ClaudeAgentAdapter` drives the Claude Code CLI bundled with `claude-agent-sdk`, per thread, with the agent's working directory as its environment. The Quickstart builds the adapter once at module scope for that reason. On an API error the CLI retries before the run fails, so a bad key can take a few seconds to surface as `RUN_ERROR`.

**14. The harness itself.** There's no root `CopilotKitProvider`: each demo mounts its page's own `App.vue`. Doc sync runs as Vite dev-server middleware and diffs the `.md` of all 31 tracked pages (the 22 Vue pages and the nine Components pages), so changes to the landing runtime block or the Claude Agent SDK Quickstart are invisible to it. `npm run doc-files` re-reads both live. The block-catalog builder reads both backtick and tilde fences (the adapter and HITL blocks are tilde-fenced) and code the rendered page carries in RSC text chunks.

**15. Generative UI › Components (added 2026-11-17).**
- **The pages.** The nine pages live under `/claude-sdk-python/generative-ui/components`, not `/vue`, and print each sample in React, Angular, React Native and Vue tabs. Only the Vue tab and untabbed code are used; tab membership is read from the snapshot's `<Tab value="Vue">` markup.
- **The agent (the ms-agent-py choice, same rules).** The overview's Vue setup includes its own runtime: a TanStack `BuiltInAgent` (`@tanstack/ai`, `openaiText("gpt-6-luna")`, `convertInputToTanStackAI`). It's shown on the route and not served. The samples keep `runtime-url="/api/copilotkit"`, so they run on the Claude Agent SDK Quickstart agent.
- **The guide reaches the model.** For a run that carries a catalog, the Copilot Runtime's generative-UI middleware adds `render_ui` to the run's tools and its guide (components, props, how to call the tool) to the run's context (`@copilotkit/runtime` 1.87.0, `generative-ui-middleware`). `ag-ui-claude-sdk` serves the tool from its in-process MCP server and appends the context to the system prompt. **Captured 2026-11-17** with a fake key and a local stand-in for the Anthropic API (`ANTHROPIC_BASE_URL`, telemetry off):
  - Catalogs sent `mcp__ag_ui__render_ui` with the guide in the system prompt.
  - Transports › markdown and Markdown mode sent the markdown guide.
  - `sendContext: false` sent neither.
  - When the stand-in model called `mcp__ag_ui__render_ui`, the adapter emitted `TOOL_CALL_START render_ui` and ended the run for the client, which is what the runtime's middleware handles.

  Not yet checked against a live model.
- **What the harness wrote, all flagged:**
  - Five pages print only an opening `<CopilotKitProvider …>` line (Catalogs, Transports ×3, Markdown mode's `sendContext: false`, Adopt from A2UI's "After"). The harness adds the imports, a `<CopilotChat />` and the closing tag.
  - Three pages print a provider component with a `<slot />` (Standard catalog, Theming, Markdown mode's `App.vue`). The harness puts a `<CopilotChat />` in the slot.
  - Surfaces, Standard catalog's override and State and actions get small harness pages that put the published pieces together.
  - Two modules printed without imports (State and actions' `shop-ui.ts`, Adopt from A2UI's `app-ui.ts`) get only their import lines.
  - Surfaces' `FeaturedProducts.vue` imports `../shop-ui`, which that page never prints. The Catalogs page's `shop-ui.ts` (same `acme/shop@1`) and its two components are copied there, labelled.
  - The overview's plugin entry (`GenerativeUIChart`, `GenerativeUIMap`) is applied in the harness's `src/main.ts`, and `chart.js` and `maplibre-gl` are installed as the page says.
- **Stand-ins (flagged):** `ProductRow` (Surfaces), `Airport` and `Arrow` (Adopt from A2UI).
- **Shown only:**
  - Catalogs' type-error demo and its `exportA2UICatalog` script;
  - Surfaces' recommendations sample (`Product` type never published);
  - State and actions' cart samples (`./cart-store` never published);
  - Theming's `index.html` dark-mode script, since it would affect every route;
  - Markdown mode's backend fragment (`MY_PROMPT` undefined);
  - Adopt from A2UI's "Before" (`vueBasicCatalog` undefined).

---

## 10. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Connection refused, or `RUN_ERROR` naming the agent URL | Agent not running, or `AGENT_URL` unset | Start terminal 1; set `AGENT_URL` in `backend/.env`; restart the backend. |
| `RUN_ERROR "HTTP 404"` | Another server holds port 8000 | Run the agent on another `--port` and update `AGENT_URL`. |
| `RUN_ERROR "Invalid API key"` | `ANTHROPIC_API_KEY` missing or wrong in **`agent/.env`** | Fix it and restart the agent (`main.py` reads `.env` at import). |
| `Agent … not found` | Backend isn't this repo's `server.ts` | Run `backend/server.ts`. |
| Threads stay on "Loading threads…" | Runtime started before the key existed (SSE → 403) | Restart the backend; the startup line must say `(intelligence)`. |
| CORS error on `/quickstart` or `/generative-ui/components` | Those `App.vue` files call `:8200` directly | Keep `cors: true`. |
| `Port 5173 is in use` | Another harness's Vite | Stop it (one harness at a time on 5173/8200). |
| Tool Rendering only: `RUN_ERROR "HTTP 404"` (or a prose answer and no card) | The agent was started with the Quickstart's `uv run uvicorn main:app`, which has no `/tool-rendering` | Start it with `uv run uvicorn harness_app:app …` (§6); every other route works with either. |
| Tool Rendering per-tool: `WeatherToolCard` shows the JSON but no city heading | Doc bug: the card reads `parameters.city`, the published tool's argument is `location` | Expected; left as published (§9.2). |
| `npm run doc-files` stops with `AssertionError: … is not on the rendered page` | A block the generator uses changed on the live site since `doc-snapshot/` (doc drift) | Run `/doc-sync`, review the changes, then `npm run doc-files` again (see Doc drift detection). |

---

## Doc drift detection

`/doc-sync` fetches the `.md` behind all 31 tracked pages, diffs each against `doc-snapshot/pages/`, replaces the snapshot, and ranks changes High/Medium/Low. Commit `pages/`, `manifest.json` and `CHANGELOG.md`; `reports/` is gitignored. **Regenerating the doc files:** `cd frontend && npm run doc-files` rebuilds the block catalog (snapshot pages, plus the Claude Agent SDK Quickstart fetched live, every block checked against the rendered page). It then rewrites the verbatim doc files (`write-genui-files.py` writes the Components routes' files), `src/lib/published.json`, `agent/main.py` and `agent/src/app/demos/tool-rendering/weather_tool.snippet.py`.

**Pending drift (found 2026-11-17, not yet synced).** The live site has changed five blocks this repo mounts since the snapshot: Slots' disclaimer sample (block 2: `CopilotChatInput` now passes `:mode`, `:tools-menu` and `:show-disclaimer="true"`), Programmatic Control's `App.vue` (block 1), useInterrupt's `App.vue` (block 3), Headless HITL's `App.vue` (block 0) and Governed Actions' `GovernedActionCard.vue` (block 4). Until `/doc-sync` updates `doc-snapshot/`, `npm run doc-files` stops on the first of them; the routes still mount the snapshot versions. The Slots change may also bear on its "disclaimer never renders" finding (§9.11).
---

## 11. Project structure

```
claude-sdk-py/
├── CLAUDE.md · PR_GUIDELINES.md · README.md · .env.example
├── doc-snapshot/                    # pages/*.md + manifest.json — doc-sync baseline
├── agent/                           # Claude Agent SDK (Python, uv) — FastAPI :8000
│   ├── main.py                      # ★ Claude Agent SDK Quickstart agent, verbatim
│   ├── harness_app.py               # [harness, flagged] serves main.app + /tool-rendering (§9.2)
│   ├── src/app/demos/tool-rendering/weather_tool.snippet.py   # Tool Rendering's tool, verbatim, served
│   └── pyproject.toml · uv.lock     # the Quickstart's `uv add` line
├── backend/                         # Copilot Runtime, Node :8200
│   ├── server.ts                    # ★ Vue Quickstart host + landing runtime
│   ├── agents.ts                    # HttpAgent per doc agent id
│   └── runtimes/ threads.ts · mcp-apps.ts · tool-rendering.ts
└── frontend/                        # Vite + Vue 3
    ├── scripts/ build-doc-catalog.py · write-doc-files.py · write-genui-files.py · write-demo-entries.py
    └── src/ lib/nav-config.ts (★ routes + statuses) · lib/published.json (every block, for page backends shown as published) · routes/<doc path>/{Notes.vue, demo-chat/} · …
```

---

## 12. References

**Getting Started**: [Quickstart (landing)](https://docs.copilotkit.ai/vue/claude-sdk-python) · [Vue Quickstart (frontend steps)](https://docs.copilotkit.ai/vue) · [Claude Agent SDK Quickstart (agent)](https://docs.copilotkit.ai/claude-sdk-python/quickstart)

**Basics**: [Prebuilt Components](https://docs.copilotkit.ai/vue/claude-sdk-python/prebuilt-components) · [Slots](https://docs.copilotkit.ai/vue/claude-sdk-python/custom-look-and-feel/slots) · [Headless UI](https://docs.copilotkit.ai/vue/claude-sdk-python/custom-look-and-feel/headless-ui) · [Programmatic Control](https://docs.copilotkit.ai/vue/claude-sdk-python/programmatic-control) · [Threads Drawer](https://docs.copilotkit.ai/vue/claude-sdk-python/prebuilt-components/copilot-threads-drawer) · [Headless Threads](https://docs.copilotkit.ai/vue/claude-sdk-python/headless-threads) · [Frontend Tools](https://docs.copilotkit.ai/vue/claude-sdk-python/frontend-tools)

**Generative UI**: [Components as Tools](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/tool-based) · [Tool Call Rendering](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/tool-rendering) · [State Rendering](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/state-rendering) · [MCP Apps](https://docs.copilotkit.ai/vue/claude-sdk-python/generative-ui/mcp-apps)

**Generative UI › Components**: [Components and surfaces](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components) · [Surfaces](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/surfaces) · [Catalogs](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/catalogs) · [Standard catalog](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/standard-catalog) · [State and actions](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/state-and-actions) · [Theming](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/theming) · [Transports](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/transports) · [Markdown mode](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/markdown-mode) · [Adopt from A2UI](https://docs.copilotkit.ai/claude-sdk-python/generative-ui/components/from-a2ui)

**Interactivity**: [Shared State](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state) · [Render agent state in your app](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state/rendering-in-app) · [State Streaming](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state/streaming) · [Agent Read-Only Context](https://docs.copilotkit.ai/vue/claude-sdk-python/shared-state/agent-readonly) · [HITL Overview](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop) · [Pausing the Agent for Input](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop/useInterrupt) · [Headless Interrupts](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop/headless) · [Governed Action Approval UI](https://docs.copilotkit.ai/vue/claude-sdk-python/human-in-the-loop/governed-actions) · [WebMCP](https://docs.copilotkit.ai/vue/claude-sdk-python/webmcp)

**Agent capabilities**: [Sub-agents](https://docs.copilotkit.ai/vue/claude-sdk-python/multi-agent/subagents)

**Intelligence (Threads routes)**: [Connect Intelligence in 5 minutes](https://docs.copilotkit.ai/vue/claude-sdk-python/intelligence/quickstart)
