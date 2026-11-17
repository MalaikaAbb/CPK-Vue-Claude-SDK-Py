<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
</script>

<template>
  <RouteHeader path="/shared-state/streaming" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      <code>StreamingDocument</code> renders agent <code>writer</code>'s <code>state.document</code> with a LIVE badge while the run streams.
    </p>
    <div class="mt-4">
      <TryIt :prompts="['Write a short poem about autumn']" expect="If a backend streamed document: LIVE, then the poem growing in the article." fail="LIVE while the run lasts and “Waiting for a draft…” — nothing streams document; at most the adapter's generic state tool sets it in one step (see below)." />
    </div>
  </Panel>
  <Panel title="The demo">
    <div class="space-y-4">
      <SourceCode file="frontend/src/routes/shared-state/streaming/demo-chat/components/StreamingDocument.vue" />
      <SourceCode file="frontend/src/routes/shared-state/streaming/demo-chat/App.vue" />
    </div>
  </Panel>
  <Panel title="The page's backend snippets, as published">
    <div class="space-y-4">
      <PublishedCode page="shared-state__streaming" :index="0" note="Titled agent.py: the write_document branch of a streaming loop, out of context." />
      <PublishedCode page="shared-state__streaming" :index="1" note="state_streaming_backend.snippet.py: a complete helper (raw Anthropic stream → document snapshots), with no agent or endpoint using it." />
    </div>
  </Panel>
  <Callout tone="warn" title="Why this route is only partial (README §9.3, §9.4)">
    <p>The page's streaming backend is written against the raw Anthropic Messages API and stops short of an agent: per your rules it is a gap, and <code>writer</code> is the Quickstart agent, which does not stream <code>document</code>.</p>
    <p>Whenever a run carries state, the Quickstart agent's adapter (<code>ag-ui-claude-sdk</code>) puts that state in the system prompt and gives the agent a generic <code>ag_ui_update_state</code> tool (verified by capturing the model request), so the agent <em>can</em> write these keys if it chooses to — as one snapshot when the tool call completes, not streamed.</p>
  </Callout>
  <Callout tone="harness" title="Agent id"><p><code>writer</code> → <code>my_agent</code>, the Claude Agent SDK Quickstart's agent (<code>backend/agents.ts</code>).</p></Callout>
</template>
