// IndexNow: tells Bing (which powers ChatGPT search and Copilot), Yandex and
// other participating engines the moment a page changes, instead of waiting
// for a crawl. The key is public by design and verified via /<key>.txt.
//
//   node scripts/indexnow.mjs manifest          -> dist/page-hashes.json
//   node scripts/indexnow.mjs submit <old.json> -> POST pages whose HTML changed
//                                                 (all pages if <old.json> is missing)
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative } from 'node:path';

const KEY = 'f6506e653f16b1b2142cb0a0f6fe8804';
const HOST = 'www.legendary-retreats.com';
const DIST = new URL('../dist', import.meta.url).pathname;

const walk = (d) => readdirSync(d).flatMap((f) => {
  const p = join(d, f);
  return statSync(p).isDirectory() ? walk(p) : [p];
});

function manifest() {
  const pages = {};
  for (const f of walk(DIST).filter((f) => f.endsWith('index.html'))) {
    const url = '/' + relative(DIST, f).replace(/index\.html$/, '');
    pages[url] = createHash('sha256').update(readFileSync(f)).digest('hex').slice(0, 16);
  }
  writeFileSync(join(DIST, 'page-hashes.json'), JSON.stringify(pages));
  console.log(`indexnow: manifest of ${Object.keys(pages).length} pages`);
}

async function submit(oldFile) {
  const now = JSON.parse(readFileSync(join(DIST, 'page-hashes.json'), 'utf8'));
  let old = {};
  try { if (oldFile && existsSync(oldFile)) old = JSON.parse(readFileSync(oldFile, 'utf8')); } catch { old = {}; }
  const changed = Object.keys(now).filter((u) => old[u] !== now[u]);
  if (!changed.length) return console.log('::notice::IndexNow: no changed pages');
  const urlList = changed.map((u) => `https://${HOST}${u}`);
  const res = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host: HOST, key: KEY, keyLocation: `https://${HOST}/${KEY}.txt`, urlList }),
  });
  const ok = res.status === 200 || res.status === 202;
  console.log(`::${ok ? 'notice' : 'warning'}::IndexNow: submitted ${urlList.length} URL(s), HTTP ${res.status}`);
  urlList.slice(0, 20).forEach((u) => console.log('  ' + u));
  // 200/202 = accepted. Anything else is reported but never fails the deploy.
}

const [cmd, arg] = process.argv.slice(2);
if (cmd === 'manifest') manifest();
else if (cmd === 'submit') await submit(arg);
else { console.error('usage: indexnow.mjs manifest | submit <old.json>'); process.exit(1); }
