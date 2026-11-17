<script setup lang="ts">
import Callout from "@/components/harness/Callout.vue";
import Panel from "@/components/harness/Panel.vue";
import PublishedCode from "@/components/harness/PublishedCode.vue";
import RouteHeader from "@/components/harness/RouteHeader.vue";
import SourceCode from "@/components/harness/SourceCode.vue";
import TryIt from "@/components/harness/TryIt.vue";
const D = "frontend/src/routes/generative-ui/components/state-and-actions/demo-chat";
</script>

<template>
  <RouteHeader path="/generative-ui/components/state-and-actions" />
  <Panel title="What it demonstrates">
    <p class="text-sm leading-relaxed text-slate-700 dark:text-slate-300">Generated UI that calls your code: shopUI declares an <code>addToCart</code> function and an <code>onAddToCart</code> event on ProductCard; the card awaits the result and shows an error if it fails.</p>
    <div class="mt-4"><TryIt :prompts="['Show the Trail Runner product card with an add-to-cart button']" expect="A ProductCard with “Add to cart”. With no handler registered (see below), clicking shows the card's error." fail="A prose answer and no component: the model did not call render_ui, or the run errored (check the Inspector)." /></div>
  </Panel>
  <Panel title="Published files, mounted verbatim">
    <div class="space-y-4">
      <SourceCode :file="`${D}/shop-ui.ts`" note="The page prints it without imports; three import lines added." />
      <SourceCode :file="`${D}/components/ProductCard.vue`" />
    </div>
  </Panel>
  <Panel title="Harness wrapper">
    <div class="space-y-4">
      <SourceCode :file="`${D}/HarnessApp.vue`" note="The provider for shopUI with a CopilotChat." />
    </div>
  </Panel>
  <Panel title="Published, not mounted">
    <div class="space-y-4">
      <PublishedCode page="claude-sdk-python__generative-ui__components__state-and-actions" :index="15" note="The addToCart handler: imports ./cart-store (useCartStore), which no page publishes — left missing, so it is not mounted." />
      <PublishedCode page="claude-sdk-python__generative-ui__components__state-and-actions" :index="3" note="Live state in generated UI (bind): ProductCard, z and createGenerativeUI are not imported." />
      <PublishedCode page="claude-sdk-python__generative-ui__components__state-and-actions" :index="7" note="useGenerativeUIState: needs ./cart-store (never published)." />
      <PublishedCode page="claude-sdk-python__generative-ui__components__state-and-actions" :index="26" note="CheckoutForm.vue: its catalog entry is printed only for React/tsx." />
    </div>
  </Panel>
  <Callout tone="info" title="Agent: the Claude Agent SDK Quickstart agent (the ms-agent-py choice, same rules; README §9.15)">
    <p>The samples keep <code>runtime-url="/api/copilotkit"</code> as published, so <code>default</code> is the Claude Agent SDK Quickstart agent. For a run that carries a catalog, the Copilot Runtime adds the <code>render_ui</code> tool to the run's tools and its guide (the components, their props, how to call the tool) to the run's context. The ag-ui-claude-sdk adapter passes both on. It serves the run's tools from an in-process MCP server, so the model sees <code>mcp__ag_ui__render_ui</code>, and the adapter reports the call back as <code>render_ui</code>. It appends the context to the system prompt. Checked on 2026-11-17 by capturing the model request with a fake key and a local stand-in for the Anthropic API. Whether the model then renders well is not yet checked against a live model. The page's own runtime — a TanStack <code>BuiltInAgent</code>, on the overview page — is shown there and not served.</p>
  </Callout>
  <Callout tone="info" title="Framework tabs"><p>This page is not under <code>/vue</code>: it prints each sample for React, Angular, React Native and Vue. Only the Vue tab (and code outside the tabs) is used.</p></Callout>
</template>
