import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  AGENTIC_CONTAINER: DurableObjectNamespace<AgenticContainer>;
}

export class AgenticContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
  enableInternet = true;
}

export default {
  async fetch(
    request: Request,
    env: Env,
  ): Promise<Response> {
    return getContainer(
      env.AGENTIC_CONTAINER,
    ).fetch(request);
  },
};
