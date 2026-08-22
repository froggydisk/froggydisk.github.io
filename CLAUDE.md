# froggydisk.github.io - Repository Guide

## Project Overview

**froggydisk.github.io** is a personal technical blog and portfolio website built with **Astro 7**, deployed to GitHub Pages. The site features 52+ blog posts covering frontend development, DevOps, ML/DL, and technical problem-solving, with a focus on Korean-language technical content.

- **Primary Language**: Korean (blog content), JavaScript/TypeScript (code)
- **Live Site**: https://froggydisk.github.io
- **License**: MIT (original theme by Mahendrata Harpi)
- **Deployment**: GitHub Pages (automated via GitHub Actions)

---

## Tech Stack

### Core Framework
- **Astro 7.2.2** - Static site generator optimized for performance
- **TypeScript (strict mode)** - Type-safe configuration and components
- **MDX** - Enhanced markdown with component support

### Key Dependencies
```json
{
  "@astrojs/markdown-remark": "^7.2.2", // unified() markdown processor factory
  "@astrojs/mdx": "^7.0.5",        // Markdown + React component rendering
  "@astrojs/rss": "^4.0.19",       // RSS feed generation
  "@astrojs/sitemap": "^3.7.3",    // Sitemap auto-generation
  "astro-icon": "^1.1.5",          // Icon system (Lucide, Phosphor)
  "@iconify-json/lucide": "^1.2.99",
  "@iconify-json/ph": "^1.2.2",
  "pagefind": "^1.4.0",            // Static search indexing
  "rehype-slug": "^6.0.0",         // Auto heading IDs
  "rehype-autolink-headings": "^7.1.0", // Anchor links for headings
  "sass": "^1.98.0"                // CSS preprocessing (devDep)
}
```

### Build & Node
- **Node 22** (from CI/CD config)
- **npm** for package management
- **Shiki (one-dark-pro theme)** for code syntax highlighting

---

## Project Structure

```
froggydisk.github.io/
├── src/
│   ├── pages/                    # Dynamic routing
│   │   ├── index.astro          # Homepage (recent posts)
│   │   ├── [...slug].astro      # Dynamic blog post routing
│   │   ├── archive.astro        # Post archive with search
│   │   ├── about.astro          # 소개 + 연락처 (ProfilePage JSON-LD)
│   │   ├── projects.astro       # 사이드 프로젝트 목록 (구 about.astro)
│   │   ├── resume.astro         # Resume/CV
│   │   ├── privacy-policy.astro # Privacy policy
│   │   ├── 404.astro            # 404 error page
│   │   ├── rss.xml.ts           # RSS feed endpoint
│   │   └── tags/                # 태그별 앵커 목록 페이지 (개별 태그 라우트는 없음)
│   ├── content.config.ts        # Content schema & validation (여기가 실제 위치)
│   ├── utils/
│   │   └── seo.ts               # slug·날짜·태그·description 추출 공용 헬퍼
│   ├── content/
│   │   └── blog/                # 62 markdown/mdx blog posts
│   │       └── YYYY-MM-DD-*.md  # Post naming convention
│   ├── components/              # 14 Astro components
│   │   ├── Navbar.astro        # Navigation + theme toggle
│   │   ├── Footer.astro        # Footer
│   │   ├── TOC.astro           # Table of Contents (scroll-spy)
│   │   ├── Comments.astro      # Disqus comments integration
│   │   ├── PostNav.astro       # Previous/Next post links
│   │   ├── Support.astro       # Ko-fi donation button
│   │   ├── StarBackground.astro # Animated star background
│   │   └── diagrams/           # 9 SVG diagram components
│   │       ├── AgentNetwork.astro
│   │       ├── SystemLayers.astro
│   │       ├── HarnessConcentric.astro
│   │       └── (6 more specialized diagrams)
│   ├── layouts/                 # 2 layout templates
│   │   ├── BaseLayout.astro    # Base HTML + meta tags
│   │   └── PostLayout.astro    # Blog post wrapper
│   └── styles/
│       ├── global.css         # Klisé 유래 베이스 스타일 (팔레트는 웜 뉴트럴로 교체)
│       └── editorial.css     # 타이포그래피·여백·레이아웃 재정의 레이어 (global.css 다음 로드)
├── public/                      # Static assets
│   ├── img/                    # Images (profile.png, etc)
│   ├── favicons/               # Favicon set
│   ├── robots.txt
│   ├── ads.txt
│   └── google*.html            # Google verification files
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions CI/CD
├── astro.config.mjs            # Astro configuration
├── tsconfig.json               # TypeScript configuration
├── package.json                # Dependencies & scripts
├── .gitignore                  # Git ignore rules
└── LICENSE                     # MIT License
```

### Important Files

