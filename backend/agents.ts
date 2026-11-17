import { HttpAgent } from "@ag-ui/client";

/**
 * Agents for every runtime in this repo.
 *
 * `myAgent()` is the agent the Claude Agent SDK (Python) landing page registers
 * (https://docs.copilotkit.ai/vue/claude-sdk-python — its only code block),
 * verbatim: an AG-UI HttpAgent pointed at AGENT_URL, where the Claude Agent SDK
 * Quickstart's FastAPI app (agent/main.py: ClaudeAgentAdapter, POST "/")
 * serves the agent.
 *
 * [harness] Doc agent ids. The landing page registers only `my_agent`, while
 * the Vue samples use `default` (no agent-id) and ids no page registers. By the
 * user's rules a page's own published agent would run under its id if it were
 * complete — but the Claude page backends are snippets for the raw Anthropic
 * API or call helpers no page defines (gaps, at the user's decision). So every
 * id is the landing page's my_agent, unchanged. The one exception (user's
 * request, 2026-11-17): Tool Rendering's published get_weather runs on
 * agent/harness_app.py's /tool-rendering, reached through its own runtime path
 * (toolRenderingAgent, runtimes/tool-rendering.ts).
 */
export function myAgent() {
  // Verbatim from the landing page's runtime route.
  return new HttpAgent({ url: process.env.AGENT_URL! });
}

/** [harness] The landing page's HttpAgent, pointed at harness_app.py's /tool-rendering (Tool Rendering's get_weather agent). */
export function toolRenderingAgent() {
  return new HttpAgent({ url: new URL("tool-rendering", process.env.AGENT_URL!).toString() });
}

/** Doc agent ids, and the page each one comes from. */
export const DOC_AGENT_IDS = {
  default: "no agent-id: Quickstart, Slots, Frontend Tools, Components as Tools, …",
  "my-agent": "Prebuilt Components, Headless UI, Headless Threads",
  sales: "Programmatic Control",
  support: "Threads Drawer",
  researcher: "State Rendering",
  workspace: "Shared State",
  writer: "State Streaming",
} as const;

export function docAgents() {
  return Object.fromEntries(Object.keys(DOC_AGENT_IDS).map((id) => [id, myAgent()]));
}
