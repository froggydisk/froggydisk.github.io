import { readdirSync, readFileSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import icon from 'astro-icon';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypeRaw from 'rehype-raw';
import rehypeImageAttrs from './src/plugins/rehype-image-attrs.mjs';

const SITE = 'https://froggydisk.github.io';

/**
 * 2026-08 슬러그 정비: 의미 없는 순번 슬러그를 주제 기반 슬러그로 교체하면서
 * 기존 색인 URL을 잃지 않도록 리다이렉트를 남긴다. (정적 빌드에서는 meta refresh + canonical)
 */
const LEGACY_SLUGS = {
  'second-post': 'top1-top5-accuracy',
  'assignment': 'cam-class-activation-map',
  'third-post': 'mobile-touch-interaction',
  'fourth-post': 'tensor-mutable-copy',
  'fifth-post': 'ios-review-status-discord',
  'sixth-post': 'mobile-touch-interaction',
  'seventh-post': 'buy-me-a-coffee-button',
  'eighth-post': 'search-console-redirect-error',
  'nineth-post': 'rn-hide-bottom-tab-navigator',
  'tenth-post': 'rn-overlapping-layers',
  'eleventh-post': 'rn-silent-failures',
  'twelveth-post': 'rn-image-upload-pipeline',
  'thirteenth-post': 'rn-image-upload-pipeline',
  'fourteenth-post': 'rn-silent-failures',
  'fifteenth-post': 'rn-overlapping-layers',
  'sixteenth-post': 'rn-ios-firebase-push-errors',
  'seventeenth-post': 'harbor-registry-troubleshooting',
  'eighteenth-post': 'k8s-jenkins-credential-error',
  'nineteenth-post': 'harbor-registry-troubleshooting',
  '20th-post': 'ubuntu-nvidia-driver-ssh-error',
  '21th-post': 'jenkins-docker-build-issues',
  '22th-post': 'rn-calendar-implementation',
  '23th-post': 'pyqt5-m1-mac-install-error',
  '24th-post': 'rn-silent-failures',
  '25th-post': 'k8s-add-worker-node',
  '26th-post': 'rn-textinput-string-to-number',
  '27th-post': 'rn-silent-failures',
  '28th-post': 'rn-auth-navigation-branching',
  '29th-post': 'jsx-curly-braces',
  '30th-post': 'rn-rounded-triangle',

  // 2026-08 정리: 짧은 글을 주제별로 합치면서 생긴 리다이렉트
  'rn-logical-and-text-error': 'jsx-curly-braces',
  'return-in-map': 'jsx-curly-braces',
  'arrow-in-onpress': 'jsx-curly-braces',
  'transmit-component': 'jsx-curly-braces',
  'next-br': 'jsx-curly-braces',
  'absolute-panel': 'rn-overlapping-layers',
  'z-index': 'rn-overlapping-layers',
  'fixed-position': 'rn-overlapping-layers',
  'rn-unmountonblur-safeareaview': 'rn-overlapping-layers',
  'rn-draggable-button-scrollview': 'rn-overlapping-layers',
  'rn-android-studio-no-module': 'rn-silent-failures',
  'hot-reload': 'rn-silent-failures',
  'rn-ios-blank-screen': 'rn-silent-failures',
  'rn-android-darkmode-text-color': 'rn-silent-failures',
  'rn-android-gradle-plugin-error': 'rn-silent-failures',
  'harbor-core-error': 'harbor-registry-troubleshooting',
  'k8s-private-registry-pull-fail': 'harbor-registry-troubleshooting',
  'k8s-harbor-image-push': 'harbor-registry-troubleshooting',
  'multer-enoent-error': 'rn-image-upload-pipeline',
  'rn-fetched-image-not-rendering': 'rn-image-upload-pipeline',
  'mobile-tap-highlight-remove': 'mobile-touch-interaction',
  'mobile-hover-remove': 'mobile-touch-interaction',
};

const redirects = Object.fromEntries(
  Object.entries(LEGACY_SLUGS).map(([from, to]) => [`/${from}`, `/${to}/`])
);

/** 포스트 파일에서 마지막 수정일을 읽어 sitemap lastmod로 쓸 맵을 만든다. */
function buildLastmodMap() {
  const dir = fileURLToPath(new URL('./src/content/blog', import.meta.url));
  const map = new Map();
  for (const file of readdirSync(dir)) {
    if (!/\.(md|mdx)$/.test(file)) continue;
    const published = file.slice(0, 10);
    const slug = file.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.(md|mdx)$/, '');
    const raw = readFileSync(`${dir}/${file}`, 'utf-8');
    const match = raw.match(/^last_modified_at:\s*["']?([^"'\n]+)["']?\s*$/m);
    const candidate = match ? new Date(match[1].trim().replace(' ', 'T')) : null;
    const date =
      candidate && !Number.isNaN(candidate.getTime())
        ? candidate
        : new Date(`${published}T00:00:00Z`);
    map.set(`${SITE}/${slug}/`, date.toISOString());
  }
  return map;
}

/**
 * 책의 장 파일에서 lastmod를 읽는다. 날짜 폴백은 src/utils/book.ts와 같은 순서다:
 * 장 last_modified_at → 책 last_modified_at → 책 published.
 * 파일 mtime은 쓰지 않는다. CI 체크아웃이 mtime을 전부 배포 시각으로 만든다.
 */
