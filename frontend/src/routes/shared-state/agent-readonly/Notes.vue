<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
</script>

<template>
  <RouteHeader path="/shared-state/agent-readonly" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
      <code>useAgentContext({ description: "Active workspace", value: workspaceId })</code> publishes the ref to the agent on every turn,
      with no setter.
    </p>
    <div class="mt-4">
      <TryIt :prompts="['Which workspace am I in?', 'Switch my workspace to “orion”']" expect="“northstar”, with no tool call. The second request cannot change “Workspace: northstar” on the page." fail="The agent does not know the workspace." />
    </div>
  </Panel>
  <Panel title="The demo">
    <div class="space-y-4">
      <SourceCode file="frontend/src/routes/shared-state/agent-readonly/demo-chat/components/WorkspaceContext.vue" />
      <SourceCode file="frontend/src/routes/shared-state/agent-readonly/demo-chat/App.vue" />
    </div>
  </Panel>
  <Callout tone="info" title="How context reaches a Claude agent (README §3)">
    <p>The page credits “the backend's CopilotKit middleware”. For the Claude Agent SDK there is no middleware: the installed <code>ag-ui-claude-sdk</code> adapter appends the run's context to the agent's system prompt itself, so the Quickstart agent sees the published value with no change to <code>main.py</code> (verified by capturing the model request).</p>
  </Callout>
</template>