**Configuration:**
- `astro.config.mjs` - Site URL, markdown settings (Shiki theme: one-dark-pro), integrations
- `tsconfig.json` - Extends Astro strict config, path aliases (`@/*`)
- `content.config.ts` - Zod schema for blog post frontmatter

**Blog Content Schema:**
```typescript
interface BlogPost {
  title: string;              // Post title (required)
  comments: boolean;          // Enable Disqus (default: false)
  categories: string[];       // Post categories (default: ['Blog'])
  tags: string[];            // Post tags (parsed from comma-separated string)
  last_modified_at?: string; // Last update timestamp
  toc: boolean;              // Show table of contents (default: true)
  image?: string;            // Post cover image
  use_math: boolean;         // Load MathJax (default: false)
}
```

---

## Build System & Scripts

### Available Commands
```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build static site + pagefind search index
npm run preview  # Preview built site locally
```

### Build Process
1. **Astro Build**: Generates static HTML/CSS/JS in `/dist`
2. **Pagefind**: Indexes content in `/dist` for static search
3. **Output**: Production-ready site in `/dist` directory

### CI/CD Pipeline (GitHub Actions)

**Workflow**: `.github/workflows/deploy.yml`

**Triggers**:
- Push to `master` branch
- Manual workflow dispatch

**Build Job**:
1. Checkout code
2. Setup Node 22 with npm cache
3. `npm ci` - Clean install dependencies
4. `npm run build` - Build site + pagefind
5. Upload `/dist` artifact to GitHub Pages

**Deploy Job**:
- Uses official `actions/deploy-pages@v4`
- Automatic HTTPS, custom domains supported

**Permissions**: `contents: read`, `pages: write`, `id-token: write`

---

## Key Features & Architecture

### 1. Dynamic Blog Routing
- **Post Naming**: `YYYY-MM-DD-slug-title.md`
- **Slug Generation**: Filename prefix stripped, used as URL path
- **Legacy Slugs**: 2026-08 정비로 순번 슬러그(`second-post`, `20th-post` 등) 30건을 주제 슬러그로 교체.
  구 URL은 `astro.config.mjs`의 `LEGACY_SLUGS`가 리다이렉트(noindex + canonical)를 생성하므로 **절대 삭제하지 말 것**
- **Sort Order**: By date descending (newest first)
- **Navigation**: Automatic prev/next links based on chronological order

### 2. Theme System
- **Light/Dark Mode**: Stored in localStorage — **라이트가 기본** (`theme` 값이 없으면 라이트)
- **CSS Variables**: `data-theme="dark"` attribute on `<body>`; 색·폰트 토큰은 `editorial.css`의
  `:root` / `body[data-theme="dark"]`에 정의 (`--bg`, `--ink`, `--body`, `--muted`, `--rule`, `--accent` …)
- **Palette**: 아이보리 `#faf9f5` / 잉크 `#141413` / 클레이 액센트 `#cc785c`, 다크는 `#191816` / `#f5f3ec` / `#d9836a`
- **Toggle**: Navbar sun/moon icon
- **Diagram Theming**: 10+ CSS variables per diagram component

### 3. Content Enhancement
- **Markdown Plugins**: configured via `markdown.processor` in `astro.config.mjs`.
  Astro 7 deprecated `markdown.remarkPlugins` / `rehypePlugins` / `remarkRehype`;
  pass them to `unified({...})` from `@astrojs/markdown-remark` instead:
  ```js
  import { unified } from '@astrojs/markdown-remark';

  markdown: {
    shikiConfig: { theme: 'one-dark-pro' },   // still a top-level markdown option
    processor: unified({ rehypePlugins: [...] }),
  }
  ```
  - `rehype-slug` - Auto-generate heading IDs
  - `rehype-autolink-headings` - Add anchor links (class: `anchor-head`)
  - `shiki` - Syntax highlighting with one-dark-pro theme
- **Table of Contents**: Scroll-spy with Intersection Observer API
- **Math Support**: Optional MathJax loading per-post
- **Comments**: Disqus integration (per-post toggle)

### 4. Search & Discovery
- **Pagefind**: Static search index built during build
- **Archive Page**: Full post list with fallback search (`<input type="search">`)
- **Tag Pages**: Category-based filtering (auto-generated from post tags)
- **RSS Feed**: Standard RSS feed at `/rss.xml`

### 5. SEO & Social
- **Open Graph Tags**: Site, title, description, image, URL, type
- **Twitter Card**: Summary card format
- **Canonical URLs**: Prevent duplicate content issues
- **Schema.org**: BlogPosting JSON-LD (author Person, publisher, datePublished/dateModified, mainEntityOfPage).
  `/about/`은 ProfilePage. `PostLayout.astro`에서 생성해 `BaseLayout`의 `jsonLd` prop으로 주입
