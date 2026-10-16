// @ts-check
import { defineConfig } from 'astro/config';

// Static site for Legendary Retreats. Output is plain static HTML served by
// nginx on the GoDaddy VPS (see DEPLOY.md). No framework islands: the few
// interactive bits (dial, FAQ accordions, share buttons) are inline scripts.
export default defineConfig({
  site: 'https://www.legendary-retreats.com',
  output: 'static',
  build: {
    // Emit /slug/index.html so clean URLs work with nginx try_files.
    format: 'directory',
  },
  // The design is intentionally inline-styled; no global CSS pipeline needed.
});