function readField(raw, key) {
  const m = raw.match(new RegExp(`^${key}:\\s*["']?([^"'\\n]+)["']?\\s*$`, 'm'));
  return m ? m[1].trim() : null;
}

function looseDate(raw) {
  if (!raw) return null;
  let v = raw.replace(' ', 'T').replace(/T$/, '');
  if (/^\d{4}-\d{2}-\d{2}$/.test(v)) v += 'T00:00:00Z';
  else if (!/(Z|[+-]\d{2}:?\d{2})$/.test(v)) v += 'Z';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? null : d;
}

function walkMarkdown(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = `${dir}/${name}`;
    if (statSync(full).isDirectory()) walkMarkdown(full, out);
    else if (/\.(md|mdx)$/.test(name)) out.push(full);
  }
  return out;
}

/** sample: true 인 책의 URL 접두사. 색인 대상이 아니다. */
const sampleBookPrefixes = new Set();

function addBookLastmod(map) {
  const root = fileURLToPath(new URL('./src/content/book', import.meta.url));
  let allDates = [];

  let books;
  try {
    books = readdirSync(root).filter((n) => statSync(`${root}/${n}`).isDirectory());
  } catch {
    return; // 책이 아직 없으면 조용히 넘어간다
  }

  for (const book of books) {
    const dir = `${root}/${book}`;
    let meta = '';
    try {
      meta = readFileSync(`${dir}/book.yaml`, 'utf-8');
    } catch {
      continue; // book.yaml 없는 디렉터리는 책이 아니다
    }

    if (readField(meta, 'sample') === 'true') {
      sampleBookPrefixes.add(`${SITE}/books/${book}/`);
    }

    const bookFallback =
      looseDate(readField(meta, 'last_modified_at')) ?? looseDate(readField(meta, 'published'));

    const chapterDates = [];
    for (const file of walkMarkdown(dir)) {
      const raw = readFileSync(file, 'utf-8');
      if (readField(raw, 'draft') === 'true') continue;

      const date = looseDate(readField(raw, 'last_modified_at')) ?? bookFallback;
      if (!date) continue;

      // 파일 경로 → URL. 세그먼트마다 숫자 접두사를 뗀다 (src/utils/book.ts와 동일)
      const rel = file.slice(dir.length + 1).replace(/\.(md|mdx)$/, '');
      const path = rel.split('/').map((seg) => seg.replace(/^\d+[-_.]/, '')).join('/');

      map.set(`${SITE}/books/${book}/${path}/`, date.toISOString());
      chapterDates.push(date);
    }

    if (chapterDates.length) {
      const latest = new Date(Math.max(...chapterDates.map((d) => d.getTime())));
      map.set(`${SITE}/books/${book}/`, latest.toISOString());
      allDates.push(latest);
    }
  }

  if (allDates.length) {
    map.set(
      `${SITE}/books/`,
      new Date(Math.max(...allDates.map((d) => d.getTime()))).toISOString()
    );
  }
}

const lastmodMap = buildLastmodMap();
// 목록 페이지의 lastmod는 블로그 최신 글을 따라간다. 책을 넣기 전에 뽑아야 한다.
const latestPost = [...lastmodMap.values()].sort().at(-1);
addBookLastmod(lastmodMap);
const redirectUrls = new Set(Object.keys(redirects).map((p) => `${SITE}${p}/`));

export default defineConfig({
  site: SITE,
  redirects,
  integrations: [
    sitemap({
      // 리다이렉트 스텁·404·샘플 책은 색인 대상이 아니다
      filter: (page) =>
        !redirectUrls.has(page) &&
        !page.includes('/404') &&
        ![...sampleBookPrefixes].some((prefix) => page.startsWith(prefix)),
      serialize(item) {
        const lastmod = lastmodMap.get(item.url);
        if (lastmod) {
          item.lastmod = lastmod;
        } else if (
          item.url === `${SITE}/` ||
          item.url === `${SITE}/archive/` ||
          item.url === `${SITE}/tags/`
        ) {
          // 목록 페이지는 최신 글 발행 시점을 따라간다
          item.lastmod = latestPost;
        }
        return item;
      },
    }),
    mdx(),
    icon(),
  ],
  markdown: {
    shikiConfig: {
      theme: 'one-dark-pro',
    },
    processor: unified({
      // 수식은 빌드 시점에 렌더링한다. 예전에는 MathJax 2.7.6 을 cdnjs 에서 런타임에
      // 불러왔는데(글 1편당 약 500KB), 정작 MathJax 2 는 인라인 $ 를 기본으로 끄기 때문에
      // 본문의 $f_k(x,y)$ 같은 수식이 원본 LaTeX 그대로 노출되고 있었다.
      // KaTeX 의 MathML 출력을 쓰면 런타임 JS·CSS·웹폰트가 모두 0 이고
      // 브라우저가 직접 그리므로 선택·스크린리더도 된다.
      remarkPlugins: [remarkMath],
      rehypePlugins: [
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: 'prepend', properties: { class: 'anchor-head' } }],
        // Astro는 rehype-raw를 사용자 플러그인 "뒤"에 돌린다. 그래서 본문에 손으로 쓴
        // <img> 같은 raw HTML이 아래 rehypeImageAttrs에게는 아직 element로 안 보인다.
        // 먼저 파싱해두면 raw HTML 이미지도 같은 처리를 받는다.
        rehypeRaw,
        rehypeImageAttrs,
        [rehypeKatex, { output: 'mathml', strict: false, throwOnError: false }],
      ],
    }),
  },
});