- **Meta Description**: 포스트마다 고유. frontmatter `description`이 있으면 그것을, 없으면
  `src/utils/seo.ts`의 `excerpt()`가 본문 첫 산문 문단에서 자동 추출 (헤딩·코드블록·JSX 제외)
- **Sitemap lastmod**: `astro.config.mjs`가 포스트 frontmatter를 읽어 주입. 리다이렉트·404는 `filter`로 제외
- **Sitemap**: `/sitemap-index.xml` + `/sitemap-0.xml` (`@astrojs/sitemap`은 `sitemap.xml`을 만들지 않는다)
- **Robots.txt**: Allow all, sitemap reference

### 6. Styling Approach
- **No CSS Framework**: Pure vanilla CSS (global.css + editorial.css)
- **Fonts**: 본문·제목 모두 Pretendard(산세리프), 코드 JetBrains Mono
  → `--font-sans`, `--font-mono` 토큰으로 사용 (제목 굵기 600, 목록 제목 450~550)
- **Measure**: 본문 폭 700px (`--measure`), 본문 18px / line-height 1.78
- **Mobile-First**: Responsive breakpoints for tab/mobile
- **Design Pattern**: 편집체(editorial) 지향 — 헤어라인 구분선, 넓은 여백, 박스·그림자 최소화
- **Link Rule**: 본문 링크는 `.page-content a`에서 잉크색 + 클레이 밑줄로 한 곳에서 정의.
  목록·내비게이션 링크(`.post-item-title a`, `.home-post-link`, `.posts-more` 등)는 특이도를 높여 밑줄 제외

### 7. Icon System
- **Library**: astro-icon (integrates Iconify)
- **Collections**:
  - Lucide: Modern, clean icons
  - Phosphor: Alternative icon set
- **Usage**: `<Icon name="lucide:sun" size={22} />`

---

## Development Workflow

### Adding a Blog Post
1. Create file in `/src/content/blog/YYYY-MM-DD-slug.md`
2. Add frontmatter with metadata:
```markdown
---
title: "Post Title"
comments: true
categories: ["Blog"]
tags: ["tag1", "tag2"]
toc: true
use_math: false
---

Content here...
```
3. Run `npm run build` (or automatically via Git push)

### Modifying Components
- Astro files use `.astro` extension
- Mix HTML, CSS, TypeScript in single file
- Props interface required for type safety
- Automatic code splitting & optimization

### Styling
- 타이포그래피·여백·색 토큰은 `/src/styles/editorial.css`에서 수정 (global.css는 베이스/레거시)
- Edit `/src/styles/global.css` for global styles
- Component-scoped styles use `<style>` tags
- CSS variables for theme consistency
- Media queries for responsive design

### Adding Diagrams
- Create new SVG component in `/src/components/diagrams/`
- Use CSS variables for theming:
  - `--an-inner`, `--an-border`, `--an-active`, etc.
  - Add `:global(body:not([data-theme="dark"]))` override
- Import in post with: `<Diagram />`

---

## Git & Deployment

### Key Git History
- **Latest**: Safari theme transition fix (repaint optimization)
- **Major Event**: Jekyll → Astro migration (commit: `8e8d230`)
- **Legacy**: Originally based on Klisé Jekyll theme (MIT licensed)

### Deployment Process
1. **Local Development**: `npm run dev` (live reload)
2. **Pre-commit**: Review changes, ensure builds pass locally
3. **Push to Master**: Triggers GitHub Actions workflow
4. **Auto-build**: 2-3 minutes, deployed to GitHub Pages
5. **Live**: Available at https://froggydisk.github.io

### Ignored Files
```
dist/                          # Build output
node_modules/                  # Dependencies
.astro/                        # Astro cache
_site/, .jekyll-*, .sass-*    # Jekyll legacy
.DS_Store                      # macOS files
._config.yml.swp               # Vim swap
```

---

## Content & Metadata

### Blog Statistics
- **Total Posts**: 52+
- **Date Range**: 2020 - 2025
- **Languages**: Korean (with occasional English)
- **Topics**: Frontend, DevOps, ML/DL, Bug Fixes, Tutorials
- **Average Length**: ~80 lines per post (range: 20-200 lines)

### Recent Post Categories
- Infrastructure/Server Setup (GPU, RTX 4090 configs)
- Kubernetes & DevOps (Harbor, Airflow, networking)
- Frontend (React, component patterns)
- AI/ML (LLM deployment, optimization)
- Bug Fixes & Troubleshooting (detailed solutions)

