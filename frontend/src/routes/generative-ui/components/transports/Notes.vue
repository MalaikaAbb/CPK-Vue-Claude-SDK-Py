<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
const D = "frontend/src/routes/generative-ui/components/transports/demo-chat";
</script>

<template>
  <RouteHeader path="/generative-ui/components/transports" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">How generated UI travels: the default <code>render_ui</code> tool, or <code>transport: 'markdown'</code> (the agent writes a2ui code blocks in its reply), and limiting generative UI to some agents with <code>agentIds</code>.</p>
    <div class="mt-4"><TryIt :prompts="['Compare three plans in a table']" expect="Tool: a component via render_ui. Markdown: a component from an a2ui block in the reply. agentIds ['shop']: plain text, since the chat's agent is default." fail="Tool: no component — see the agent note. Markdown: plain text — the model did not write an a2ui block." /></div>
  </Panel>
  <Panel title="Harness wrappers around the published provider lines">
    <div class="space-y-4">
      <SourceCode :file="`${D}/tool/HarnessApp.vue`" note="Opening provider line verbatim; imports, chat and closing tag added." />
      <SourceCode :file="`${D}/markdown/HarnessApp.vue`" note="Same." />
      <SourceCode :file="`${D}/agent-ids/HarnessApp.vue`" note="Same. No agent is registered as shop." />
    </div>
  </Panel>
  <Panel title="Published, not mounted">
    <div class="space-y-4">
      <PublishedCode page="claude-sdk-python__generative-ui__components__transports" :index="4" note="A runtime option (generativeUI: true), printed as a Next route; the harness runtime is unchanged." />
    </div>
  </Panel>
  <Callout tone="info" title="Agent: the Claude Agent SDK Quickstart agent (the ms-agent-py choice, same rules; README §9.15)">
    <p>The samples keep <code>runtime-url="/api/copilotkit"</code> as published, so <code>default</code> is the Claude Agent SDK Quickstart agent. For a run that carries a catalog, the Copilot Runtime adds the <code>render_ui</code> tool to the run's tools and its guide (the components, their props, how to call the tool) to the run's context. The ag-ui-claude-sdk adapter passes both on. It serves the run's tools from an in-process MCP server, so the model sees <code>mcp__ag_ui__render_ui</code>, and the adapter reports the call back as <code>render_ui</code>. It appends the context to the system prompt. Checked on 2026-11-17 by capturing the model request with a fake key and a local stand-in for the Anthropic API. Whether the model then renders well is not yet checked against a live model. The page's own runtime — a TanStack <code>BuiltInAgent</code>, on the overview page — is shown there and not served.</p>
  </Callout>
  <Callout tone="info" title="Framework tabs"><p>This page is not under <code>/vue</code>: it prints each sample for React, Angular, React Native and Vue. Only the Vue tab (and code outside the tabs) is used.</p></Callout>
</template>
