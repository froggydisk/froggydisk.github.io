import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import icon from 'astro-icon';
import { unified } from '@astrojs/markdown-remark';
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
  'third-post': 'mobile-hover-remove',
  'fourth-post': 'tensor-mutable-copy',
  'fifth-post': 'ios-review-status-discord',
  'sixth-post': 'mobile-tap-highlight-remove',
  'seventh-post': 'buy-me-a-coffee-button',
  'eighth-post': 'search-console-redirect-error',
  'nineth-post': 'rn-hide-bottom-tab-navigator',
  'tenth-post': 'rn-draggable-button-scrollview',
  'eleventh-post': 'rn-android-gradle-plugin-error',
  'twelveth-post': 'multer-enoent-error',
  'thirteenth-post': 'rn-fetched-image-not-rendering',
  'fourteenth-post': 'rn-ios-blank-screen',
  'fifteenth-post': 'rn-unmountonblur-safeareaview',
  'sixteenth-post': 'rn-ios-firebase-push-errors',
  'seventeenth-post': 'k8s-harbor-image-push',
  'eighteenth-post': 'k8s-jenkins-credential-error',
  'nineteenth-post': 'k8s-private-registry-pull-fail',
  '20th-post': 'ubuntu-nvidia-driver-ssh-error',
  '21th-post': 'jenkins-docker-build-issues',
  '22th-post': 'rn-calendar-implementation',
  '23th-post': 'pyqt5-m1-mac-install-error',
  '24th-post': 'rn-android-studio-no-module',
  '25th-post': 'k8s-add-worker-node',
  '26th-post': 'rn-textinput-string-to-number',
  '27th-post': 'rn-android-darkmode-text-color',
  '28th-post': 'rn-auth-navigation-branching',
  '29th-post': 'rn-logical-and-text-error',
  '30th-post': 'rn-rounded-triangle',
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

const lastmodMap = buildLastmodMap();
const latestPost = [...lastmodMap.values()].sort().at(-1);
const redirectUrls = new Set(Object.keys(redirects).map((p) => `${SITE}${p}/`));

export default defineConfig({
  site: SITE,
  redirects,
  integrations: [
    sitemap({
      // 리다이렉트 스텁과 404는 색인 대상이 아니다
      filter: (page) => !redirectUrls.has(page) && !page.includes('/404'),
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
      rehypePlugins: [
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: 'prepend', properties: { class: 'anchor-head' } }],
        // Astro는 rehype-raw를 사용자 플러그인 "뒤"에 돌린다. 그래서 본문에 손으로 쓴
        // <img> 같은 raw HTML이 아래 rehypeImageAttrs에게는 아직 element로 안 보인다.
        // 먼저 파싱해두면 raw HTML 이미지도 같은 처리를 받는다.
        rehypeRaw,
        rehypeImageAttrs,
      ],
    }),
  },
});