### Social/Integrations
- **GitHub**: Link in navbar (`https://github.com/froggydisk`)
- **Velog**: External link to Velog blog (`https://velog.io/@frog`)
- **AdSense**: Google AdSense ads (CA-PUB-4715878791193779)
- **Ko-fi**: Donation link (Support component)
- **Google Analytics**: 미설치 (개인정보처리방침 문구는 설치 예정 기준으로 작성돼 있음)

---

## Key Code Patterns & Conventions

### Astro File Structure
```astro
---
// TypeScript frontmatter (server-side only)
import Component from '../components/Component.astro';
const data = await getCollection('blog');
---

<!-- HTML template with client-side reactivity -->
<div>{data.map(item => ...)}</div>

<style>
  /* Scoped CSS */
  div { color: var(--color-primary); }
</style>

<script>
  // Client-side JavaScript
  document.addEventListener('click', () => {});
</script>
```

### Date Handling
- **Parsing**: Extract from filename prefix (YYYY-MM-DD)
- **Display**: `new Date(dateStr + 'T00:00:00')` for ISO conversion
- **Format**: `toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })`

### Slug Generation
```javascript
const slug = post.id.replace(/^\d{4}-\d{2}-\d{2}-/, '');
// Input: "2025-02-18-server-build.md"
// Output: "server-build"
```

### Tag Parsing
```javascript
const rawTags = post.data.tags || [];
const tags = rawTags
  .flatMap((t) => t.split(',').map((s) => s.trim()))
  .filter(Boolean);
```

### Theme Toggle
```javascript
const theme = localStorage.getItem('theme');
if (theme === 'dark' || !theme) {
  document.body.setAttribute('data-theme', 'dark');
} else {
  document.body.removeAttribute('data-theme');
}
```

---

## Performance & Optimization

### Built-in Optimizations
- **Static Generation**: Pre-built HTML (no server needed)
- **Partial Hydration**: Only interactive components loaded with JavaScript
- **Image Optimization**: Astro auto-optimizes images
- **Syntax Highlighting**: Done at build time (Shiki)
- **Search Index**: Pre-built pagefind index (no runtime overhead)

### Deployment Efficiency
- **Artifact Caching**: GitHub Actions npm cache layer
- **Single File Output**: `/dist` directory as deployment target
- **Zero Database**: All content in Git (version controlled)

---

## Troubleshooting & Common Tasks

### Build Issues
- **Node version mismatch**: Ensure Node 22+
- **Cache issues**: Delete `node_modules/`, `.astro/`, run `npm ci`
- **Search not working**: Rebuild pagefind with `npm run build`

### Development Issues
- **HMR not working**: Try killing dev server, restart with `npm run dev`
- **Theme not persisting**: Check localStorage in browser DevTools
- **Post not appearing**: Verify YAML frontmatter syntax, filename format

### Deployment Issues
- **Build failing in CI/CD**: Check GitHub Actions logs, verify git push
- **Old content cached**: GitHub Pages caches; wait 5-10 minutes or hard refresh (Ctrl+Shift+R)
- **Domain issues**: Verify CNAME file or GitHub Pages settings

---

## Contributing Guidelines

### Adding Content
1. Follow post naming convention: `YYYY-MM-DD-slug.md`
2. Include required frontmatter (title, at minimum)
3. Use semantic markdown (h2 for sections, proper lists)
4. Tag appropriately for discovery
5. Enable comments if discussion expected

### Code Changes
1. Test locally: `npm run dev`
2. Build for production: `npm run build`
3. Verify pagefind index works
4. Check git diff before committing
5. Push to master to trigger auto-deployment

### Component Best Practices
- Keep components focused (single responsibility)
- Use TypeScript interfaces for props
- Scope CSS within components where possible
- Test theme toggle with `data-theme` attribute
- Mobile-first responsive design

---

## License & Attribution

- **Site Content**: Copyright (c) 2020-2025 froggydisk
- **Theme Base**: Klisé (MIT License, by Mahendrata Harpi)
- **Framework**: Astro (Apache 2.0)
- **Icons**: Lucide, Phosphor (via Iconify)
- **Font**: Pretendard (SIL Open Font License)

All theme modifications and content are available under MIT License per `/LICENSE` file.

---

## Useful Resources

- **Astro Docs**: https://docs.astro.build
- **Pagefind**: https://pagefind.app
- **Shiki Themes**: https://shiki.tmix.dev/themes
- **Pretendard Font**: https://github.com/orioncactus/pretendard
- **Iconify**: https://iconify.design

---

## Development Server

```bash
# Install dependencies
npm install

# Start local dev server
npm run dev
# Accessible at: http://localhost:3000
# Includes: HMR, automatic rebuild

# Build for production
npm run build
# Output directory: ./dist

# Preview production build
npm run preview
```

---

**Last Updated**: August 22, 2026
**Framework**: Astro 7.2.2
**Node**: 22
