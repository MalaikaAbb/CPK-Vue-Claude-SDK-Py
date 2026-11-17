<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
</script>

<template>
  <RouteHeader path="/multi-agent/subagents" />
  <Callout tone="warn" title="Gap: no supervisor loop, and no frontend (README §9.3)">
    <p>· <code>src/agents/subagents_agent.py</code> (printed in two sections) defines the sub-agent prompts, the supervisor prompt, the three delegation tool schemas and <code>_invoke_sub_agent</code> — a raw Anthropic call. It imports nothing and uses <code>normalize_claude_model</code> and <code>DEFAULT_ANTHROPIC_MODEL</code>, which no page defines, and the supervisor loop it refers to (<code>run_subagents_agent</code>) is never printed. Per your rules nothing was written in its place; it is not served.</p>
    <p>· The “Rendering a live delegation log” section publishes no Vue code, so this route has no demo.</p>
  </Callout>
  <Panel title="Published backend, as printed">
    <div class="space-y-4">
      <PublishedCode page="multi-agent__subagents" :index="1" />
      <PublishedCode page="multi-agent__subagents" :index="2" note="The page prints the supervisor tool schemas a second time (also its first block)." />
    </div>
  </Panel>
</template>
