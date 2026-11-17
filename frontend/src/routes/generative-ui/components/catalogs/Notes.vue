<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
const D = "frontend/src/routes/generative-ui/components/catalogs/demo-chat";
</script>

<template>
  <RouteHeader path="/generative-ui/components/catalogs" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">A catalog of your own components (<code>ProductGrid</code> with a <code>children</code> slot, <code>ProductCard</code>) declared with zod props in <code>createGenerativeUI</code>, handed to the provider.</p>
    <div class="mt-4"><TryIt :prompts="['Show me three products in a grid']" expect="A ProductGrid holding ProductCards, rendered in the chat." fail="A prose answer and no component: the model did not call render_ui, or the run errored (check the Inspector)." /></div>
  </Panel>
  <Panel title="Published files, mounted verbatim">
    <div class="space-y-4">
      <SourceCode :file="`${D}/components/ProductGrid.vue`" />
      <SourceCode :file="`${D}/components/ProductCard.vue`" />
      <SourceCode :file="`${D}/shop-ui.ts`" />
    </div>
  </Panel>
  <Panel title="Harness wrapper">
    <div class="space-y-4">
      <SourceCode :file="`${D}/HarnessApp.vue`" note="The page prints only the opening provider line; imports, a CopilotChat and the closing tag added." />
    </div>
  </Panel>
  <Panel title="Published, not mounted">
    <div class="space-y-4">
      <PublishedCode page="claude-sdk-python__generative-ui__components__catalogs" :index="13" note="Fragment that deliberately shows a type error (props.color); shopUI is not imported." />
      <PublishedCode page="claude-sdk-python__generative-ui__components__catalogs" :index="19" note="Fragment: cartUI, Hero and z are never defined or imported." />
      <PublishedCode page="claude-sdk-python__generative-ui__components__catalogs" :index="23" note="A Node script (fs is never imported) that exports the catalog as JSON." />
    </div>
  </Panel>
  <Callout tone="info" title="Agent: the Claude Agent SDK Quickstart agent (the ms-agent-py choice, same rules; README §9.15)">
    <p>The samples keep <code>runtime-url="/api/copilotkit"</code> as published, so <code>default</code> is the Claude Agent SDK Quickstart agent. For a run that carries a catalog, the Copilot Runtime adds the <code>render_ui</code> tool to the run's tools and its guide (the components, their props, how to call the tool) to the run's context. The ag-ui-claude-sdk adapter passes both on. It serves the run's tools from an in-process MCP server, so the model sees <code>mcp__ag_ui__render_ui</code>, and the adapter reports the call back as <code>render_ui</code>. It appends the context to the system prompt. Checked on 2026-11-17 by capturing the model request with a fake key and a local stand-in for the Anthropic API. Whether the model then renders well is not yet checked against a live model. The page's own runtime — a TanStack <code>BuiltInAgent</code>, on the overview page — is shown there and not served.</p>
  </Callout>
  <Callout tone="info" title="Framework tabs"><p>This page is not under <code>/vue</code>: it prints each sample for React, Angular, React Native and Vue. Only the Vue tab (and code outside the tabs) is used.</p></Callout>
</template>
