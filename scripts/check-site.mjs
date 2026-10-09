#!/usr/bin/env node
/**
 * 빌드 결과(dist/)의 SEO·링크 검사. `npm run build` 다음에 돌린다.
 *
 *   node scripts/check-site.mjs [dist]
 *
 * 오류가 하나라도 있으면 종료 코드 1로 끝나 CI 배포를 막는다.
 * 경고는 출력만 한다.
 *
 * 왜 있는가: 콘솔에 아무 말 없이 깨지는 것들이 반복됐다.
 *  - sitemap.xml(손으로 만듦)과 sitemap-0.xml(@astrojs/sitemap)의 URL이
 *    56 vs 128로 어긋난 채 배포됐다 (c200f77).
 *  - 뼈대 장 70개가 sitemap의 41%를 차지하고 있었다 (src/utils/stub.mjs).
 * 의존성 없이 정규식으로 읽는다. 빌드 결과는 Astro가 만든 HTML이라 형태가 일정하다.
 */
import { readdirSync, readFileSync, statSync, existsSync } from 'node:fs';
import path from 'node:path';

const DIST = path.resolve(process.argv[2] ?? 'dist');
const SITE = 'https://froggydisk.github.io';

/** 검사하지 않는 파일. 서치콘솔 소유 확인 파일은 일반 페이지가 아니다 */
const SKIP = [/^\/google[0-9a-f]+\.html$/, /^\/pagefind\//];

const errors = [];
const warnings = [];
const err = (rule, msg) => errors.push(`[${rule}] ${msg}`);
const warn = (rule, msg) => warnings.push(`[${rule}] ${msg}`);

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = path.join(dir, name);
    if (statSync(full).isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

const files = new Set(walk(DIST).map((f) => '/' + path.relative(DIST, f).split(path.sep).join('/')));

/** dist 안에 그 경로로 응답할 파일이 있는가 (GitHub Pages 규칙) */
function exists(urlPath) {
  const p = decodeURI(urlPath.split('#')[0].split('?')[0]);
  if (!p) return true;
  if (p.endsWith('/')) return files.has(p + 'index.html');
  return files.has(p) || files.has(p + '.html') || files.has(p + '/index.html');
}

const unescape = (s) =>
  s.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>');

function attr(tag, name) {
  const m = tag.match(new RegExp(`\\s${name}=(?:"([^"]*)"|'([^']*)'|([^\\s>]+))`, 'i'));
  return m ? unescape(m[1] ?? m[2] ?? m[3]) : null;
}

function meta(html, key) {
  const out = [];
  for (const tag of html.match(/<meta\b[^>]*>/gi) ?? []) {
    if (attr(tag, 'name') === key || attr(tag, 'property') === key) out.push(attr(tag, 'content'));
  }
  return out;
}

/* ── 페이지 수집 ─────────────────────────────────────────── */

const pages = new Map(); // url path → { html, indexable }
for (const f of files) {
  if (!f.endsWith('.html') || SKIP.some((re) => re.test(f))) continue;
  const html = readFileSync(path.join(DIST, f), 'utf-8');
  // LEGACY_SLUGS 리다이렉트 스텁 (meta refresh + noindex)
  if (/http-equiv="refresh"/i.test(html) && !/<html\b/i.test(html.slice(0, 300))) continue;
  const url = f.endsWith('index.html') ? f.slice(0, -'index.html'.length) : f;
  const robots = meta(html, 'robots')[0] ?? '';
  pages.set(url, { html, indexable: !/noindex/i.test(robots) });
}

/* ── 페이지별 검사 ───────────────────────────────────────── */

const titles = new Map();
const descs = new Map();

for (const [url, { html, indexable }] of pages) {
  const title = unescape(html.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.trim() ?? '');
  const desc = meta(html, 'description')[0];

  if (!title) err('title', `${url} 제목 없음`);
  if (!desc) err('description', `${url} description 없음`);
  if (!/<html\b[^>]*\slang="/i.test(html)) err('lang', `${url} <html lang> 없음`);

  const canon = (html.match(/<link\b[^>]*rel="canonical"[^>]*>/gi) ?? []).map((t) => attr(t, 'href'));
  if (canon.length !== 1) err('canonical', `${url} canonical ${canon.length}개`);
  else if (indexable && canon[0] !== SITE + url) err('canonical', `${url} → ${canon[0]}`);

  for (const m of html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi)) {
    try {
      JSON.parse(m[1]);
    } catch (e) {
      err('json-ld', `${url} 파싱 실패: ${e.message}`);
    }
  }

  for (const img of html.match(/<img\b[^>]*>/gi) ?? []) {
    if (attr(img, 'alt') === null) err('img-alt', `${url} alt 없음: ${attr(img, 'src')}`);
  }

  for (const tag of html.match(/<a\b[^>]*>/gi) ?? []) {
    let href = attr(tag, 'href');
    if (!href) continue;
    if (href.startsWith(SITE)) href = href.slice(SITE.length) || '/';
    if (!href.startsWith('/') || href.startsWith('//')) continue;
    if (!exists(href)) err('broken-link', `${url} → ${href}`);
    else {
      const p = href.split('#')[0];
      // 확장자 없는 경로에 슬래시가 빠지면 GitHub Pages가 301을 한 번 거친다
      if (p && !p.endsWith('/') && !/\.[a-z0-9]+$/i.test(p)) warn('trailing-slash', `${url} → ${href}`);
    }
  }

  if (!indexable) continue;

  if (title.length > 70) warn('title-length', `${url} ${title.length}자`);
  if (desc && desc.length > 160) warn('description-length', `${url} ${desc.length}자`);
  if (!/application\/ld\+json/.test(html)) warn('json-ld', `${url} 구조화 데이터 없음`);
  for (const key of ['og:title', 'og:description', 'og:image', 'og:url']) {
    if (!meta(html, key).length) err('open-graph', `${url} ${key} 없음`);
  }
  const ogImage = meta(html, 'og:image')[0];
  if (ogImage?.startsWith(SITE) && !exists(ogImage.slice(SITE.length))) err('og-image', `${url} → ${ogImage}`);

  titles.set(title, [...(titles.get(title) ?? []), url]);
  if (desc) descs.set(desc, [...(descs.get(desc) ?? []), url]);
}

for (const [t, urls] of titles) if (urls.length > 1) err('duplicate-title', `"${t}" ${urls.join(', ')}`);
for (const [d, urls] of descs) if (urls.length > 1) err('duplicate-description', `"${d.slice(0, 40)}…" ${urls.join(', ')}`);

/* ── sitemap ─────────────────────────────────────────────── */

function locs(file) {
  const p = path.join(DIST, file);
  if (!existsSync(p)) {
    err('sitemap', `${file} 없음`);
    return new Set();
  }
  return new Set([...readFileSync(p, 'utf-8').matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]));
}

// 제출용 단일 파일과 @astrojs/sitemap 산출물. 어긋나면 안 된다 (CLAUDE.md 'Sitemap')
const submitted = locs('sitemap.xml');
const generated = locs('sitemap-0.xml');
for (const u of submitted) if (!generated.has(u)) err('sitemap-mismatch', `sitemap.xml에만 있음: ${u}`);
for (const u of generated) if (!submitted.has(u)) err('sitemap-mismatch', `sitemap-0.xml에만 있음: ${u}`);

for (const u of submitted) {
  const page = pages.get(u.slice(SITE.length));
  if (!page) err('sitemap', `페이지 없음: ${u}`);
  else if (!page.indexable) err('sitemap', `noindex 페이지가 sitemap에 있음: ${u}`);
}
for (const [url, { indexable }] of pages) {
  if (indexable && !submitted.has(SITE + url)) err('sitemap', `색인 대상인데 sitemap에 없음: ${url}`);
}

const robots = existsSync(path.join(DIST, 'robots.txt')) ? readFileSync(path.join(DIST, 'robots.txt'), 'utf-8') : '';
if (!robots.includes(`Sitemap: ${SITE}/sitemap.xml`)) err('robots', 'robots.txt가 sitemap.xml을 알리지 않음');
if (/sitemap-index\.xml/.test(robots)) err('robots', 'robots.txt에 sitemap-index.xml이 있음 (서치콘솔이 못 읽는다)');

/* ── 출력 ───────────────────────────────────────────────── */

const indexable = [...pages.values()].filter((p) => p.indexable).length;
console.log(`페이지 ${pages.size}개 (색인 ${indexable}) · sitemap ${submitted.size}개`);

const group = (list) => {
  const by = new Map();
  for (const line of list) {
    const rule = line.match(/^\[([^\]]+)\]/)[1];
    by.set(rule, [...(by.get(rule) ?? []), line]);
  }
  return by;
};

for (const [rule, lines] of group(warnings)) {
  console.log(`\n경고 ${rule} (${lines.length})`);
  for (const l of lines.slice(0, 10)) console.log('  ' + l.replace(/^\[[^\]]+\] /, ''));
  if (lines.length > 10) console.log(`  … 외 ${lines.length - 10}건`);
}
for (const [rule, lines] of group(errors)) {
  console.log(`\n오류 ${rule} (${lines.length})`);
  for (const l of lines) console.log('  ' + l.replace(/^\[[^\]]+\] /, ''));
}

if (errors.length) {
  console.log(`\n오류 ${errors.length}건`);
  process.exit(1);
}
console.log('\n오류 없음');
