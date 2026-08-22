import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { postSlug, postDate, excerpt } from '../utils/seo';

export async function GET(context: { site: URL }) {
  const posts = (await getCollection('blog'))
    .sort((a, b) => b.id.slice(0, 10).localeCompare(a.id.slice(0, 10)));

  return rss({
    title: 'froggydisk',
    description: 'Frontend, DevOps, ML/DL 관련 기술 블로그. 개발 과정에서의 문제 해결과 새로운 기술을 기록합니다.',
    site: context.site,
    customData: '<language>ko-kr</language>',
    items: posts.map((post) => ({
      title: post.data.title,
      description: post.data.description?.trim() || excerpt(post.body ?? '', 300),
      pubDate: postDate(post.id),
      link: `/${postSlug(post.id)}/`,
      categories: (post.data.tags || []).flatMap((t) => t.split(',').map((s) => s.trim())).filter(Boolean),
    })),
  });
}
