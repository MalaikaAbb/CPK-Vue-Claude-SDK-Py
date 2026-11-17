<script setup lang="ts">
import { CopilotKitProvider } from "@copilotkit/vue/v2";
import AgentExperience from "./components/AgentExperience.vue";
</script>

<template>
  <!-- [harness] published: runtime-url="/api/copilotkit" — Tool Rendering's get_weather agent is mounted separately at /api/copilotkit-tool-rendering (README §9) -->
  <CopilotKitProvider runtime-url="/api/copilotkit-tool-rendering"><AgentExperience /></CopilotKitProvider>
</template>
