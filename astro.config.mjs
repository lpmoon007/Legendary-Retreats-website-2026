// @ts-check
import { defineConfig } from 'astro/config';
import preact from '@astrojs/preact';

// Static site for Legendary Retreats. Output is plain static HTML served by
// nginx on the GoDaddy VPS (see DEPLOY.md). The only interactive island is the
// "Pick your level of Legendary" dial on /ways-to-work-together.
export default defineConfig({
  site: 'https://www.legendary-retreats.com',
  output: 'static',
  integrations: [preact()],
  build: {
    // Emit /slug/index.html so clean URLs work with nginx try_files.
    format: 'directory',
  },
  // The design is intentionally inline-styled; no global CSS pipeline needed.
});
