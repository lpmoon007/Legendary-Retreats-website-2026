// Smaller copies of every large photo, so phones download a phone-sized hero.
// Writes <name>-800w.webp (and -1280w for sources wider than 1600) next to each
// source under public/assets; scripts/generate.mjs adds them to the hero
// <img> as srcset. Generated files are gitignored and rebuilt only when missing
// or older than their source.
import sharp from 'sharp';
import { readdirSync, statSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname;
const ASSETS = join(ROOT, 'public/assets');
export const VARIANT_WIDTHS = [800, 1280];
const VARIANT = /-\d+w\.webp$/;

const walk = (d) => readdirSync(d).flatMap((f) => {
  const p = join(d, f);
  return statSync(p).isDirectory() ? (f === 'og' ? [] : walk(p)) : [p];
});

let made = 0;
for (const src of walk(ASSETS).filter((f) => f.endsWith('.webp') && !VARIANT.test(f))) {
  const { width } = await sharp(src).metadata();
  for (const w of VARIANT_WIDTHS) {
    if (width < w * 1.25) continue;
    const out = src.replace(/\.webp$/, `-${w}w.webp`);
    if (existsSync(out) && statSync(out).mtimeMs >= statSync(src).mtimeMs) continue;
    await sharp(src).resize({ width: w }).webp({ quality: 74, effort: 5 }).toFile(out);
    made++;
  }
}
console.log(`image-variants: ${made} written`);
