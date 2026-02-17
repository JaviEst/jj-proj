import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 30000,
  use: {
    baseURL: "http://127.0.0.1:4173",
    headless: true,
  },
  webServer: {
    command:
      "npm --prefix code/frontend/frontend run build && npx --yes http-server code/frontend/frontend/dist -p 4173 -a 127.0.0.1",
    port: 4173,
    timeout: 120000,
    reuseExistingServer: true,
  },
});
