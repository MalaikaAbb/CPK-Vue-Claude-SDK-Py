<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
</script>

<template>
  <RouteHeader path="/generative-ui/state-rendering" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      <code>useAgent</code> with <code>OnStateChanged</code> + <code>OnRunStatusChanged</code> on agent <code>researcher</code>;
      <code>ResearchProgress</code> renders <code>status</code>, a progress bar from <code>completed</code>/<code>total</code>, and <code>draft</code>.
    </p>
    <div class="mt-4">
      <TryIt :prompts="['Write a short note about bicycles']" expect="If the backend wrote these keys: status text, a moving bar and a draft." fail="“Idle” and an empty bar — no published backend writes these keys; only the adapter's generic state tool could (see below)." />
    </div>
  </Panel>
  <Panel title="The demo">
    <div class="space-y-4">
      <SourceCode file="frontend/src/routes/generative-ui/state-rendering/demo-chat/components/ResearchProgress.vue" />
      <SourceCode file="frontend/src/routes/generative-ui/state-rendering/demo-chat/App.vue" />
    </div>
  </Panel>
  <Panel title="The page's backend snippets, as published">
    <div class="space-y-4">
      <PublishedCode page="generative-ui__state-rendering" :index="2" note="Titled agent.py: 16 lines from inside a streaming loop (current_tool_name, _partial_json_string_property, state, encoder are all outside it)." />
      <PublishedCode page="generative-ui__state-rendering" :index="3" note="state_streaming_backend.snippet.py: a complete helper that turns a raw Anthropic message stream into document snapshots — but no agent, endpoint or Anthropic call uses it." />
    </div>
  </Panel>
  <Callout tone="warn" title="Why this route is only partial (README §9.3, §9.4)">
    <p>Both snippets target the raw Anthropic Messages API, not the Quickstart's <code>ClaudeAgentAdapter</code>, and neither is an agent. Per your rules nothing was written in their place; <code>researcher</code> is the Quickstart agent. Even wired, they write <code>document</code>, while <code>ResearchProgress</code> reads <code>status</code>, <code>completed</code>, <code>total</code> and <code>draft</code>.</p>
    <p>Whenever a run carries state, the Quickstart agent's adapter (<code>ag-ui-claude-sdk</code>) puts that state in the system prompt and gives the agent a generic <code>ag_ui_update_state</code> tool (verified by capturing the model request), so the agent <em>can</em> write these keys if it chooses to — as one snapshot when the tool call completes, not streamed.</p>
  </Callout>
  <Callout tone="harness" title="Agent id"><p><code>researcher</code> → <code>my_agent</code>, the Claude Agent SDK Quickstart's agent (<code>backend/agents.ts</code>).</p></Callout>
</template>
