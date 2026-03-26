import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context: { site: URL }) {
  const posts = (await getCollection('blog'))
    .sort((a, b) => b.id.slice(0, 10).localeCompare(a.id.slice(0, 10)));

  return rss({
    title: 'froggydisk',
    description: 'Frontend, DevOps, ML/DL 관련 기술 블로그',
    site: context.site,
    items: posts.map((post) => {
      const slug = post.id.replace(/^\d{4}-\d{2}-\d{2}-/, '');
      const dateStr = post.id.slice(0, 10);
      return {
        title: post.data.title,
        pubDate: new Date(dateStr + 'T00:00:00'),
        link: `/${slug}/`,
      };
    }),
  });
}
