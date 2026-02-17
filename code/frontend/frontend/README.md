This is a lightweight frontend used to validate UI workflows and Docker builds.

If you replace it with a full Angular app, keep:
- `npm run build` as the CI build command.
- build output under `dist/`.
- Playwright config at `code/frontend/frontend/playwright.config.mjs`.
