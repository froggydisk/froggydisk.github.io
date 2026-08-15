import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import icon from 'astro-icon';
import { unified } from '@astrojs/markdown-remark';
import rehypeSlug from 'rehype-slug';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';

export default defineConfig({
  site: 'https://froggydisk.github.io',
  integrations: [sitemap(), mdx(), icon()],
  markdown: {
    shikiConfig: {
      theme: 'one-dark-pro',
    },
    processor: unified({
      rehypePlugins: [
        rehypeSlug,
        [rehypeAutolinkHeadings, { behavior: 'prepend', properties: { class: 'anchor-head' } }],
      ],
    }),
  },
});
