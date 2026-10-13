#!/usr/bin/env node
// node tools/build-constellations.mjs data/constellations.json docs/constellations

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const [inputPath = "data/constellations.json", outDir = 'docs/constellations_svg'] = process.argv.slice(2);

const PAD = 28, STAR_SCALE = 2.4, LINE_WIDTH = 1.2;
const BG = '#f5f6fa', STAR = '#0f1226', LINE = '#9aa0c4', HALO = '#1cb0f5';
const f = n => +Number(n).toFixed(2);
const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));

function buildSvg(c) {
  const { stars, lines, id, name = id } = c;

  const xs = stars.map(s => s.x), ys = stars.map(s => s.y);
  let minX = Math.min(...xs) - PAD, maxX = Math.max(...xs) + PAD;
  let minY = Math.min(...ys) - PAD, maxY = Math.max(...ys) + PAD;

  const w0 = maxX - minX, h0 = maxY - minY;
  if (w0 > h0) { const d = (w0 - h0) / 2; minY -= d; maxY += d; }
  else         { const d = (h0 - w0) / 2; minX -= d; maxX += d; }

  const w = maxX - minX, h = maxY - minY;

  const lineEls = lines.map(([a, b]) => {
    const A = stars[a], B = stars[b];
    if (!A || !B) return '';
    return `<line x1="${f(A.x)}" y1="${f(A.y)}" x2="${f(B.x)}" y2="${f(B.y)}"/>`;
  }).join('');

  const haloEls = stars.map(s => {
    const r = (s.r ?? 2) * STAR_SCALE;
    return `<circle cx="${f(s.x)}" cy="${f(s.y)}" r="${f(r * 2.6)}"/>`;
  }).join('');

  const starEls = stars.map(s =>
    `<circle cx="${f(s.x)}" cy="${f(s.y)}" r="${f((s.r ?? 2) * STAR_SCALE)}"/>`
  ).join('');

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${f(minX)} ${f(minY)} ${f(w)} ${f(h)}" ` +
    `width="${Math.round(w)}" height="${Math.round(h)}" role="img" aria-label="Star chart of ${esc(name)}">
<title>${esc(name)}</title>
<defs>
<radialGradient id="halo">
<stop offset="0%" stop-color="${HALO}" stop-opacity="0.55"/>
<stop offset="60%" stop-color="${HALO}" stop-opacity="0.15"/>
<stop offset="100%" stop-color="${HALO}" stop-opacity="0"/>
</radialGradient>
</defs>
<rect x="${f(minX)}" y="${f(minY)}" width="${f(w)}" height="${f(h)}" fill="${BG}"/>
<g stroke="${LINE}" stroke-width="${LINE_WIDTH}" stroke-linecap="round">${lineEls}</g>
<g fill="url(#halo)">${haloEls}</g>
<g fill="${STAR}">${starEls}</g>
</svg>
`;
}

const data = JSON.parse(readFileSync(inputPath, 'utf8'));
mkdirSync(outDir, { recursive: true });

for (const c of data) {
  writeFileSync(join(outDir, `${c.id}.svg`), buildSvg(c));
}
console.log(`✓ ${data.length} charts → ${outDir}/`);