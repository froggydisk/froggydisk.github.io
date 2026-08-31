/**
 * 책 컬렉션의 경로 규칙을 한 곳에 모아둔다.
 *
 * 파일 경로:  <책>/<NN-부>/<NN-장>.md      예) llm-serving/01-basics/02-batching
 * URL 경로:   /books/<책>/<부>/<장>/        예) /books/llm-serving/basics/batching/
 *
 * 숫자 접두사는 순서를 정하는 데만 쓰고 URL에서는 떨어진다. 접두사를 URL에 남기면
 * 장을 한 번 재배치할 때마다 바깥으로 나간 링크가 전부 깨진다.
 */

import type { CollectionEntry } from 'astro:content';

export type BookEntry = CollectionEntry<'book'>;
export type BookMeta = CollectionEntry<'bookMeta'>;

const PREFIX = /^\d+[-_.]/;

/** 'llm-serving/01-basics/02-batching' → 'llm-serving' */
export function bookOf(id: string): string {
  return id.split('/')[0];
}

/** 'llm-serving/01-basics/02-batching' → 'basics/batching' */
export function chapterPath(id: string): string {
  return id
    .split('/')
    .slice(1)
    .map((seg) => seg.replace(PREFIX, ''))
    .join('/');
}

/** 장 하나의 사이트 절대 경로 */
export function chapterHref(id: string): string {
  return `/books/${bookOf(id)}/${chapterPath(id)}/`;
}

export function bookHref(bookSlug: string): string {
  return `/books/${bookSlug}/`;
}

/**
 * 'YYYY-MM-DD' 또는 'YYYY-MM-DDTHH:mm' 같은 느슨한 표기를 UTC 기준 Date로.
 * 타임존이 없으면 UTC로 읽어 로컬 빌드와 CI 빌드가 하루 어긋나는 것을 막는다.
 */
export function parseLooseDate(raw?: string): Date | null {
  if (!raw) return null;
  let v = raw.trim().replace(' ', 'T').replace(/T$/, '');
  if (/^\d{4}-\d{2}-\d{2}$/.test(v)) v += 'T00:00:00Z';
  else if (!/(Z|[+-]\d{2}:?\d{2})$/.test(v)) v += 'Z';
  const d = new Date(v);
  return Number.isNaN(d.getTime()) ? null : d;
}

/**
 * 장의 수정일. 장 → 책 → 책 발행일 순으로 폴백한다.
 * 파일 mtime은 쓰지 않는다. CI 체크아웃이 mtime을 전부 배포 시각으로 만들어버린다.
 */
export function chapterModified(entry: BookEntry, meta?: BookMeta): Date {
  return (
    parseLooseDate(entry.data.last_modified_at) ??
    parseLooseDate(meta?.data.last_modified_at) ??
    parseLooseDate(meta?.data.published) ??
    new Date(0)
  );
}

/** 책의 수정일. 가장 최근에 손댄 장을 따라간다. */
export function bookModified(chapters: BookEntry[], meta?: BookMeta): Date {
  const dates = chapters.map((c) => chapterModified(c, meta).getTime());
  const latest = dates.length ? Math.max(...dates) : 0;
  const base = parseLooseDate(meta?.data.last_modified_at) ?? parseLooseDate(meta?.data.published);
  return new Date(Math.max(latest, base ? base.getTime() : 0));
}

/**
 * 정렬 키. 접두사 숫자를 자연수로 비교해 10장이 2장 뒤에 오게 한다.
 * (문자열 정렬은 '10' < '2' 라서 0 패딩을 강제하게 되는데, 그 규칙을 사람이 지키게 하고 싶지 않다)
 */
function sortKey(id: string): string {
  return id
    .split('/')
    .map((seg) => {
      const m = seg.match(/^(\d+)/);
      return m ? m[1].padStart(6, '0') + seg.slice(m[1].length) : seg;
    })
    .join('/');
}

export function sortChapters(entries: BookEntry[]): BookEntry[] {
  return [...entries].sort((a, b) => sortKey(a.id).localeCompare(sortKey(b.id)));
}

export interface TocChapter {
  id: string;
  title: string;
  href: string;
  /** 책 전체에서 몇 번째 장인지 (1-base) */
  index: number;
}

export interface TocPart {
  /** 디렉터리 이름 (접두사 포함). 부가 없는 평면 구성이면 빈 문자열 */
  dir: string;
  title: string;
  /** book.yaml 의 parts[].icon. 없으면 아이콘 없이 나간다 */
  icon?: string;
  chapters: TocChapter[];
}

/**
 * 정렬된 장 목록을 부 단위로 묶는다. 부 제목은 book.yaml의 parts에서 찾고,
 * 없으면 디렉터리 이름에서 접두사와 하이픈을 걷어내 쓴다.
 */
export function buildToc(chapters: BookEntry[], meta?: BookMeta): TocPart[] {
  const declared = new Map((meta?.data.parts ?? []).map((p) => [p.dir, p]));
  const parts: TocPart[] = [];
  let index = 0;

  for (const entry of sortChapters(chapters)) {
    const segments = entry.id.split('/').slice(1);
    // 장 파일 자신을 뺀 나머지가 부 디렉터리다. 평면 구성이면 빈 문자열.
    const dir = segments.length > 1 ? segments[0] : '';

    let part = parts.at(-1);
    if (!part || part.dir !== dir) {
      const declaredPart = declared.get(dir);
      part = {
        dir,
        title: declaredPart?.title ?? dir.replace(PREFIX, '').replace(/[-_]/g, ' '),
        icon: declaredPart?.icon,
        chapters: [],
      };
      parts.push(part);
    }

    part.chapters.push({
      id: entry.id,
      title: entry.data.title,
      href: chapterHref(entry.id),
      index: ++index,
    });
  }

  return parts;
}

/** 목차 순서대로 앞/뒤 장을 찾는다 */
export function neighbors(toc: TocPart[], currentId: string) {
  const flat = toc.flatMap((p) => p.chapters);
  const at = flat.findIndex((c) => c.id === currentId);
  return {
    prev: at > 0 ? flat[at - 1] : null,
    next: at >= 0 && at < flat.length - 1 ? flat[at + 1] : null,
    current: at >= 0 ? flat[at] : null,
    total: flat.length,
  };
}
