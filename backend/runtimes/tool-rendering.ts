import { CopilotRuntime } from "@copilotkit/runtime/v2";

import { toolRenderingAgent } from "../agents";

/**
 * [harness] The runtime behind /generative-ui/tool-rendering, mounted at
 * /api/copilotkit-tool-rendering on the same Node server.
 *
 * Tool Rendering's samples use agent `default`, which every other route shares
 * with the Quickstart agent. Here `default` is the agent that
 * agent/harness_app.py mounts at /tool-rendering: the Quickstart's options plus
 * the page's published get_weather (schema + handler, unchanged). The three
 * Tool Rendering App.vue files point their runtime-url here (labelled).
 * README §9.2.
 */
export function createToolRenderingRuntime(): CopilotRuntime {
  return new CopilotRuntime({ agents: { default: toolRenderingAgent() } });
}
