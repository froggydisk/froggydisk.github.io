import { getCollection } from 'astro:content';
import { postSlug, modifiedDate } from '../utils/seo';
import {
  bookHref,
  bookModified,
  bookOf,
  chapterHref,
  chapterModified,
  sortChapters,
} from '../utils/book';

/**
 * 인덱스를 거치지 않는 단일 sitemap.
 *
 * @astrojs/sitemap은 sitemap-index.xml + sitemap-0.xml 두 단계로 만든다.
 * 인덱스를 읽고 자식을 다시 가져오는 과정에서 실패하는 크롤러가 있어서,
 * 같은 URL 목록을 한 파일에 담은 관례적인 주소(/sitemap.xml)를 함께 제공한다.
 *
 * 제외 대상은 astro.config.mjs의 sitemap filter와 같다.
 * 리다이렉트 스텁, 404, sample 표시된 책의 하위 페이지는 넣지 않는다.
 */

const STATIC_PATHS = [
  '/',
  '/about/',
  '/archive/',
  '/projects/',
  '/resume/',
  '/privacy-policy/',
  '/tags/',
  '/books/',
];

function entry(site: URL, path: string, lastmod?: Date): string {
  const loc = new URL(path, site).href;
  const mod = lastmod ? `<lastmod>${lastmod.toISOString()}</lastmod>` : '';
  return `<url><loc>${loc}</loc>${mod}</url>`;
}

export async function GET(context: { site: URL }) {
  const site = context.site;
  const posts = await getCollection('blog');

  const postEntries = posts
    .map((post) => ({
      path: `/${postSlug(post.id)}/`,
      lastmod: modifiedDate(post.id, post.data.last_modified_at),
    }))
    .sort((a, b) => b.lastmod.getTime() - a.lastmod.getTime());

  // 루트는 가장 최근에 손댄 글의 날짜를 쓴다
  const latest = postEntries[0]?.lastmod;

  /*
   * 책 표지와 장. astro.config.mjs의 sitemap filter와 같은 것을 걸러낸다.
   * 이 목록이 빠지면 제출용 sitemap.xml과 sitemap-0.xml의 URL 수가 어긋난다.
   */
  const metas = await getCollection('bookMeta');
  const publishedChapters = (await getCollection('book')).filter((c) => !c.data.draft);
  const bookEntries: { path: string; lastmod: Date }[] = [];

  for (const meta of metas) {
    if (meta.data.sample) continue; // 샘플 책은 noindex로 나간다
    const mine = sortChapters(publishedChapters.filter((c) => bookOf(c.id) === meta.id));
    if (mine.length === 0) continue; // 장이 하나도 없으면 라우트도 생기지 않는다

    bookEntries.push({ path: bookHref(meta.id), lastmod: bookModified(mine, meta) });
    for (const chapter of mine) {
      bookEntries.push({
        path: chapterHref(chapter.id),
        lastmod: chapterModified(chapter, meta),
      });
    }
  }

  const body = [
    ...STATIC_PATHS.map((p) => entry(site, p, p === '/' ? latest : undefined)),
    ...postEntries.map((p) => entry(site, p.path, p.lastmod)),
    ...bookEntries.map((p) => entry(site, p.path, p.lastmod)),
  ].join('');

  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?>` +
      `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${body}</urlset>`,
    {
      headers: {
        'Content-Type': 'application/xml; charset=utf-8',
      },
    }
  );
}
