import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    // 지정하지 않으면 본문 첫 문단에서 자동 추출된다 (src/utils/seo.ts)
    description: z.string().optional(),
    comments: z.boolean().default(false),
    categories: z.array(z.string()).default(['Blog']),
    tags: z.array(z.string()).default([]),
    last_modified_at: z.string().optional(),
    toc: z.boolean().default(true),
    image: z.string().optional(),
    use_math: z.boolean().default(false),
  }),
});

/**
 * YAML은 따옴표 없는 2026-08-26 을 Date 객체로 파싱한다. 원고를 몇 달에 걸쳐 쓰면서
 * 따옴표를 매번 기억하게 만들 이유가 없으니 양쪽 다 받아 ISO 문자열로 통일한다.
 */
const looseDate = z
  .union([z.string(), z.date()])
  .transform((v) => (typeof v === 'string' ? v.trim() : v.toISOString()));

/**
 * 온라인 책. 블로그와 분리해 둔다.
 * 블로그는 날짜순·평면·RSS 중심이고 책은 순서·계층 중심이라, 한 컬렉션에 섞으면
 * archive·tags·rss·sitemap lastmod·prev/next가 전부 책 항목까지 끌어안게 된다.
 *
 * 파일 경로가 곧 구조다: src/content/book/<책>/<NN-부>/<NN-장>.md
 * id는 확장자만 떼고 경로를 그대로 쓴다 (예: 'llm-serving/01-basics/02-batching').
 * 숫자 접두사는 순서 결정에만 쓰고 URL에서는 떨어진다 (src/utils/book.ts).
 */
const book = defineCollection({
  loader: glob({
    pattern: '**/*.{md,mdx}',
    base: './src/content/book',
    generateId: ({ entry }) => entry.replace(/\.(md|mdx)$/, ''),
  }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    last_modified_at: looseDate.optional(),
    toc: z.boolean().default(true),
    use_math: z.boolean().default(false),
    // 초안은 목차와 sitemap에서 빠진다
    draft: z.boolean().default(false),
  }),
});

/** 책 한 권의 메타. src/content/book/<책>/book.yaml */
const bookMeta = defineCollection({
  loader: glob({
    pattern: '**/book.yaml',
    base: './src/content/book',
    generateId: ({ entry }) => entry.replace(/\/book\.yaml$/, ''),
  }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    description: z.string(),
    author: z.string().default('froggydisk'),
    cover: z.string().optional(),
    status: z.enum(['writing', 'done']).default('writing'),
    // 레이아웃 검증용 더미. 배지가 붙고 noindex + sitemap 제외로 나간다.
    sample: z.boolean().default(false),
    // 날짜 폴백의 바닥. 빌드 시각을 쓰면 sitemap lastmod가 매 배포마다 흔들린다.
    published: looseDate,
    last_modified_at: looseDate.optional(),
    // 디렉터리 이름(접두사 포함)에 붙일 부(部) 제목. 없으면 디렉터리 이름을 그대로 쓴다.
    parts: z
      .array(
        z.object({
          dir: z.string(),
          title: z.string(),
          /** 목차의 부 제목 옆 아이콘. astro-icon 이름 (예: 'lucide:cpu') */
          icon: z.string().optional(),
        })
      )
      .default([]),
  }),
});

export const collections = { blog, book, bookMeta };
