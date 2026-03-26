import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    comments: z.boolean().default(false),
    categories: z.array(z.string()).default(['Blog']),
    tags: z.array(z.string()).default([]),
    last_modified_at: z.string().optional(),
    toc: z.boolean().default(true),
    image: z.string().optional(),
    use_math: z.boolean().default(false),
  }),
});

export const collections = { blog };
