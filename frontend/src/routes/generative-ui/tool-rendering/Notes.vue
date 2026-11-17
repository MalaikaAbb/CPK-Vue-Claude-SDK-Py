<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
const D = "frontend/src/routes/generative-ui/tool-rendering/demo-chat";
</script>

<template>
  <RouteHeader path="/generative-ui/tool-rendering" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      Three ways to draw a tool call — the built-in <code>*</code> renderer, a custom catch-all, and a per-tool <code>useRenderTool</code> for
      <code>get_weather</code> — for the page's backend tool, <code>get_weather</code>.
    </p>
    <div class="mt-4">
      <TryIt :prompts="['What is the weather in Tokyo?']" expect="Per-tool: WeatherToolCard with the handler's JSON (68, Sunny); its heading stays empty because the card reads parameters.city but the tool's argument is location (doc bug). Zero-config: a get_weather card that ends “Done”. Catch-all: the BrandedToolCard stand-in with the result." fail="A prose answer and no tool call: the agent server is running main.py instead of harness_app.py (no /tool-rendering), or the model skipped the tool." />
    </div>
  </Panel>
  <Panel title="Published files, mounted verbatim">
    <div class="space-y-4">
      <SourceCode :file="`${D}/default/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/per-tool/components/WeatherToolCard.vue`" />
      <SourceCode :file="`${D}/per-tool/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/per-tool/App.vue`" note="The same published App.vue is copied into each variant directory, unchanged." />
    </div>
  </Panel>
  <Panel title="The page's backend, as published">
    <div class="space-y-4">
      <PublishedCode page="generative-ui__tool-rendering" :index="8" note="weather_tool.snippet.py: a complete get_weather (Anthropic tool schema + handler). Written verbatim to agent/src/app/demos/tool-rendering/ and served (see below)." />
      <PublishedCode page="generative-ui__tool-rendering" :index="6" note="claude_agent_sdk_adapter.py, part 1: run_with_claude_agent_sdk. Calls _build_sdk_tools, _set_state, _normalize_claude_agent_sdk_model and _with_initial_state, and uses ExecuteTool, COPILOTKIT_MCP_SERVER_NAME and COPILOTKIT_TOOL_PREFIX — none defined on any page; no imports. Not served." />
      <PublishedCode page="generative-ui__tool-rendering" :index="7" note="Part 2: _make_sdk_tool, which wraps one tool schema as a Claude SDK tool given an execute_tool callback no page defines." />
    </div>
  </Panel>
  <Callout tone="info" title="Agent: the page's get_weather on /tool-rendering (README §9.2, your request)">
    <p><code>agent/harness_app.py</code> loads the published <code>weather_tool.snippet.py</code> unchanged. It attaches the tool the way the adapter excerpt does: an in-process MCP server in <code>mcp_servers</code>, with the tool granted in <code>allowed_tools</code>. A few lines of harness glue pass the published schema through and return the handler's result as text. The agent is a second <code>ClaudeAgentAdapter</code> with the Quickstart's options, served at <code>/tool-rendering</code> on the same app. The three samples reach it through their own runtime path, <code>/api/copilotkit-tool-rendering</code>, so every other route keeps the Quickstart agent.</p>
    <p><strong>Tool name (fixed in the harness).</strong> The model calls <code>mcp__weather__get_weather</code>, and the adapter strips only its own <code>mcp__ag_ui__</code> prefix. Left alone, the call would reach the page under the full name, and the per-tool <code>useRenderTool({ name: "get_weather" })</code> would never match. Naming the server <code>ag_ui</code> doesn't help, because the adapter replaces that server with its own. So the <code>/tool-rendering</code> endpoint renames this server's calls back to the published schema's name, <code>get_weather</code>, in the tool-call and messages-snapshot events. Nothing else in the stream changes.</p>
    <p>Checked on 2026-11-17 with a fake key and a local stand-in model. Per-tool drew <code>WeatherToolCard</code>, zero-config drew a <code>get_weather</code> card, and catch-all drew the stand-in, all with the handler's result. A follow-up message in the same chat ran cleanly. Not yet driven against a live model.</p>
  </Callout>
  <Panel title="Custom catch-all" description="The page prints only one line for this file.">
    <div class="space-y-4">
      <PublishedCode page="generative-ui__tool-rendering" :index="1" />
      <SourceCode :file="`${D}/catch-all/components/AgentExperience.vue`" />
      <SourceCode :file="`${D}/catch-all/components/BrandedToolCard.vue`" />
    </div>
  </Panel>
  <Panel title="Published, not mounted">
    <PublishedCode page="generative-ui__tool-rendering" :index="4" note="Fragment: `parameters` and `locale` are never declared." />
  </Panel>
  <Callout tone="harness" title="What the harness added">
    <p>· The catch-all <code>AgentExperience.vue</code> wraps the published line; <code>BrandedToolCard</code> is a stand-in — never published.</p>
    <p>· The three <code>App.vue</code> files use <code>runtime-url="/api/copilotkit-tool-rendering"</code> (the published value is kept as a comment); <code>backend/runtimes/tool-rendering.ts</code> serves it from the same Node server.</p>
    <p>· <code>agent/harness_app.py</code>: the Quickstart's app plus <code>/tool-rendering</code>, with the published tool attached through a small SDK-tool wrapper, and its tool-call name mapped back to <code>get_weather</code>.</p>
  </Callout>
</template>
