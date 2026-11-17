<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
</script>

<template>
  <RouteHeader path="/quickstart" />

  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      The whole stack, assembled from the three places the docs put it: the Vue app from the Vue Quickstart (<code>App.vue</code> with
      <code>CopilotChat</code>), the runtime from the Claude Agent SDK (Python) landing page (an AG-UI <code>HttpAgent</code> named <code>my_agent</code>
      pointed at <code>AGENT_URL</code>) hosted in the Vue Quickstart's Node <code>server.ts</code>, and the agent from the Claude Agent SDK
      Quickstart (<code>main.py</code>: a <code>ClaudeAgentAdapter</code> behind a FastAPI <code>POST /</code>). Three
      processes: the agent on :8000, the runtime on :8200, Vite on :5173.
    </p>
    <div class="mt-4">
      <TryIt
        :prompts="['Hello! What can you do?', 'Write a haiku about rivers.']"
        expect="A streamed reply from the Claude agent; the Inspector's AG-UI Events show RUN_STARTED → TEXT_MESSAGE_* → RUN_FINISHED."
        fail="Connection refused or RUN_ERROR — the agent is not running on :8000 or AGENT_URL is unset; an authentication error — ANTHROPIC_API_KEY missing in agent/.env."
      />
    </div>
  </Panel>

  <Panel title="The demo" description="Verbatim src/App.vue from the Vue Quickstart, which the Claude Agent SDK (Python) Vue Quickstart's .md is.">
    <SourceCode file="frontend/src/routes/quickstart/demo-chat/App.vue" />
  </Panel>

  <Panel title="The runtime, as published on the Claude Agent SDK landing page" description="Its only code block — a Next.js route.">
    <PublishedCode page="index" :index="9" />
  </Panel>

  <Panel title="This repo's runtime" description="The Vue Quickstart's Node host with the landing page's agent registration; additions marked [harness].">
    <div class="space-y-4">
      <SourceCode file="backend/server.ts" />
      <SourceCode file="backend/agents.ts" />
    </div>
  </Panel>

  <Panel title="The agent — Claude Agent SDK Quickstart, “Use an existing agent”" description="main.py verbatim. Run with uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000, as the Quickstart says.">
    <SourceCode file="agent/main.py" />
  </Panel>

  <Panel title="The Vue Quickstart's server.ts and main.ts, as published">
    <div class="space-y-4">
      <PublishedCode page="index" :index="4" note="Host only — its BuiltInAgent registration is replaced by the landing page's HttpAgent, as the Vue Quickstart itself instructs for an existing agent." />
      <PublishedCode page="index" :index="5" />
    </div>
  </Panel>

  <Callout tone="harness" title="How the three sources fit (README §3, §9.1)">
    <p>· <strong>The Vue Claude Agent SDK (Python) Quickstart redirects to a landing page.</strong> Its .md is the built-in Vue Quickstart, which says: if you already have an agent, keep its Vue frontend steps and take the runtime wiring from your framework's quickstart.</p>
    <p>· <strong>The landing page</strong> publishes only the runtime route (<code>my_agent: new HttpAgent({ url: process.env.AGENT_URL! })</code>), as a Next.js route; a Vue app has no Next route, so it is hosted in the Vue Quickstart's Node listener.</p>
    <p>· <strong>The agent</strong> is from the Claude Agent SDK Quickstart the landing page links as its guide: the “Use an existing agent” path — a module-level <code>ClaudeAgentAdapter</code> (<code>ANTHROPIC_MODEL</code>, default <code>claude-opus-4-8</code>, no tools, <code>permission_mode: "dontAsk"</code>) streamed from a FastAPI <code>POST /</code>.</p>
    <p>· The runtime also registers the doc agent ids (<code>backend/agents.ts</code>); each is <code>my_agent</code>.</p>
  </Callout>

  <Callout tone="info" title="What this agent can and cannot do (README §3)">
    <p>The <code>ag-ui-claude-sdk</code> adapter exposes every CopilotKit frontend tool to the agent through an in-process MCP server (<code>mcp__ag_ui__&lt;name&gt;</code>), appends read-only context and the current state to the system prompt, and adds a generic <code>ag_ui_update_state</code> tool whenever a run carries state — all verified by capturing the model request. So frontend tools, HITL and context work with no change to <code>main.py</code>, and the agent can write shared state if it chooses to. It has no backend tools and never interrupts.</p>
  </Callout>
</template>
