// Build-time: render each source photo in OG_MAP into a 1200x630 JPEG share
// card under public/assets/og/. Runs before generate.mjs in `npm run build`.
// Output is a build artifact (gitignored) — Astro copies public/ into dist/.
// Crop uses sharp's "attention" strategy so portrait sources keep their subject.
import sharp from 'sharp';
import { mkdirSync, existsSync } from 'node:fs';
import { dirname, join, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { OG_MAP } from './og-map.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = join(ROOT, 'public', 'assets');
const OUT = join(ASSETS, 'og');
mkdirSync(OUT, { recursive: true });

const sources = [...new Set(Object.values(OG_MAP))];
let made = 0;
for (const src of sources) {
  const inFile = join(ASSETS, `${src}.webp`);
  if (!existsSync(inFile)) {
    console.error(`OG source missing: ${src}.webp`);
    process.exit(1);
  }
  const outFile = join(OUT, `${basename(src)}.jpg`);
  await sharp(inFile)
    .resize(1200, 630, { fit: 'cover', position: 'attention' })
    .jpeg({ quality: 82, mozjpeg: true })
    .toFile(outFile);
  made++;
}
console.log(`Generated ${made} OG images (${Object.keys(OG_MAP).length} pages mapped) -> public/assets/og/`);
